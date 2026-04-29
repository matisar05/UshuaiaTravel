"""
Sync hotels from Amadeus Self-Service API.
"""
import logging
from django.core.management.base import BaseCommand, CommandParser
from hotels.amadeus_service import AmadeusService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync hotel data from Amadeus API"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--max-hotels",
            type=int,
            default=20,
            help="Maximum hotels to sync",
        )

    def handle(self, *args, **options) -> None:
        max_hotels: int = options["max_hotels"]

        self.stdout.write(self.style.SUCCESS("Syncing hotels from Amadeus..."))

        try:
            service = AmadeusService()
            saved = service.sync(max_hotels=max_hotels)
            self.stdout.write(
                self.style.SUCCESS(f"Synced {saved} hotels from Amadeus")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing Amadeus: {e}"))
            logger.exception("Amadeus sync failed")
