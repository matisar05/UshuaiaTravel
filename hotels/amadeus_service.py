"""
Maps Amadeus API responses to our Hotel and Price models.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from hotels.models import Hotel, Price
from hotels.repositories import HotelRepository, PriceRepository
from ushuaia_travel.amadeus_client import AmadeusClient

logger = logging.getLogger(__name__)

PLATFORM = "amadeus"

AMENITY_MAP: dict[str, str] = {
    "WIFI": "Wi-Fi",
    "PARKING": "Estacionamiento",
    "RESTAURANT": "Restaurante",
    "ROOM_SERVICE": "Room Service",
    "BAR": "Bar",
    "GYM": "Gimnasio",
    "POOL": "Piscina",
    "SPA": "Spa",
    "PET_ALLOWED": "Pet Friendly",
    "AIR_CONDITIONING": "Aire Acondicionado",
    "BREAKFAST": "Desayuno",
    "LAUNDRY": "Lavandería",
}


class AmadeusService:
    def __init__(self):
        self.client = AmadeusClient()

    def sync(self, max_hotels: int = 20) -> int:
        saved = 0

        hotels_data = self.client.get_hotels_by_city("USH")
        logger.info(f"Amadeus returned {len(hotels_data)} hotels for Ushuaia")

        hotel_ids = [h["hotelId"] for h in hotels_data[:max_hotels] if h.get("hotelId")]
        if not hotel_ids:
            logger.warning("No hotel IDs found in Amadeus response")
            return 0

        check_in = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")

        offers_data = self.client.get_hotel_offers(hotel_ids, check_in, check_out)
        logger.info(f"Amadeus returned offers for {len(offers_data)} hotels")

        for offer in offers_data:
            try:
                self._save_hotel(offer)
                saved += 1
            except Exception as e:
                logger.warning(f"Error saving Amadeus hotel: {e}")

        return saved

    def _save_hotel(self, offer: dict) -> Hotel | None:
        hotel_data = offer.get("hotel", {})
        name = hotel_data.get("name", "")
        if not name:
            return None

        address_lines = hotel_data.get("address", {}).get("lines", [])
        address = ", ".join(address_lines) if address_lines else ""

        hotel_id = hotel_data.get("hotelId", "")
        lat = hotel_data.get("latitude")
        lon = hotel_data.get("longitude")

        images = []
        for media in hotel_data.get("media", []):
            uri = media.get("uri", "")
            if uri:
                images.append(uri)

        amenities = self._map_amenities(hotel_data.get("amenities", []))

        stars_str = hotel_data.get("rating", "")
        stars = int(stars_str[0]) if stars_str and stars_str[0].isdigit() else 0

        pet_friendly = any(
            "PET" in a or "pet" in a.lower() for a in hotel_data.get("amenities", [])
        )

        contact = self._build_contact(hotel_data.get("contact", {}))

        hotel, created = HotelRepository.get_or_create_by_name(
            name=name,
            defaults={
                "name": name,
                "address": address,
                "stars": stars,
                "pet_friendly": pet_friendly,
                "source_platform": PLATFORM,
                "images": images,
                "main_image": images[0] if images else "",
                "amenities": amenities,
                "contact_info": contact,
                "latitude": float(lat) if lat else None,
                "longitude": float(lon) if lon else None,
            },
        )

        if not created:
            HotelRepository.update(
                hotel.id,
                address=address or hotel.address,
                stars=stars or hotel.stars,
                pet_friendly=pet_friendly,
                images=images or hotel.images,
                main_image=(images[0] if images else hotel.main_image),
                amenities=amenities or hotel.amenities,
                contact_info=contact or hotel.contact_info,
                latitude=float(lat) if lat else hotel.latitude,
                longitude=float(lon) if lon else hotel.longitude,
            )

        for room_offer in offer.get("offers", []):
            price_data = room_offer.get("price", {})
            total = price_data.get("total", "0")
            currency = price_data.get("currency", "ARS")
            try:
                price_val = Decimal(total)
            except Exception:
                continue

            room_type = room_offer.get("room", {}).get("typeEstimated", {}).get("category", "")
            guests = room_offer.get("guests", {}).get("adults", 2)

            if price_val > 0:
                Price.objects.update_or_create(
                    hotel=hotel,
                    platform=PLATFORM,
                    defaults={
                        "platform_url": (
                            f"https://www.amadeus.com/hotel/{hotel_id}"
                            if hotel_id else ""
                        ),
                        "price_per_night": price_val,
                        "currency": currency,
                        "room_type": room_type,
                        "max_guests": guests,
                        "is_available": True,
                    },
                )

        return hotel

    def _map_amenities(self, codes: list[str]) -> list[str]:
        result = []
        for code in codes:
            if code in AMENITY_MAP:
                result.append(AMENITY_MAP[code])
            else:
                result.append(code.replace("_", " ").title())
        return result

    def _build_contact(self, contact: dict) -> dict:
        info = {}
        phone = contact.get("phone", "")
        if phone:
            info["phone"] = phone
        email = contact.get("email", "")
        if email:
            info["email"] = email
        website = contact.get("website", "")
        if website:
            info["website"] = website
        return info
