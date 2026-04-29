"""
Django management command to run hotel scrapers.
"""
import logging
import os
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils import timezone
from hotels.models import PriceHistory
from hotels.repositories import HotelRepository, PriceRepository
from scrapers.booking_scraper import BookingScraper
from scrapers.airbnb_scraper import AirbnbScraper
from scrapers.tripadvisor_scraper import TripAdvisorScraper
from scrapers.despegar_scraper import DespegarScraper
from scrapers.expedia_scraper import ExpediaScraper

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape hotel data from various platforms"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--platform",
            type=str,
            default="all",
            help="Platform to scrape: booking, airbnb, tripadvisor, local, or all",
        )
        parser.add_argument(
            "--headless",
            action="store_true",
            default=True,
            help="Run browser in headless mode",
        )
        parser.add_argument(
            "--max-hotels",
            type=int,
            default=50,
            help="Maximum number of hotels to scrape per platform",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without saving to database",
        )

    def handle(self, *args, **options) -> None:
        platform: str = options["platform"]
        headless: bool = options["headless"]
        max_hotels: int = options["max_hotels"]
        dry_run: bool = options["dry_run"]

        self.stdout.write(self.style.SUCCESS("Starting hotel scraping..."))

        if platform in ["booking", "all"]:
            self._scrape_platform("Booking.com", BookingScraper, headless, max_hotels, dry_run)

        if platform in ["airbnb", "all"]:
            self._scrape_platform("Airbnb", AirbnbScraper, headless, max_hotels, dry_run)

        if platform in ["tripadvisor", "all"]:
            self._scrape_platform("TripAdvisor", TripAdvisorScraper, headless, max_hotels, dry_run)

        if platform in ["despegar", "all"]:
            self._scrape_platform("Despegar", DespegarScraper, headless, max_hotels, dry_run)

        if platform in ["expedia", "all"]:
            self._scrape_platform("Expedia", ExpediaScraper, headless, max_hotels, dry_run)

        self.stdout.write(self.style.SUCCESS("Scraping completed!"))

    def _scrape_platform(
        self, label: str, scraper_class, headless: bool, max_hotels: int, dry_run: bool
    ) -> None:
        self.stdout.write(f"Scraping {label}...")

        try:
            with scraper_class(headless=headless) as scraper:
                hotels_data = scraper.scrape(max_hotels=max_hotels)

                if dry_run:
                    self.stdout.write(f"DRY RUN: Would save {len(hotels_data)} hotels from {label}")
                    for hotel_data in hotels_data[:5]:
                        self.stdout.write(f"  - {hotel_data.get('name')}: ${hotel_data.get('price_per_night')}")
                    return

                saved_count = 0
                for hotel_data in hotels_data:
                    if self.save_hotel_data(hotel_data):
                        saved_count += 1

                self.stdout.write(
                    self.style.SUCCESS(f"Saved {saved_count}/{len(hotels_data)} hotels from {label}")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error scraping {label}: {str(e)}"))
            logger.exception(f"{label} scraping failed")

    @transaction.atomic
    def save_hotel_data(self, data: dict) -> bool:
        try:
            hotel, created = HotelRepository.get_or_create_by_name(
                name=data.get("name", ""),
                defaults={
                    "name": data.get("name", ""),
                    "address": data.get("address", ""),
                    "stars": data.get("stars", 0),
                    "source_platform": data.get("platform", ""),
                    "description": data.get("description", ""),
                    "images": data.get("images", []),
                    "main_image": data.get("main_image", ""),
                    "amenities": data.get("amenities", {}),
                },
            )

            if not created:
                updates: dict = {}
                if data.get("address"):
                    updates["address"] = data["address"]
                if "stars" in data:
                    updates["stars"] = data["stars"]
                if data.get("description"):
                    updates["description"] = data["description"]
                if data.get("images"):
                    updates["images"] = data["images"]
                if data.get("main_image"):
                    updates["main_image"] = data["main_image"]
                if data.get("amenities"):
                    updates["amenities"] = data["amenities"]
                if updates:
                    HotelRepository.update(hotel.id, **updates)

            platform_url: str = data.get("platform_url", "")
            price_per_night = data.get("price_per_night")

            if price_per_night:
                PriceRepository.upsert_price(
                    hotel=hotel,
                    platform=data.get("platform", "booking"),
                    platform_url=platform_url,
                    price_per_night=Decimal(str(price_per_night)),
                    room_type=data.get("room_type", ""),
                    max_guests=data.get("max_guests", 2),
                )

                self._record_price_history(
                    hotel_id=hotel.id,
                    platform=data.get("platform", "booking"),
                    price=Decimal(str(price_per_night)),
                )

                from hotels.tasks import check_price_drops_and_notify
                check_price_drops_and_notify(hotel.id, price_per_night)

            return True

        except Exception as e:
            logger.error(f"Error saving hotel {data.get('name')}: {str(e)}")
            return False

    def _record_price_history(self, hotel_id: int, platform: str, price: Decimal) -> None:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        prev_lowest = PriceHistory.objects.filter(
            hotel_id=hotel_id,
            platform=platform,
            recorded_at__gte=thirty_days_ago,
        ).order_by("price_per_night").first()

        is_lowest = not prev_lowest or price < prev_lowest.price_per_night

        if is_lowest:
            PriceHistory.objects.filter(
                hotel_id=hotel_id,
                platform=platform,
                is_lowest_30d=True,
            ).update(is_lowest_30d=False)

        PriceHistory.objects.create(
            hotel_id=hotel_id,
            platform=platform,
            price_per_night=price,
            currency="ARS",
            recorded_at=now,
            is_lowest_30d=is_lowest,
        )
