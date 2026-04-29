"""
RapidAPI client for hotel data aggregation.
Handles Booking.com, Airbnb and TripAdvisor through a single RapidAPI key.
"""
import logging
from typing import Any
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class RapidAPIClient:
    def __init__(self):
        self.key = settings.RAPIDAPI_KEY

    def _get(self, host: str, path: str, params: dict[str, Any] | None = None) -> dict:
        headers = {
            "X-RapidAPI-Key": self.key,
            "X-RapidAPI-Host": host,
        }
        resp = requests.get(
            f"https://{host}{path}",
            headers=headers,
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


class BookingRapidAPI:
    """Booking.com via RapidAPI (booking-com15)."""
    HOST = "booking-com15.p.rapidapi.com"

    def __init__(self):
        self.client = RapidAPIClient()

    def search_hotels(self, location: str = "Ushuaia", check_in: str = "",
                      check_out: str = "", adults: int = 2) -> list[dict]:
        params: dict[str, Any] = {
            "dest_id": "-1014321",
            "search_type": "city",
            "arrival_date": check_in,
            "departure_date": check_out,
            "adults": adults,
            "room_qty": 1,
            "units": "metric",
            "locale": "es-ar",
        }
        for path in [
            "/api/v1/hotels/searchHotels",
            "/api/v1/hotels/search",
            "/api/v1/searchHotels",
            "/api/v1/search",
        ]:
            try:
                data = self.client._get(self.HOST, path, params)
                hotels = data.get("data", {}).get("hotels", data.get("result", []))
                if hotels:
                    return hotels
            except Exception:
                continue

        try:
            alt_params = {
                "query": location,
                "checkin": check_in,
                "checkout": check_out,
                "adults": adults,
            }
            data = self.client._get(self.HOST, "/api/v1/hotels/searchDestination", alt_params)
            dest = data.get("data", [])
            if dest and len(dest) > 0:
                dest_id = str(dest[0].get("dest_id", ""))
                params["dest_id"] = dest_id
                data = self.client._get(self.HOST, "/api/v1/hotels/searchHotels", params)
                return data.get("data", {}).get("hotels", [])
        except Exception:
            pass

        return []

    def get_hotel_details(self, hotel_id: str, check_in: str = "",
                          check_out: str = "") -> dict:
        data = self.client._get(
            self.HOST,
            "/api/v1/hotels/getHotelDetails",
            {
                "hotel_id": hotel_id,
                "arrival_date": check_in,
                "departure_date": check_out,
                "locale": "es-ar",
            },
        )
        return data.get("data", {})


class AirbnbRapidAPI:
    """Airbnb via RapidAPI (airbnb19)."""
    HOST = "airbnb19.p.rapidapi.com"

    def __init__(self):
        self.client = RapidAPIClient()

    def search_listings(self, location: str = "Ushuaia", check_in: str = "",
                        check_out: str = "", adults: int = 2) -> list[dict]:
        try:
            data = self.client._get(
                self.HOST,
                "/api/v2/searchPropertyByPlaceId",
                {
                    "placeId": "ChIJ7cv00DwsDogRAMDACa2m4K8",  # Ushuaia
                    "adults": adults,
                    "guestFavorite": "false",
                    "ib": "false",
                    "currency": "ARS",
                },
            )
            logger.info(f"Airbnb raw keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            results = data.get("data", data.get("results", data.get("list", [])))
            return results if isinstance(results, list) else []
        except Exception as e:
            logger.warning(f"Airbnb search failed: {e}")
            return []


class TripAdvisorRapidAPI:
    """TripAdvisor via RapidAPI (tripadvisor16)."""
    HOST = "tripadvisor16.p.rapidapi.com"

    def __init__(self):
        self.client = RapidAPIClient()

    def search_hotels(self, location: str = "Ushuaia", check_in: str = "",
                      check_out: str = "", adults: int = 2) -> list[dict]:
        data = self.client._get(
            self.HOST,
            "/api/v1/hotels/searchHotels",
            {
                "geoId": "312855",  # Ushuaia correct geoId
                "checkIn": check_in,
                "checkOut": check_out,
                "adults": adults,
            },
        )
        return data.get("data", {}).get("data", [])

    def get_hotel_details(self, hotel_id: str) -> dict:
        data = self.client._get(
            self.HOST,
            "/api/v1/hotels/getHotelDetails",
            {"id": hotel_id},
        )
        return data.get("data", {})
