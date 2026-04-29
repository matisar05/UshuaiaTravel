from __future__ import annotations

from typing import Any
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import connections
from django.db.utils import OperationalError
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Hotel, Price, PriceAlert
from .serializers import (
    HotelListSerializer, HotelDetailSerializer, PriceSerializer,
    PriceAlertSerializer, MultiHotelCompareSerializer,
)
from .services import CurrencyService, HotelService
from .repositories import HotelRepository


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request: Request, version: str | None = None) -> Response:
    db_status = "ok"
    try:
        connections["default"].cursor()
    except OperationalError:
        db_status = "unavailable"

    overall = db_status == "ok"

    return Response(
        {
            "status": "healthy" if overall else "degraded",
            "database": db_status,
            "service": "ushuaia-travel-api",
        },
        status=status.HTTP_200_OK if overall else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def create_price_alert(request: Request, version: str | None = None) -> Response:
    serializer = PriceAlertSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class HotelFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="cached_min_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="cached_min_price", lookup_expr="lte")
    min_stars = django_filters.NumberFilter(field_name="stars", lookup_expr="gte")

    class Meta:
        model = Hotel
        fields = {
            "hotel_type": ["exact"],
            "location_type": ["exact"],
            "stars": ["exact"],
            "pet_friendly": ["exact"],
        }


class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HotelFilter
    search_fields = ["name", "description"]
    ordering_fields = ["cached_min_price", "stars", "name"]
    ordering = ["name"]

    def get_serializer_class(self) -> type:
        if self.action == "retrieve":
            return HotelDetailSerializer
        return HotelListSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["currency"] = self.request.query_params.get("currency", "ARS")
        return context

    @method_decorator(cache_page(60 * 15))
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return HotelRepository.get_with_active_prices()

    @action(detail=False, methods=["get"])
    def featured(self, request: Request, **kwargs: Any) -> Response:
        hotels = HotelRepository.get_featured()
        page = self.paginate_queryset(hotels)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(hotels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def rates(self, request: Request, **kwargs: Any) -> Response:
        rates = CurrencyService.get_rates()
        return Response(rates)

    @action(detail=False, methods=["post"])
    def compare(self, request: Request, **kwargs: Any) -> Response:
        input_serializer = MultiHotelCompareSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        hotel_ids = input_serializer.validated_data["hotel_ids"]

        hotels = Hotel.objects.filter(id__in=hotel_ids, is_active=True).prefetch_related("prices")
        serializer = HotelListSerializer(
            hotels, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def compare_prices(self, request: Request, pk: int | None = None, **kwargs: Any) -> Response:
        hotel = self.get_object()
        prices = hotel.prices.filter(is_available=True)

        comparison: dict[str, list] = {}
        for price in prices:
            serializer = PriceSerializer(price, context=self.get_serializer_context())
            platform = price.platform
            comparison.setdefault(platform, []).append(serializer.data)

        cheapest = prices.order_by("price_per_night").first()
        cheapest_data = (
            PriceSerializer(cheapest, context=self.get_serializer_context()).data
            if cheapest else None
        )

        return Response({
            "hotel_id": hotel.id,
            "hotel_name": hotel.name,
            "comparison": comparison,
            "cheapest": cheapest_data,
        })


class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Price.objects.filter(is_available=True).select_related("hotel")
    serializer_class = PriceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["platform", "hotel", "currency"]
    ordering_fields = ["price_per_night", "last_checked"]
    ordering = ["price_per_night"]

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["currency"] = self.request.query_params.get("currency", "ARS")
        return context


@api_view(["POST"])
@permission_classes([AllowAny])
def create_donation(request: Request, version: str | None = None) -> Response:
    amount = request.data.get("amount", 0)
    description = request.data.get("description", "Donación Ushuaia Travel")
    platform = request.data.get("platform", "mercadopago")

    if not amount or float(amount) <= 0:
        return Response({"error": "Monto inválido"}, status=status.HTTP_400_BAD_REQUEST)

    if platform == "mercadopago":
        try:
            from ushuaia_travel.mercadopago_service import create_donation_preference
            result = create_donation_preference(
                amount=float(amount),
                description=description,
                payer_email=request.data.get("email", ""),
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": f"Error al crear preferencia: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Plataforma no soportada"}, status=status.HTTP_400_BAD_REQUEST)
