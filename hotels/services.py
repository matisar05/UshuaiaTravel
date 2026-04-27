import requests
from django.core.cache import cache
from django.db.models import Min, Max
from .models import Hotel, Price

class CurrencyService:
    API_URL = "https://dolarapi.com/v1/dolares"
    CACHE_KEY = "exchange_rates"
    CACHE_TIMEOUT = 3600  # 1 hour

    @staticmethod
    def get_rates():
        """Fetch exchange rates from DolarAPI with caching."""
        rates = cache.get(CurrencyService.CACHE_KEY)
        if rates:
            return rates

        try:
            response = requests.get(CurrencyService.API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Map of interest: Oficial, Blue, MEP, Tarjeta
            rates = {item['casa']: item['venta'] for item in data if 'casa' in item}
            cache.set(CurrencyService.CACHE_KEY, rates, CurrencyService.CACHE_TIMEOUT)
            return rates
        except Exception as e:
            print(f"Error fetching rates: {e}")
            # Fallback values if API fails
            return {"oficial": 850, "mep": 1000, "blue": 1050, "tarjeta": 1400}

    @staticmethod
    def convert(amount, from_currency, to_currency, rate_type="mep"):
        """Convert amount between currencies."""
        if from_currency == to_currency:
            return amount
        
        rates = CurrencyService.get_rates()
        rate = rates.get(rate_type, rates.get("mep", 1000))

        if from_currency == "ARS" and to_currency == "USD":
            return amount / rate
        elif from_currency == "USD" and to_currency == "ARS":
            return amount * rate
        
        return amount

class HotelService:
    @staticmethod
    def calculate_price_range(hotel_id, target_currency="ARS"):
        prices = Price.objects.filter(hotel_id=hotel_id, is_available=True)
        if not prices.exists():
            return None
        
        # This is a bit tricky because prices might be in different currencies
        # For simplicity, we'll convert all to target_currency for comparison
        all_prices = []
        for p in prices:
            converted = CurrencyService.convert(p.price_per_night, p.currency, target_currency)
            all_prices.append(converted)
            
        return {
            'min_price': min(all_prices),
            'max_price': max(all_prices),
            'currency': target_currency
        }
    
    @staticmethod
    def update_cached_min_price(hotel_id):
        # We always cache min price in ARS for indexing/filtering consistency
        price_data = HotelService.calculate_price_range(hotel_id, target_currency="ARS")
        if price_data and price_data['min_price']:
            Hotel.objects.filter(id=hotel_id).update(
                cached_min_price=price_data['min_price']
            )
