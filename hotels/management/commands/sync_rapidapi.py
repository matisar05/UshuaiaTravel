"""
Sync hotels from RapidAPI (TripAdvisor + Airbnb).
"""
import logging
from django.core.management.base import BaseCommand, CommandParser
from hotels.rapidapi_service import RapidAPISyncService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync hotels from RapidAPI (Booking + TripAdvisor + Airbnb)"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--platform",
            type=str,
            default="all",
            choices=["all", "booking", "tripadvisor", "airbnb"],
            help="Platform to sync",
        )
        parser.add_argument(
            "--max-hotels",
            type=int,
            default=10,
            help="Maximum hotels per platform",
        )

    def handle(self, *args, **options) -> None:
        platform: str = options["platform"]
        max_hotels: int = options["max_hotels"]

        service = RapidAPISyncService()

        try:
            if platform in ("booking", "all"):
                self.stdout.write("Syncing Booking...")
                saved = service.sync_booking(max_hotels)
                self.stdout.write(self.style.SUCCESS(f"Booking: {saved} hotels"))

            if platform in ("tripadvisor", "all"):
                self.stdout.write("Syncing TripAdvisor...")
                saved = service.sync_tripadvisor(max_hotels)
                self.stdout.write(self.style.SUCCESS(f"TripAdvisor: {saved} hotels"))

            if platform in ("airbnb", "all"):
                self.stdout.write("Syncing Airbnb...")
                saved = service.sync_airbnb(max_hotels)
                self.stdout.write(self.style.SUCCESS(f"Airbnb: {saved} hotels"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            logger.exception("RapidAPI sync failed")
