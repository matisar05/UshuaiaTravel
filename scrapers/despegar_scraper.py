"""
Despegar scraper for Ushuaia hotels (Playwright-based)
"""
import logging
from datetime import datetime, timedelta
from .base import BaseScraper

logger = logging.getLogger(__name__)


class DespegarScraper(BaseScraper):
    """Scraper for Despegar.com.ar hotels in Ushuaia."""

    PLATFORM = "despegar"
    BASE_URL = "https://www.despegar.com.ar"
    SEARCH_URL = "https://www.despegar.com.ar/hoteles/hoteles-en-ushuaia"

    def get_platform_name(self):
        return self.PLATFORM

    def scrape(self, max_hotels=50):
        hotels = []
        logger.info(f"Starting Despegar scrape (target: {max_hotels})")

        if not self.safe_navigate(self.SEARCH_URL, timeout=40000):
            logger.error("Failed to load Despegar search page")
            return hotels

        self.page.wait_for_timeout(5000)

        try:
            self.page.wait_for_selector('[data-testid="cluster-card"]', timeout=20000)
        except Exception:
            try:
                self.page.wait_for_selector(".cluster-card", timeout=10000)
            except Exception:
                logger.warning("Could not find Despegar hotel cards, trying alternative selectors")
                self.page.wait_for_timeout(3000)

        self._scroll_for_lazy_load()
        cards = self._get_all_cards()

        logger.info(f"Found {len(cards)} Despegar cards")

        context = self.page.context

        for card in cards:
            try:
                data = self._extract_card_data(card)
                if not data or not data.get("name"):
                    continue

                url = data.get("platform_url")
                if url:
                    detail_page = context.new_page()
                    detail_page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    detail_page.wait_for_timeout(3000)

                    self.page = detail_page
                    details = self._extract_page_details()
                    data.update(details)
                    hotels.append(data)

                    detail_page.close()
                else:
                    hotels.append(data)
            except Exception as e:
                logger.warning(f"Error processing Despegar listing: {e}")

        return hotels

    def _get_all_cards(self):
        primary = self.page.query_selector_all('[data-testid="cluster-card"]')
        if primary:
            return primary
        fallback = self.page.query_selector_all(".cluster-card")
        if fallback:
            return fallback
        return self.page.query_selector_all('[class*="cluster"]')

    def _scroll_for_lazy_load(self):
        for _ in range(4):
            self.page.evaluate("window.scrollBy(0, 1200)")
            self.page.wait_for_timeout(1500)

    def _extract_card_data(self, card) -> dict | None:
        data: dict = {"platform": self.PLATFORM}

        name_el = card.query_selector('[data-testid="cluster-name"]') or \
                  card.query_selector(".cluster-name") or \
                  card.query_selector("h3")
        if not name_el:
            return None

        data["name"] = self.clean_text(name_el.inner_text())

        link_el = card.query_selector("a")
        if link_el:
            href = link_el.get_attribute("href") or ""
            if href:
                data["platform_url"] = href if href.startswith("http") else self.BASE_URL + href

        price_el = card.query_selector('[data-testid="cluster-price"]') or \
                   card.query_selector(".price-amount") or \
                   card.query_selector('[class*="price"]')
        if price_el:
            data["price_per_night"] = self.normalize_price(price_el.inner_text())

        stars_el = card.query_selector('[data-testid="cluster-stars"]') or \
                   card.query_selector('[class*="star"]')
        if stars_el:
            import re
            text = stars_el.inner_text() or stars_el.get_attribute("aria-label") or ""
            m = re.search(r"(\d+)", text)
            if m:
                data["stars"] = int(m.group(1))

        img_el = card.query_selector("img")
        if img_el:
            src = img_el.get_attribute("src") or ""
            if src and not src.startswith("data:"):
                data["main_image"] = src
                data["images"] = [src]

        return data if data.get("name") else None

    def _extract_page_details(self) -> dict:
        details: dict = {}
        self.page.wait_for_timeout(2000)

        addr_el = self.page.query_selector('[data-testid="hotel-address"]') or \
                  self.page.query_selector(".address-container") or \
                  self.page.query_selector('[class*="address"]')
        if addr_el:
            details["address"] = self.clean_text(addr_el.inner_text())

        amenity_els = self.page.query_selector_all('[data-testid="amenity-item"]') or \
                      self.page.query_selector_all('[class*="amenity"]')
        if amenity_els:
            details["amenities"] = [
                self.clean_text(el.inner_text())
                for el in amenity_els
                if el.inner_text().strip()
            ]

        img_els = self.page.query_selector_all('[data-testid="gallery-image"] img') or \
                  self.page.query_selector_all(".gallery img, .photo-gallery img")
        images = []
        for img in img_els[:8]:
            src = img.get_attribute("src") or img.get_attribute("data-src") or ""
            if src and not src.startswith("data:") and "http" in src:
                images.append(src)
        if images:
            details["images"] = images
            details["main_image"] = images[0]

        room_el = self.page.query_selector('[data-testid="room-type"]') or \
                  self.page.query_selector(".room-type h4, .room-name")
        if room_el:
            details["room_type"] = self.clean_text(room_el.inner_text())

        import re
        guest_el = self.page.query_selector('[data-testid="occupancy"]') or \
                   self.page.query_selector('[class*="occupancy"], [class*="guest"]')
        if guest_el:
            m = re.search(r"(\d+)\s*(?:huésped|persona|adulto)", guest_el.inner_text(), re.IGNORECASE)
            if m:
                details["max_guests"] = int(m.group(1))

        return details
