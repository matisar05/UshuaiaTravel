"""
Django management command to run hotel scrapers.
"""
import logging
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from hotels.models import Hotel, Price
from scrapers.booking_scraper import BookingScraper

# Allow DB access even if Playwright leaves an async loop open
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scrape hotel data from various platforms'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            default='all',
            help='Platform to scrape: booking, airbnb, tripadvisor, local, or all'
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            default=True,
            help='Run browser in headless mode'
        )
        parser.add_argument(
            '--max-hotels',
            type=int,
            default=50,
            help='Maximum number of hotels to scrape per platform'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without saving to database'
        )
    
    def handle(self, *args, **options):
        platform = options['platform']
        headless = options['headless']
        max_hotels = options['max_hotels']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('Starting hotel scraping...'))
        
        if platform in ['booking', 'all']:
            self.scrape_booking(headless, max_hotels, dry_run)
        
        # Future: Add more platforms
        # if platform in ['airbnb', 'all']:
        #     self.scrape_airbnb(headless, max_hotels, dry_run)
        
        self.stdout.write(self.style.SUCCESS('Scraping completed!'))
    
    def scrape_booking(self, headless, max_hotels, dry_run):
        """Scrape Booking.com."""
        self.stdout.write('Scraping Booking.com...')
        
        try:
            with BookingScraper(headless=headless) as scraper:
                hotels_data = scraper.scrape(max_hotels=max_hotels)
                
                if dry_run:
                    self.stdout.write(f'DRY RUN: Would save {len(hotels_data)} hotels')
                    for hotel_data in hotels_data[:5]:  # Show first 5
                        self.stdout.write(f"  - {hotel_data.get('name')}: ${hotel_data.get('price_per_night')}")
                    return
                
                saved_count = 0
                for hotel_data in hotels_data:
                    if self.save_hotel_data(hotel_data):
                        saved_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Saved {saved_count}/{len(hotels_data)} hotels from Booking.com')
                )
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error scraping Booking.com: {str(e)}'))
            logger.exception("Booking.com scraping failed")
    
    @transaction.atomic
    def save_hotel_data(self, data):
        """Save or update hotel and price data."""
        try:
            # Try to find existing hotel by name (simple matching)
            hotel, created = Hotel.objects.get_or_create(
                name__iexact=data.get('name', ''),
                defaults={
                    'name': data.get('name', ''),
                    'address': data.get('address', ''),
                    'stars': data.get('stars', 0),
                    'source_platform': data.get('platform', ''),
                    'description': data.get('description', ''),
                    'images': data.get('images', []),
                    'main_image': data.get('main_image', ''),
                    'amenities': data.get('amenities', {}),
                }
            )
            
            if not created:
                # Update existing hotel
                if data.get('address'):
                    hotel.address = data['address']
                if data.get('stars'):
                    hotel.stars = data['stars']
                if data.get('description'):
                    hotel.description = data['description']
                if data.get('images'):
                    hotel.images = data['images']
                if data.get('main_image'):
                    hotel.main_image = data['main_image']
                if data.get('amenities'):
                    hotel.amenities = data['amenities']
                hotel.save()
            
            # Create or update price
            platform_url = data.get('platform_url', '')
            price_per_night = data.get('price_per_night')
            
            if price_per_night:
                price_obj, created = Price.objects.update_or_create(
                    hotel=hotel,
                    platform=data.get('platform', 'booking'),
                    defaults={
                        'platform_url': platform_url,
                        'price_per_night': price_per_night,
                        'currency': 'ARS',
                        'is_available': True,
                    }
                )
                
                # Trigger alerts if price dropped (Integrated instead of Celery)
                from hotels.tasks import check_price_drops_and_notify
                check_price_drops_and_notify(hotel.id, price_per_night)
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving hotel {data.get('name')}: {str(e)}")
            return False
