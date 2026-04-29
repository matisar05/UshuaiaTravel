from __future__ import annotations

from typing import Any
from decimal import Decimal
from rest_framework import serializers
from .models import Hotel, Price, PriceAlert, PriceHistory
from .services import HotelService, CurrencyService


class PriceSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source="get_platform_display", read_only=True)
    price_converted = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = [
            "id",
            "platform",
            "platform_display",
            "platform_url",
            "price_per_night",
            "currency",
            "price_converted",
            "room_type",
            "max_guests",
            "is_available",
            "notes",
            "last_checked",
        ]

    def get_price_converted(self, obj: Price) -> Decimal:
        target_currency: str = self.context.get("currency", "ARS")
        if obj.currency == target_currency:
            return obj.price_per_night

        return CurrencyService.convert(
            obj.price_per_night, obj.currency, target_currency
        )


class HotelListSerializer(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    location_display = serializers.CharField(source="get_location_type_display", read_only=True)
    type_display = serializers.CharField(source="get_hotel_type_display", read_only=True)
    target_currency = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    best_platform = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "hotel_type",
            "type_display",
            "location_type",
            "location_display",
            "stars",
            "pet_friendly",
            "main_image",
            "address",
            "min_price",
            "price_range",
            "target_currency",
            "last_updated",
            "best_platform",
        ]

    def get_target_currency(self, obj: Hotel) -> str:
        return str(self.context.get("currency", "ARS"))

    def get_min_price(self, obj: Hotel) -> Decimal | None:
        currency: str = self.context.get("currency", "ARS")
        price_data = HotelService.calculate_price_range(obj.id, target_currency=currency)
        return price_data["min_price"] if price_data else None

    def get_price_range(self, obj: Hotel) -> dict | None:
        currency: str = self.context.get("currency", "ARS")
        return HotelService.calculate_price_range(obj.id, target_currency=currency)

    def get_last_updated(self, obj: Hotel) -> str | None:
        latest = obj.prices.filter(is_available=True).order_by("-last_checked").first()
        if latest and latest.last_checked:
            return latest.last_checked.isoformat()
        return None

    def get_best_platform(self, obj: Hotel) -> str | None:
        best = obj.prices.filter(is_available=True).order_by("price_per_night").first()
        return best.get_platform_display() if best else None


class HotelDetailSerializer(serializers.ModelSerializer):
    prices = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    location_display = serializers.CharField(source="get_location_type_display", read_only=True)
    type_display = serializers.CharField(source="get_hotel_type_display", read_only=True)
    target_currency = serializers.SerializerMethodField()
    price_history = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "description",
            "address",
            "hotel_type",
            "type_display",
            "location_type",
            "location_display",
            "stars",
            "pet_friendly",
            "amenities",
            "contact_info",
            "images",
            "main_image",
            "latitude",
            "longitude",
            "prices",
            "price_history",
            "min_price",
            "price_range",
            "target_currency",
            "last_updated",
            "created_at",
            "updated_at",
        ]

    def get_target_currency(self, obj: Hotel) -> str:
        return str(self.context.get("currency", "ARS"))

    def get_prices(self, obj: Hotel) -> list[dict]:
        prices = obj.prices.filter(is_available=True)
        return PriceSerializer(prices, many=True, context=self.context).data

    def get_price_history(self, obj: Hotel) -> list[dict]:
        from django.db.models import Min
        history = obj.price_history.order_by("-recorded_at")[:30]
        return PriceHistorySerializer(history, many=True).data

    def get_min_price(self, obj: Hotel) -> Decimal | None:
        currency: str = self.context.get("currency", "ARS")
        price_data = HotelService.calculate_price_range(obj.id, target_currency=currency)
        return price_data["min_price"] if price_data else None

    def get_price_range(self, obj: Hotel) -> dict | None:
        currency: str = self.context.get("currency", "ARS")
        return HotelService.calculate_price_range(obj.id, target_currency=currency)

    def get_last_updated(self, obj: Hotel) -> str | None:
        latest = obj.prices.filter(is_available=True).order_by("-last_checked").first()
        if latest and latest.last_checked:
            return latest.last_checked.isoformat()
        return None


class PriceAlertSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)

    class Meta:
        model = PriceAlert
        fields = [
            "id",
            "hotel",
            "hotel_name",
            "user_email",
            "target_price",
            "target_currency",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "is_active"]


class PriceHistorySerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source="get_platform_display", read_only=True)

    class Meta:
        model = PriceHistory
        fields = ["id", "hotel", "platform", "platform_display", "price_per_night", "currency", "recorded_at", "is_lowest_30d"]


class MultiHotelCompareSerializer(serializers.Serializer):
    hotel_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1, max_length=5)
