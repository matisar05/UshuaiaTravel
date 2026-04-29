from decimal import Decimal
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from .models import Hotel, Price


class HotelRepository:
    @staticmethod
    def get_active_hotels() -> QuerySet[Hotel]:
        return Hotel.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(hotel_id: int) -> Hotel:
        return get_object_or_404(Hotel, id=hotel_id, is_active=True)

    @staticmethod
    def get_with_active_prices() -> QuerySet[Hotel]:
        from django.db.models import Prefetch
        active_prices = Price.objects.filter(is_available=True)
        return (
            Hotel.objects
            .filter(is_active=True)
            .prefetch_related(Prefetch("prices", queryset=active_prices))
        )

    @staticmethod
    def get_featured() -> QuerySet[Hotel]:
        return Hotel.objects.filter(is_active=True, cached_min_price__isnull=False).order_by(
            "cached_min_price"
        )[:10]

    @staticmethod
    def get_or_create_by_name(name: str, defaults: dict) -> tuple[Hotel, bool]:
        defaults_with_name = {"name": name, **defaults}
        return Hotel.objects.get_or_create(
            name__iexact=name,
            defaults=defaults_with_name,
        )

    @staticmethod
    def update(hotel_id: int, **fields) -> int:
        return Hotel.objects.filter(id=hotel_id).update(**fields)

    @staticmethod
    def update_cached_price(hotel_id: int, price: Decimal) -> int:
        return Hotel.objects.filter(id=hotel_id).update(cached_min_price=price)


class PriceRepository:
    @staticmethod
    def get_active_prices() -> QuerySet[Price]:
        return Price.objects.filter(is_available=True).select_related("hotel")

    @staticmethod
    def get_active_prices_for_hotel(hotel_id: int) -> QuerySet[Price]:
        return Price.objects.filter(hotel_id=hotel_id, is_available=True)

    @staticmethod
    def get_min_price_for_hotel(hotel_id: int) -> Price | None:
        return Price.objects.filter(hotel_id=hotel_id, is_available=True).order_by(
            "price_per_night"
        ).first()

    @staticmethod
    def upsert_price(hotel: Hotel, platform: str, platform_url: str,
                     price_per_night: Decimal, room_type: str = "",
                     max_guests: int = 2) -> tuple[Price, bool]:
        return Price.objects.update_or_create(
            hotel=hotel,
            platform=platform,
            defaults={
                "platform_url": platform_url,
                "price_per_night": price_per_night,
                "currency": "ARS",
                "room_type": room_type,
                "max_guests": max_guests,
                "is_available": True,
            },
        )
