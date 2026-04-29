"""
Base scraper class with common functionality for all scrapers.
"""
import time
import random
import logging
import threading
from collections import defaultdict
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import stealth_sync
from django.conf import settings

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

MAX_RETRIES = 3
BACKOFF_BASE = 1.5
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_COOLDOWN = 600  # 10 minutes

_circuit_state: dict[str, dict] = defaultdict(lambda: {"failures": 0, "open_until": 0})
_circuit_lock = threading.Lock()


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def is_circuit_open(platform: str) -> bool:
    with _circuit_lock:
        state = _circuit_state[platform]
        if state["failures"] >= CIRCUIT_BREAKER_THRESHOLD:
            if time.time() < state["open_until"]:
                logger.warning(f"Circuit OPEN for {platform}")
                return True
            state["failures"] = 0
            state["open_until"] = 0
            logger.info(f"Circuit RESET for {platform}")
    return False


def record_circuit_failure(platform: str) -> None:
    with _circuit_lock:
        state = _circuit_state[platform]
        state["failures"] += 1
        if state["failures"] >= CIRCUIT_BREAKER_THRESHOLD:
            state["open_until"] = time.time() + CIRCUIT_BREAKER_COOLDOWN
            logger.error(f"Circuit TRIPPED for {platform} ({state['failures']} failures)")


def record_circuit_success(platform: str) -> None:
    with _circuit_lock:
        _circuit_state[platform]["failures"] = 0


class BaseScraper(ABC):
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.user_agent = get_random_user_agent()
        self.delay_ms = getattr(settings, "SCRAPER_DELAY_MS", 2000)
        self.proxy = getattr(settings, "SCRAPER_PROXY", None)
        self.playwright = None
        self.browser = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()

        launch_kwargs = {"headless": self.headless}
        if self.proxy:
            launch_kwargs["proxy"] = self.proxy

        self.browser = self.playwright.chromium.launch(**launch_kwargs)

        context = self.browser.new_context(
            user_agent=self.user_agent,
            viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
        )
        self.page = context.new_page()

        stealth_sync(self.page)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def wait_random(self, min_ms: int | None = None, max_ms: int | None = None):
        delay = random.randint(min_ms or self.delay_ms, max_ms or self.delay_ms * 2) / 1000.0
        time.sleep(delay)

    def _retry_with_backoff(self, func, max_retries: int = MAX_RETRIES, *args, **kwargs):
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = BACKOFF_BASE ** attempt + random.uniform(0, 1)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {wait_time:.1f}s"
                    )
                    time.sleep(wait_time)
        raise last_error

    def safe_navigate(self, url: str, timeout: int = 30000) -> bool:
        platform = self.get_platform_name()
        if is_circuit_open(platform):
            logger.warning(f"Skipping navigate: circuit open for {platform}")
            return False

        try:
            logger.info(f"Navigating to: {url} [UA: {self.user_agent[:30]}...]")
            self.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            self.wait_random()
            record_circuit_success(platform)
            return True
        except PlaywrightTimeout:
            logger.error(f"Timeout navigating to {url}")
            record_circuit_failure(platform)
            return False
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            record_circuit_failure(platform)
            return False

    def safe_click(self, selector: str, timeout: int = 5000) -> bool:
        try:
            self.page.click(selector, timeout=timeout)
            self.wait_random()
            return True
        except Exception as e:
            logger.warning(f"Could not click {selector}: {str(e)}")
            return False

    def safe_text(self, selector: str, default: str = "") -> str:
        try:
            element = self.page.query_selector(selector)
            return element.inner_text().strip() if element else default
        except Exception as e:
            logger.warning(f"Could not extract text from {selector}: {str(e)}")
            return default

    def safe_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        try:
            element = self.page.query_selector(selector)
            return element.get_attribute(attribute) if element else default
        except Exception as e:
            logger.warning(f"Could not extract {attribute} from {selector}: {str(e)}")
            return default

    def simulate_human_behavior(self):
        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(100, 600)
            self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.3, 1.5))

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        pass

    def normalize_price(self, price_text: str) -> float | None:
        import re
        if not price_text:
            return None

        clean = re.sub(r"[^\d,.]", "", price_text)

        if "." in clean and "," in clean:
            clean = clean.replace(".", "").replace(",", ".")
        elif "." in clean and "," not in clean:
            clean = clean.replace(".", "")
        elif "," in clean:
            clean = clean.replace(",", ".")

        try:
            return float(clean)
        except ValueError:
            logger.warning(f"Could not parse price: {price_text}")
            return None

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        return " ".join(text.split()).strip()
