"""
TripAdvisor scraper for Ushuaia hotels (Playwright-based)
"""
import logging
import re
from .base import BaseScraper

logger = logging.getLogger(__name__)


class TripAdvisorScraper(BaseScraper):
    """Scraper for TripAdvisor hotels in Ushuaia using Playwright."""

    PLATFORM = "tripadvisor"
    BASE_URL = "https://www.tripadvisor.com"
    SEARCH_URL = (
        "https://www.tripadvisor.com/Hotels-g312848-"
        "Ushuaia_Province_of_Tierra_del_Fuego_Patagonia-Hotels.html"
    )

    def get_platform_name(self):
        return self.PLATFORM

    def scrape(self, max_hotels=50):
        hotels = []
        logger.info(f"Starting TripAdvisor scrape (target: {max_hotels})")

        if not self.safe_navigate(self.SEARCH_URL, timeout=40000):
            logger.error("Failed to load TripAdvisor search page")
            return hotels

        try:
            self.page.wait_for_selector('[data-automation="hotel-card"]', timeout=25000)
            self.page.wait_for_timeout(2000)
        except Exception:
            logger.warning("Could not find TripAdvisor hotel cards")
            return hotels

        all_cards = []
        for _ in range(3):
            cards = self.page.query_selector_all('[data-automation="hotel-card"]')
            for card in cards[len(all_cards):max_hotels]:
                all_cards.append(card)
            if len(all_cards) >= max_hotels:
                break
            if not self._go_to_next_page():
                break

        logger.info(f"Found {len(all_cards)} TripAdvisor cards total")

        context = self.page.context

        for card in all_cards:
            try:
                data = self._extract_card_data(card)
                if not data or not data.get("name"):
                    continue

                url = data.get("platform_url")
                if url:
                    detail_page = context.new_page()
                    detail_page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    detail_page.wait_for_timeout(2000)

                    self.page = detail_page
                    details = self._extract_page_details()
                    data.update(details)
                    hotels.append(data)

                    detail_page.close()
                else:
                    hotels.append(data)
            except Exception as e:
                logger.warning(f"Error processing TripAdvisor listing: {e}")

        return hotels

    def _extract_card_data(self, card) -> dict | None:
        data: dict = {"platform": self.PLATFORM}

        name_el = card.query_selector('a[href*="Hotel_Review"]')
        if not name_el:
            return None

        name = (name_el.get_attribute("aria-label") or name_el.inner_text()).strip()
        if not name:
            return None
        data["name"] = name

        href = name_el.get_attribute("href") or ""
        data["platform_url"] = self.BASE_URL + href if not href.startswith("http") else href

        price_el = card.query_selector('[data-automation="price"]') or card.query_selector(".price")
        if price_el:
            data["price_per_night"] = self.normalize_price(price_el.inner_text())

        rating_el = card.query_selector('[aria-label*="bubbles"]')
        if rating_el:
            aria = rating_el.get_attribute("aria-label") or ""
            m = re.search(r"(\d+\.?\d*)", aria)
            if m:
                data["stars"] = float(m.group(1))

        count_el = card.query_selector('[data-automation="reviewCount"]')
        if count_el:
            text = count_el.inner_text()
            m = re.search(r"([\d,]+)", text)
            if m:
                data["review_count"] = int(m.group(1).replace(",", ""))

        img_el = card.query_selector("img")
        if img_el:
            src = img_el.get_attribute("src") or ""
            if src and not src.startswith("data:"):
                data["main_image"] = src
                data["images"] = [src]

        return data if data.get("name") else None

    def _extract_page_details(self) -> dict:
        details: dict = {}

        addr_el = self.page.query_selector('[data-automation="hotel-address"]')
        if addr_el:
            details["address"] = self.clean_text(addr_el.inner_text())

        amenity_els = self.page.query_selector_all('[data-automation="amenity"]')
        if amenity_els:
            details["amenities"] = [
                self.clean_text(el.inner_text())
                for el in amenity_els
                if el.inner_text().strip()
            ]

        img_els = self.page.query_selector_all('img[data-testid="photo-viewer-image"]')
        if not img_els:
            img_els = self.page.query_selector_all(".hero-image img, .large_photo_wrapper img")
        images = []
        for img in img_els[:8]:
            src = img.get_attribute("src") or ""
            if src and not src.startswith("data:") and "http" in src:
                images.append(src)
        if images:
            details["images"] = images
            details["main_image"] = images[0]

        room_el = self.page.query_selector('[data-automation="room-type"]') or \
                  self.page.query_selector(".room-info h3")
        if room_el:
            details["room_type"] = self.clean_text(room_el.inner_text())

        return details

    def _go_to_next_page(self) -> bool:
        try:
            next_btn = self.page.query_selector('a[aria-label="Next page"]')
            if not next_btn:
                next_btn = self.page.query_selector(".nav.next")
            if next_btn:
                next_btn.click()
                self.page.wait_for_timeout(4000)
                self.page.wait_for_selector('[data-automation="hotel-card"]', timeout=15000)
                return True
        except Exception:
            pass
        return False
