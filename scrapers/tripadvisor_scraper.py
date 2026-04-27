"""
TripAdvisor scraper for Ushuaia hotels
"""
import time
import logging
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base import BaseScraper

logger = logging.getLogger(__name__)


class TripAdvisorScraper(BaseScraper):
    """Scraper for TripAdvisor hotels in Ushuaia"""
    
    PLATFORM = 'tripadvisor'
    BASE_URL = 'https://www.tripadvisor.com'
    SEARCH_URL = 'https://www.tripadvisor.com/Hotels-g312848-Ushuaia_Province_of_Tierra_del_Fuego_Patagonia-Hotels.html'
    
    def __init__(self):
        super().__init__()
        self.max_retries = 3
    
    def search_hotels(self, location: str = "Ushuaia", **kwargs) -> List[Dict]:
        """
        Search for hotels in Ushuaia on TripAdvisor
        
        Args:
            location: Location to search (default: Ushuaia)
            **kwargs: Additional search parameters
        
        Returns:
            List of hotel data dictionaries
        """
        logger.info(f"Starting TripAdvisor search for {location}")
        
        try:
            driver = self.get_driver()
            driver.get(self.SEARCH_URL)
            
            # Wait for listings to load
            self._wait_for_listings(driver)
            
            # Handle cookie consent
            self._handle_cookie_consent(driver)
            
            # Extract all listings
            hotels = []
            page = 1
            max_pages = kwargs.get('max_pages', 3)
            
            while page <= max_pages:
                logger.info(f"Scraping page {page}")
                
                # Extract listings from current page
                page_hotels = self._extract_listings(driver)
                hotels.extend(page_hotels)
                
                # Try to go to next page
                if page < max_pages and not self._go_to_next_page(driver):
                    break
                
                page += 1
                time.sleep(self.get_random_delay())
            
            logger.info(f"Found {len(hotels)} TripAdvisor listings")
            return hotels
            
        except Exception as e:
            logger.error(f"Error searching TripAdvisor: {str(e)}")
            return []
        finally:
            self.close()
    
    def _wait_for_listings(self, driver, timeout: int = 15):
        """Wait for hotel listings to appear"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-automation="hotel-card"]'))
            )
            time.sleep(2)
        except TimeoutException:
            logger.warning("Timeout waiting for TripAdvisor listings")
    
    def _handle_cookie_consent(self, driver):
        """Handle cookie consent popup"""
        try:
            accept_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
            accept_button.click()
            time.sleep(1)
        except NoSuchElementException:
            pass
    
    def _extract_listings(self, driver) -> List[Dict]:
        """Extract hotel data from current page"""
        listings = []
        
        try:
            # Try multiple selectors for hotel cards
            cards = driver.find_elements(By.CSS_SELECTOR, '[data-automation="hotel-card"]')
            
            if not cards:
                cards = driver.find_elements(By.CSS_SELECTOR, '.listing_title')
            
            logger.info(f"Found {len(cards)} hotel cards")
            
            for card in cards:
                try:
                    listing_data = self._parse_hotel_card(card)
                    if listing_data:
                        listings.append(listing_data)
                except Exception as e:
                    logger.warning(f"Error parsing hotel card: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error extracting listings: {str(e)}")
        
        return listings
    
    def _parse_hotel_card(self, card) -> Optional[Dict]:
        """Parse individual hotel card"""
        try:
            # Extract name
            name = None
            try:
                name_elem = card.find_element(By.CSS_SELECTOR, 'a[href*="Hotel_Review"]')
                name = name_elem.text.strip()
                url = name_elem.get_attribute('href')
                if not url.startswith('http'):
                    url = self.BASE_URL + url
            except:
                return None
            
            if not name:
                return None
            
            # Extract rating
            rating = None
            try:
                rating_elem = card.find_element(By.CSS_SELECTOR, '[aria-label*="bubbles"]')
                rating_text = rating_elem.get_attribute('aria-label')
                import re
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            except:
                pass
            
            # Extract review count
            review_count = None
            try:
                review_elem = card.find_element(By.CSS_SELECTOR, '[data-automation="reviewCount"]')
                review_text = review_elem.text
                import re
                review_match = re.search(r'([\d,]+)', review_text)
                if review_match:
                    review_count = int(review_match.group(1).replace(',', ''))
            except:
                pass
            
            # Extract price
            price_per_night = None
            try:
                price_elem = card.find_element(By.CSS_SELECTOR, '[data-automation="price"]')
                price_text = price_elem.text
                price_per_night = self._parse_price(price_text)
            except:
                pass
            
            # Extract image
            image_url = None
            try:
                img_elem = card.find_element(By.CSS_SELECTOR, 'img')
                image_url = img_elem.get_attribute('src')
            except:
                pass
            
            return {
                'name': name,
                'platform': self.PLATFORM,
                'platform_url': url,
                'price_per_night': price_per_night,
                'rating': rating,
                'review_count': review_count,
                'image_url': image_url,
            }
        
        except Exception as e:
            logger.warning(f"Failed to parse hotel card: {str(e)}")
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text"""
        if not price_text:
            return None
        
        try:
            import re
            # Match numbers with optional currency symbol
            price_match = re.search(r'[\$]?\s*(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?)', price_text)
            if price_match:
                price_str = price_match.group(1)
                price_str = price_str.replace(',', '').replace('.', '')
                if len(price_str) > 2:
                    price_str = price_str[:-2] + '.' + price_str[-2:]
                return float(price_str)
        except Exception as e:
            logger.warning(f"Failed to parse price '{price_text}': {str(e)}")
        
        return None
    
    def _go_to_next_page(self, driver) -> bool:
        """Navigate to next page"""
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next page"]')
            next_button.click()
            time.sleep(self.get_random_delay(3, 6))
            self._wait_for_listings(driver)
            return True
        except:
            return False
    
    def get_hotel_details(self, url: str) -> Optional[Dict]:
        """Get detailed information for a specific hotel"""
        logger.info(f"Getting TripAdvisor hotel details: {url}")
        
        try:
            driver = self.get_driver()
            driver.get(url)
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
            )
            time.sleep(3)
            
            details = {
                'platform': self.PLATFORM,
                'platform_url': url,
            }
            
            # Name
            try:
                name_elem = driver.find_element(By.CSS_SELECTOR, 'h1')
                details['name'] = name_elem.text.strip()
            except:
                pass
            
            # Address
            try:
                address_elem = driver.find_element(By.CSS_SELECTOR, '[data-automation="hotel-address"]')
                details['address'] = address_elem.text.strip()
            except:
                pass
            
            # Amenities
            try:
                amenity_elems = driver.find_elements(By.CSS_SELECTOR, '[data-automation="amenity"]')
                details['amenities'] = [elem.text.strip() for elem in amenity_elems if elem.text.strip()]
            except:
                details['amenities'] = []
            
            return details
        
        except Exception as e:
            logger.error(f"Error getting hotel details: {str(e)}")
            return None
        finally:
            self.close()
