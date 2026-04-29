import logging
import requests
from decimal import Decimal
from django.core.cache import cache
from .repositories import HotelRepository, PriceRepository
from .exceptions import ExternalServiceError, NotFoundError

logger = logging.getLogger(__name__)


class CurrencyService:
    API_URL = "https://dolarapi.com/v1/dolares"
    CACHE_KEY = "exchange_rates"
    CACHE_TIMEOUT = 3600  # 1 hour

    FALLBACK_RATES = {
        "oficial": 850.0,
        "mep": 1000.0,
        "blue": 1050.0,
        "tarjeta": 1400.0,
    }

    @staticmethod
    def get_rates() -> dict[str, float]:
        rates: dict | None = cache.get(CurrencyService.CACHE_KEY)
        if rates:
            return rates

        try:
            response = requests.get(CurrencyService.API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            rates = {item["casa"]: float(item["venta"]) for item in data if "casa" in item}
            cache.set(CurrencyService.CACHE_KEY, rates, CurrencyService.CACHE_TIMEOUT)
            return rates
        except requests.RequestException as e:
            logger.error(f"DolarAPI request failed: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"DolarAPI response parsing failed: {e}")

        logger.warning("Using fallback exchange rates")
        return dict(CurrencyService.FALLBACK_RATES)

    @staticmethod
    def convert(
        amount: Decimal | float | int,
        from_currency: str,
        to_currency: str,
        rate_type: str = "mep",
    ) -> Decimal:
        if from_currency == to_currency:
            return Decimal(str(amount))

        rates = CurrencyService.get_rates()
        rate = Decimal(str(rates.get(rate_type, rates.get("mep", 1000))))

        if from_currency == "ARS" and to_currency == "USD":
            return Decimal(str(amount)) / rate
        elif from_currency == "USD" and to_currency == "ARS":
            return Decimal(str(amount)) * rate

        return Decimal(str(amount))


class HotelService:
    @staticmethod
    def calculate_price_range(hotel_id: int, target_currency: str = "ARS") -> dict | None:
        prices = PriceRepository.get_active_prices_for_hotel(hotel_id)
        if not prices.exists():
            return None

        all_prices: list[Decimal] = []
        for p in prices:
            converted = CurrencyService.convert(
                p.price_per_night, p.currency, target_currency
            )
            all_prices.append(converted)

        return {
            "min_price": min(all_prices),
            "max_price": max(all_prices),
            "currency": target_currency,
        }

    @staticmethod
    def update_cached_min_price(hotel_id: int) -> None:
        price_data = HotelService.calculate_price_range(hotel_id, target_currency="ARS")
        if price_data and price_data["min_price"]:
            HotelRepository.update_cached_price(hotel_id, price_data["min_price"])
