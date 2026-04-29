"""
Amadeus Self-Service API client.
Docs: https://developers.amadeus.com/self-service
"""
import logging
import time
from typing import Any
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://test.api.amadeus.com"


class AmadeusClient:
    def __init__(self):
        self.client_id = settings.AMADEUS_API_KEY
        self.client_secret = settings.AMADEUS_API_SECRET
        self._token: str | None = None
        self._token_expires: float = 0

    def _authenticate(self) -> str:
        if self._token and time.time() < self._token_expires - 60:
            return self._token

        logger.info("Authenticating with Amadeus...")
        resp = requests.post(
            f"{BASE_URL}/v1/security/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires = time.time() + data.get("expires_in", 1799)
        logger.info("Amadeus authenticated successfully")
        return self._token

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        token = self._authenticate()
        resp = requests.get(
            f"{BASE_URL}{path}",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_hotels_by_city(self, city_code: str = "USH") -> list[dict]:
        """Get hotel list for a city. Ushuaia = USH."""
        logger.info(f"Fetching hotels for city {city_code}...")
        data = self._get(
            "/v1/reference-data/locations/hotels/by-city",
            params={"cityCode": city_code, "radius": 50, "radiusUnit": "KM"},
        )
        return data.get("data", [])

    def get_hotel_offers(
        self,
        hotel_ids: list[str],
        check_in: str,
        check_out: str,
        adults: int = 2,
        currency: str = "ARS",
    ) -> list[dict]:
        """Get room offers + prices for specific hotels."""
        logger.info(f"Fetching offers for {len(hotel_ids)} hotels...")
        data = self._get(
            "/v3/shopping/hotel-offers",
            params={
                "hotelIds": ",".join(hotel_ids),
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "adults": adults,
                "currency": currency,
                "radius": 50,
                "radiusUnit": "KM",
                "bestRateOnly": True,
            },
        )
        return data.get("data", [])
