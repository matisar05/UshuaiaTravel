"""
Base scraper class with common functionality for all scrapers.
"""
import time
import logging
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import stealth_sync
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers with stealth capabilities."""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.user_agent = getattr(settings, 'SCRAPER_USER_AGENT', 
                                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.delay_ms = getattr(settings, 'SCRAPER_DELAY_MS', 2000)
        self.proxy = getattr(settings, 'SCRAPER_PROXY', None) # Expected format: {"server": "...", "username": "...", "password": "..."}
        self.playwright = None
        self.browser = None
        self.page = None
    
    def __enter__(self):
        """Context manager entry with stealth mode."""
        self.playwright = sync_playwright().start()
        
        launch_kwargs = {'headless': self.headless}
        if self.proxy:
            launch_kwargs['proxy'] = self.proxy
            
        self.browser = self.playwright.chromium.launch(**launch_kwargs)
        
        context = self.browser.new_context(user_agent=self.user_agent)
        self.page = context.new_page()
        
        # Apply stealth patterns
        stealth_sync(self.page)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def wait_polite(self):
        """Wait between requests to be polite."""
        time.sleep(self.delay_ms / 1000.0)
    
    def safe_navigate(self, url, timeout=30000):
        """Safely navigate to URL with error handling."""
        try:
            logger.info(f"Navigating to: {url}")
            self.page.goto(url, timeout=timeout, wait_until='domcontentloaded')
            self.wait_polite()
            return True
        except PlaywrightTimeout:
            logger.error(f"Timeout navigating to {url}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def safe_click(self, selector, timeout=5000):
        """Safely click element with error handling."""
        try:
            self.page.click(selector, timeout=timeout)
            self.wait_polite()
            return True
        except Exception as e:
            logger.warning(f"Could not click {selector}: {str(e)}")
            return False
    
    def safe_text(self, selector, default=''):
        """Safely extract text from element."""
        try:
            element = self.page.query_selector(selector)
            return element.inner_text().strip() if element else default
        except Exception as e:
            logger.warning(f"Could not extract text from {selector}: {str(e)}")
            return default
    
    def safe_attribute(self, selector, attribute, default=''):
        """Safely extract attribute from element."""
        try:
            element = self.page.query_selector(selector)
            return element.get_attribute(attribute) if element else default
        except Exception as e:
            logger.warning(f"Could not extract {attribute} from {selector}: {str(e)}")
            return default
    
    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_platform_name(self):
        """Return platform name for database storage."""
        pass
    
    def normalize_price(self, price_text):
        """Extract numeric price from text."""
        import re
        if not price_text:
            return None
            
        # Log original text for debugging
        # logger.debug(f"Parsing price: {price_text}")
        
        # Strategy for ARS/Latam (e.g. "ARS 1.234.567,00" or "581.220")
        # 1. Remove currency symbols and whitespace
        # 2. If text contains both ',' and '.', assume '.' is thousands and ',' is decimal
        # 3. If text contains only '.', it's ambiguous. In ARS context usually thousands.
        
        clean = re.sub(r'[^\d,.]', '', price_text)
        
        # Case: 1.234,56 -> Remove dot, replace comma
        if '.' in clean and ',' in clean:
            clean = clean.replace('.', '').replace(',', '.')
        
        # Case: 1.234 -> Remove dot (Assuming thousands in simple integers)
        # Risk: USD 1.50 -> 150. But context is likely ARS high values.
        # Case: 1.234 -> Remove dot (Assuming thousands in simple integers > 3 digits)
        elif '.' in clean and ',' not in clean:
             # Heuristic: if last group is 3 digits, it's likely thousands (e.g. 581.220)
             # vs 10.50 (decimal). ARS prices usually high.
             # Safest for Argentina: Remove ALL dots.
             clean = clean.replace('.', '')
        
        # Case: 1234,56 -> Replace comma with dot
        elif ',' in clean:
            clean = clean.replace(',', '.')
            
        try:
            return float(clean)
        except ValueError:
            logger.warning(f"Could not parse price: {price_text}")
            return None
    
    def clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return ""
        # Remove extra whitespace and newlines
        return " ".join(text.split()).strip()
