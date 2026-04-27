"""
Booking.com scraper for Ushuaia hotels.
"""
import logging
from .base import BaseScraper

logger = logging.getLogger(__name__)


class BookingScraper(BaseScraper):
    """Scraper for Booking.com Ushuaia hotels."""
    
    BASE_URL = "https://www.booking.com/searchresults.html"
    
    def get_platform_name(self):
        return 'booking'
    
    def build_search_url(self, checkin='', checkout='', adults=2):
        """Build search URL for Ushuaia."""
        params = {
            'ss': 'Ushuaia',
            'checkin': checkin or '',
            'checkout': checkout or '',
            'group_adults': adults,
            'group_children': 0,
            'no_rooms': 1,
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.BASE_URL}?{query_string}"
    
        if data.get('name') and data.get('price_per_night'):
            # Visit detail page for more info
            if data.get('platform_url') and not 'http' in data['platform_url']:
                 data['platform_url'] = 'https://www.booking.com' + data['platform_url']

            if data.get('platform_url'):
                try:
                    details = self._scrape_detail_page(data['platform_url'])
                    if details:
                        data.update(details)
                except Exception as e:
                    logger.warning(f"Failed to scrape details for {data.get('name')}: {str(e)}")
            
            return data
        
        return None

    def _scrape_detail_page(self, url):
        """Scrape detailed information from hotel page."""
        details = {}
        
        # Open new page/tab or navigate current? 
        # Better to use a new page context if possible, or navigate back.
        # For simplicity in this structure, we'll safe_navigate, extract, and return.
        # NOTE: This changes the current page state! The caller loop needs to handle this.
        # Actually, since we are iterating a list of cards, the cards become stale if we navigate away.
        # Strategy: Extract URLs first, THEN iterate URLs to scrape details.
        
        # Wait, the current architecture iterates cards on the search page.
        # If we navigate away, we lose the search page context.
        # Modification: We should grab basic info + URL from search page, then visit URLs one by one.
        pass # Placeholder, logic moved to scrape() method for correct flow

    def scrape(self, max_hotels=50):
        """
        Scrape Ushuaia hotels from Booking.com.
        
        Returns list of hotel dictionaries.
        """
        hotels = []
        
        # Calculate future dates to ensure prices are shown
        from datetime import datetime, timedelta
        today = datetime.now()
        checkin_date = today + timedelta(days=7)
        checkout_date = checkin_date + timedelta(days=1)
        
        # Format dates as YYYY-MM-DD
        checkin_str = checkin_date.strftime('%Y-%m-%d')
        checkout_str = checkout_date.strftime('%Y-%m-%d')
        
        logger.info(f"Scraping for dates: {checkin_str} to {checkout_str}")
        url = self.build_search_url(checkin=checkin_str, checkout=checkout_str)
        
        if not self.safe_navigate(url):
            logger.error("Failed to load Booking.com search page")
            return hotels
            
        # Wait for results
        try:
            self.page.wait_for_selector('[data-testid="property-card"]', timeout=20000)
        except Exception:
            logger.warning("Property cards not found")
            return hotels
        
        # First extraction pass: Basic Info + URLs
        basic_listings = []
        hotel_cards = self.page.query_selector_all('[data-testid="property-card"]')
        
        for card in hotel_cards[:max_hotels]:
            try:
                data = self._extract_basic_data(card)
                if data:
                    basic_listings.append(data)
            except Exception as e:
                logger.error(f"Error extracting basic card: {e}")
        
        logger.info(f"Found {len(basic_listings)} hotels. Starting detailed scraping...")
        
        # Second pass: Visit each URL for details
        for listing in basic_listings:
            try:
                if listing.get('platform_url'):
                    full_url = listing['platform_url']
                    if not full_url.startswith('http'):
                        full_url = 'https://www.booking.com' + full_url
                    
                    logger.info(f"Scraping details for: {listing.get('name')}")
                    
                    if self.safe_navigate(full_url):
                        details = self._extract_page_details()
                        listing.update(details)
                        hotels.append(listing)
                    else:
                        logger.warning(f"Could not navigate to {full_url}")
            except Exception as e:
                logger.error(f"Error processing {listing.get('name')}: {e}")
                
        return hotels

    def _extract_basic_data(self, card):
        """Extract data from search result card."""
        data = {'platform': self.get_platform_name()}
        
        # Name
        name_elem = card.query_selector('[data-testid="title"]')
        if not name_elem:
             name_elem = card.query_selector('h3') # Fallback
        
        if name_elem:
            data['name'] = self.clean_text(name_elem.inner_text())
            
        # Price
        price_elem = card.query_selector('[data-testid="price-and-discounted-price"]')
        if not price_elem:
            price_elem = card.query_selector('.prco-valign-middle-helper')
        # Price
        price_elem = card.query_selector('[data-testid="price-and-discounted-price"]')
        if not price_elem:
            price_elem = card.query_selector('.prco-valign-middle-helper')
        
        if price_elem:
            data['price_per_night'] = self.normalize_price(price_elem.inner_text())
        else:
             # Try generic match for price format with loose regex
             text = card.inner_text()
             # Look for ARS or $ followed by numbers, handling spaces/dots/commas
             # Matches: ARS 1.234, $ 1.234, ARS1234
             import re
             price_match = re.search(r'(?:ARS|\$)\s*([\d,.]+)', text)
             if price_match:
                 data['price_per_night'] = self.normalize_price(price_match.group(0))

        # URL
        link_elem = card.query_selector('a[data-testid="title-link"]')
        if not link_elem:
            link_elem = card.query_selector('a')
            
        if link_elem:
            href = link_elem.get_attribute('href')
            if href:
                data['platform_url'] = href.split('?')[0]
                

                
        # Address (Basic)
        address_elem = card.query_selector('[data-testid="address"]')
        if address_elem:
            data['address'] = self.clean_text(address_elem.inner_text())
            
        # Stars
        rating_elem = card.query_selector('[data-testid="rating-stars"]')
        if rating_elem:
            stars_html = rating_elem.get_attribute('aria-label') or ''
            import re
            stars_match = re.search(r'(\d+)', stars_html)
            if stars_match:
                data['stars'] = int(stars_match.group(1))
                
        if data.get('name') and data.get('price_per_night'):
            return data
        return None

    def _extract_page_details(self):
        """Extract details from the currently open hotel page."""
        details = {}
        
        # Hotel Type
        try:
            type_elem = self.page.query_selector('[data-testid="property-type-badge"]')
            if type_elem:
                type_text = self.clean_text(type_elem.inner_text()).lower()
                # Map to our internal types
                if 'hostal' in type_text or 'hostel' in type_text:
                    details['hotel_type'] = 'hostel'
                elif 'apart' in type_text or 'departamento' in type_text:
                    details['hotel_type'] = 'apart'
                elif 'cabaña' in type_text:
                    details['hotel_type'] = 'cabaña'
                elif 'casa' in type_text:
                    details['hotel_type'] = 'casa'
                else:
                    details['hotel_type'] = 'hotel' # Default
        except:
            pass

        # Images
        try:
            images = []
            # Updated selector for Booking's new gallery
            # Prioritize huge images in the grid
            img_elems = self.page.query_selector_all('[data-testid="image-gallery-image"] img') or \
                        self.page.query_selector_all('.bh-photo-grid-item img') or \
                        self.page.query_selector_all('#hotel_main_content img')
            
            for img in img_elems[:8]: # Top 8 images
                src = img.get_attribute('src') or img.get_attribute('data-src')
                if src and 'http' in src:
                    # Filter out small icons or transparent placeholders if possible
                    if 'icon' not in src and 'spinner' not in src:
                        images.append(src)
            
            details['images'] = images
            if images:
                details['main_image'] = images[0]
        except:
            pass
            
        # Amenities
        try:
            amenities = []
            # Looking for popular facilities
            amenity_elems = self.page.query_selector_all('.important_facility') or \
                            self.page.query_selector_all('[data-testid="important-facility"]')
            
            for am in amenity_elems:
                text = self.clean_text(am.inner_text())
                if text:
                    amenities.append(text)
            
            details['amenities'] = amenities
        except:
            pass
            
        # Address (Better source)
        try:
            addr_elem = self.page.query_selector('.hp_address_subtitle') or \
                        self.page.query_selector('[data-node_tt_id="location_score_tooltip"]')
            if addr_elem:
                details['address'] = self.clean_text(addr_elem.inner_text())
        except:
            pass

        return details
