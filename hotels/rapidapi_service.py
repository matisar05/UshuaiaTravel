"""
Sync hotels from RapidAPI (Booking + TripAdvisor + Airbnb).
Maps API responses to Hotel and Price models.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from hotels.models import Hotel, Price
from hotels.repositories import HotelRepository
from ushuaia_travel.rapidapi_client import (
    BookingRapidAPI,
    AirbnbRapidAPI,
    TripAdvisorRapidAPI,
)

logger = logging.getLogger(__name__)


class RapidAPISyncService:
    def __init__(self):
        self.booking = BookingRapidAPI()
        self.airbnb = AirbnbRapidAPI()
        self.tripadvisor = TripAdvisorRapidAPI()

    def _dates(self) -> tuple[str, str]:
        check_in = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
        return check_in, check_out

    def sync_booking(self, max_hotels: int = 10) -> int:
        check_in, check_out = self._dates()
        logger.info("Fetching Booking.com via RapidAPI...")

        results = self.booking.search_hotels(
            location="Ushuaia", check_in=check_in, check_out=check_out
        )
        logger.info(f"Booking returned {len(results)} hotels")

        saved = 0
        for item in results[:max_hotels]:
            try:
                hotel_id = str(item.get("hotel_id", ""))
                detail = {}
                if hotel_id:
                    try:
                        detail = self.booking.get_hotel_details(hotel_id, check_in, check_out)
                    except Exception:
                        pass
                self._save_booking(item, detail)
                saved += 1
            except Exception as e:
                logger.warning(f"Error saving Booking hotel: {e}")
        return saved

    def sync_tripadvisor(self, max_hotels: int = 10) -> int:
        check_in, check_out = self._dates()
        logger.info("Fetching TripAdvisor via RapidAPI...")

        results = self.tripadvisor.search_hotels(
            location="Ushuaia", check_in=check_in, check_out=check_out
        )
        logger.info(f"TripAdvisor returned {len(results)} hotels")

        saved = 0
        for item in results[:max_hotels]:
            try:
                hotel_id = item.get("id") or item.get("hotelId", "")
                detail = {}
                if hotel_id:
                    try:
                        detail = self.tripadvisor.get_hotel_details(str(hotel_id))
                    except Exception:
                        pass
                self._save_tripadvisor(item, detail)
                saved += 1
            except Exception as e:
                logger.warning(f"Error saving TripAdvisor hotel: {e}")
        return saved

    def sync_airbnb(self, max_hotels: int = 10) -> int:
        check_in, check_out = self._dates()
        logger.info("Fetching Airbnb via RapidAPI...")

        results = self.airbnb.search_listings(
            location="Ushuaia", check_in=check_in, check_out=check_out
        )
        logger.info(f"Airbnb returned {len(results)} listings")

        saved = 0
        for item in results[:max_hotels]:
            try:
                self._save_airbnb(item)
                saved += 1
            except Exception as e:
                logger.warning(f"Error saving Airbnb listing: {e}")
        return saved

    def sync_all(self, max_hotels: int = 10) -> dict[str, int]:
        return {
            "booking": self.sync_booking(max_hotels),
            "tripadvisor": self.sync_tripadvisor(max_hotels),
            "airbnb": self.sync_airbnb(max_hotels),
        }

    def _save_booking(self, item: dict, detail: dict) -> Hotel | None:
        name = detail.get("name") or item.get("hotel_name") or item.get("name", "")
        if not name:
            return None

        address = detail.get("address") or item.get("address", "")
        lat = detail.get("latitude") or item.get("latitude")
        lon = detail.get("longitude") or item.get("longitude")

        stars_str = item.get("hotel_class") or detail.get("stars") or "0"
        stars = int(str(stars_str).split(".")[0]) if stars_str else 0

        images = []
        for photo in detail.get("photos", []) or []:
            if isinstance(photo, dict):
                url = photo.get("url_max") or photo.get("url_original") or photo.get("url", "")
            else:
                url = str(photo)
            if url and "http" in url:
                images.append(url)

        amenities_list = []
        for a in detail.get("facilities", []) or []:
            if isinstance(a, dict):
                amenities_list.append(a.get("name", str(a)))
            else:
                amenities_list.append(str(a))

        hotel, created = HotelRepository.get_or_create_by_name(
            name=name,
            defaults={
                "name": name,
                "address": address,
                "stars": stars,
                "source_platform": "booking",
                "images": images,
                "main_image": images[0] if images else "",
                "amenities": amenities_list,
                "latitude": float(lat) if lat else None,
                "longitude": float(lon) if lon else None,
            },
        )

        if not created:
            HotelRepository.update(
                hotel.id,
                address=address or hotel.address,
                stars=stars or hotel.stars,
                images=images or hotel.images,
                main_image=images[0] if images else hotel.main_image,
                amenities=amenities_list or hotel.amenities,
                latitude=float(lat) if lat else hotel.latitude,
                longitude=float(lon) if lon else hotel.longitude,
            )

        price_raw = item.get("min_total_price") or item.get("price_breakdown", {}).get("sum_excluded_raw")
        if not price_raw:
            price_raw = item.get("price") or detail.get("price", 0)

        if price_raw:
            try:
                price_val = Decimal(str(price_raw))
                currency = item.get("currencycode", "ARS")
                Price.objects.update_or_create(
                    hotel=hotel,
                    platform="booking",
                    defaults={
                        "platform_url": detail.get("url") or item.get("url", ""),
                        "price_per_night": price_val,
                        "currency": currency,
                        "room_type": item.get("room_name", ""),
                        "max_guests": item.get("adults", 2),
                        "is_available": True,
                    },
                )
            except Exception as e:
                logger.warning(f"Could not save Booking price: {e}")

        return hotel

    def _save_tripadvisor(self, item: dict, detail: dict) -> Hotel | None:
        name = detail.get("name") or item.get("title") or item.get("name", "")
        if not name:
            return None

        address = detail.get("address") or item.get("address", "")
        lat = detail.get("latitude") or item.get("latitude")
        lon = detail.get("longitude") or item.get("longitude")

        stars = 0
        rating = detail.get("rating") or item.get("rating", "")
        if rating:
            try:
                stars = int(float(rating))
            except (ValueError, TypeError):
                pass

        images = []
        for photo in detail.get("photos", []) or item.get("photos", []):
            if isinstance(photo, dict):
                url = photo.get("url", "") or photo.get("sizes", {}).get("large", "")
            else:
                url = str(photo)
            if url and "http" in url:
                images.append(url)

        amenities_list: list[str] = []
        for a in detail.get("amenities", []) or item.get("amenities", []):
            if isinstance(a, dict):
                amenities_list.append(a.get("name", ""))
            else:
                amenities_list.append(str(a))

        hotel, created = HotelRepository.get_or_create_by_name(
            name=name,
            defaults={
                "name": name,
                "address": address,
                "stars": stars,
                "source_platform": "tripadvisor",
                "images": images,
                "main_image": images[0] if images else "",
                "amenities": amenities_list,
                "latitude": float(lat) if lat else None,
                "longitude": float(lon) if lon else None,
            },
        )

        if not created:
            HotelRepository.update(
                hotel.id,
                address=address or hotel.address,
                stars=stars or hotel.stars,
                images=images or hotel.images,
                main_image=images[0] if images else hotel.main_image,
                amenities=amenities_list or hotel.amenities,
                latitude=float(lat) if lat else hotel.latitude,
                longitude=float(lon) if lon else hotel.longitude,
            )

        price_val = item.get("price") or detail.get("price")
        if not price_val:
            import re
            price_raw = item.get("priceForDisplay") or item.get("displayPrice") or ""
            m = re.search(r"[\d,.]+", str(price_raw))
            if m:
                price_val = m.group(0).replace(",", "")

        if price_val:
            try:
                Price.objects.update_or_create(
                    hotel=hotel,
                    platform="tripadvisor",
                    defaults={
                        "platform_url": detail.get("url") or item.get("url", ""),
                        "price_per_night": Decimal(str(price_val)),
                        "currency": item.get("currency", "ARS"),
                        "room_type": item.get("roomType", ""),
                        "max_guests": item.get("adults", 2),
                        "is_available": True,
                    },
                )
            except Exception as e:
                logger.warning(f"Could not save TripAdvisor price: {e}")

        return hotel

    def _save_airbnb(self, item: dict) -> Hotel | None:
        name = item.get("name") or item.get("title", "")
        if not name:
            return None

        lat = item.get("lat") or item.get("latitude")
        lon = item.get("lng") or item.get("longitude")

        images = []
        for img in item.get("images", []) or item.get("photos", []):
            url = img if isinstance(img, str) else img.get("url", "")
            if url and "http" in url:
                images.append(url)

        stars = 0
        rating = item.get("rating") or item.get("starRating", 0)
        try:
            stars = int(float(rating))
        except (ValueError, TypeError):
            pass

        hotel, created = HotelRepository.get_or_create_by_name(
            name=name,
            defaults={
                "name": name,
                "address": item.get("address", ""),
                "stars": stars,
                "source_platform": "airbnb",
                "images": images,
                "main_image": images[0] if images else "",
                "latitude": float(lat) if lat else None,
                "longitude": float(lon) if lon else None,
            },
        )

        price_val = item.get("price") or item.get("pricePerNight") or 0
        try:
            price_val = Decimal(str(price_val))
        except Exception:
            return hotel

        if price_val > 0:
            Price.objects.update_or_create(
                hotel=hotel,
                platform="airbnb",
                defaults={
                    "platform_url": item.get("url", ""),
                    "price_per_night": price_val,
                    "currency": item.get("currency", "ARS"),
                    "room_type": item.get("roomType", ""),
                    "max_guests": item.get("guests", 2),
                    "is_available": True,
                },
            )

        return hotel
