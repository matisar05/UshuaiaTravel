"""
Airbnb scraper for Ushuaia hotels (Playwright-based)
"""
import logging
from .base import BaseScraper

logger = logging.getLogger(__name__)


class AirbnbScraper(BaseScraper):
    """Scraper for Airbnb listings in Ushuaia using Playwright."""
    
    BASE_URL = "https://www.airbnb.com"
    SEARCH_URL = "https://www.airbnb.com/s/Ushuaia--Tierra-del-Fuego--Argentina/homes"

    def get_platform_name(self):
        return 'airbnb'

    def scrape(self, max_hotels=50):
        """
        Scrape Ushuaia hotels from Airbnb.
        """
        hotels = []
        logger.info(f"Starting Airbnb scrape (Target: {max_hotels})")
        
        # Build search URL with dates similar to Booking
        from datetime import datetime, timedelta
        today = datetime.now()
        checkin_date = today + timedelta(days=7)
        checkout_date = checkin_date + timedelta(days=1)
        
        # Airbnb format: &checkin=2024-01-01&checkout=2024-01-02
        date_params = f"&checkin={checkin_date.strftime('%Y-%m-%d')}&checkout={checkout_date.strftime('%Y-%m-%d')}"
        url = f"{self.SEARCH_URL}?items_offset=0{date_params}"
        
        if not self.safe_navigate(url):
             logger.error("Failed to load Airbnb search page")
             return hotels

        try:
            # Wait for grid or list
            self.page.wait_for_selector('[data-testid="card-container"]', timeout=20000)
            
            # Scroll to load more (lazy loading)
            self._scroll_slowly()
            
            # Close translation or cookie modals if they appear
            try:
                self.page.click('button[aria-label="Close"]', timeout=2000)
            except:
                pass

        except Exception as e:
            logger.warning(f"Could not find listings: {e}")
            return hotels

        # Extract listings
        cards = self.page.query_selector_all('[data-testid="card-container"]')
        logger.info(f"Found {len(cards)} cards on initial load")
        
        for card in cards[:max_hotels]:
            try:
                data = self._extract_card_data(card)
                if data:
                    hotels.append(data)
            except Exception as e:
                logger.error(f"Error parsing Airbnb card: {e}")

        return hotels

    def _extract_card_data(self, card):
        """Extract data from a single Airbnb card."""
        data = {
            'platform': self.get_platform_name(),
            'amenities': [] # Airbnb cards don't show many amenities usually
        }
        
        # Name (often "Apartment in Ushuaia" or specific name)
        # Airbnb often puts the name in an aria-label or specific ID
        try:
            # Try getting aria-label of the link
            link = card.query_selector('a[href^="/rooms/"]')
            if link:
                href = link.get_attribute('href')
                if href:
                    data['platform_url'] = self.BASE_URL + href.split('?')[0]
                
                # Title might be in aria-label
                aria_label = link.get_attribute('aria-label')
                if aria_label:
                    # Aria label format "Listing name by Host, Rating X, Price Y"
                    data['name'] = aria_label.split(',')[0]
                else:
                    # Fallback to visual texts
                    # Usually the first div with text is location, second is name/distance
                    # This is brittle on Airbnb due to dynamic classes
                    pass
        except:
            pass
            
        # Price
        # Look for the price element
        try:
            price_elem = card.query_selector('span._1y74zjx') or \
                         card.query_selector('[data-testid="price-availability-row"]') or \
                         card.query_selector('span._tyxjp1')
            
            if price_elem:
                data['price_per_night'] = self.normalize_price(price_elem.inner_text())
        except:
            pass

        # Rating
        try:
            rating_elem = card.query_selector('span[aria-hidden="true"]')
            # Look for "4.92" pattern
            if rating_elem:
                text = rating_elem.inner_text()
                if '.' in text and len(text) <= 4:
                    try:
                        data['stars'] = float(text)
                    except:
                        pass
        except:
            pass
            
        # Image
        try:
            img = card.query_selector('img')
            if img:
                src = img.get_attribute('src')
                if src:
                    data['main_image'] = src
                    data['images'] = [src]
        except:
             pass

        if not data.get('name'):
            # Fallback name extraction
            try:
                # Airbnb structures are complex. Simplest is to assume the location or bold text is the name
                # But typically 'name' is just "Flat in Ushuaia".
                desc_line = card.query_selector('[data-testid="listing-card-title"]')
                if desc_line:
                    data['name'] = desc_line.inner_text()
            except:
                pass
        
        # Default name if missing
        if not data.get('name'):
            data['name'] = "Alojamiento en Airbnb"

        # Validate existence of price
        if data.get('price_per_night'):
            return data
            
        return None

    def _scroll_slowly(self):
        """Scroll down to trigger lazy loading."""
        for _ in range(5):
            self.page.evaluate("window.scrollBy(0, 1000)")
            self.page.wait_for_timeout(500)
