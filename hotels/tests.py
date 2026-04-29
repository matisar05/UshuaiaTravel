from __future__ import annotations

import json
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

import requests as requests_lib

from .models import Hotel, Price
from .services import CurrencyService, HotelService
from .exceptions import NotFoundError, ValidationError, ExternalServiceError
from .repositories import HotelRepository, PriceRepository


class TestCurrencyService(TestCase):
    def setUp(self):
        import django.core.cache as cache_module
        self.cache = cache_module.cache
        self.cache.clear()

    def test_get_rates_returns_fallback_on_request_error(self):
        with patch("hotels.services.requests.get", side_effect=requests_lib.RequestException("Network error")):
            rates = CurrencyService.get_rates()
            self.assertIsInstance(rates, dict)
            self.assertIn("mep", rates)
            self.assertEqual(rates["mep"], 1000.0)

    def test_get_rates_parses_api_response_correctly(self):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"casa": "oficial", "venta": "920.5"},
            {"casa": "mep", "venta": "1100"},
        ]
        mock_response.raise_for_status = MagicMock()

        with patch("hotels.services.requests.get", return_value=mock_response):
            rates = CurrencyService.get_rates()
            self.assertEqual(rates["oficial"], 920.5)
            self.assertEqual(rates["mep"], 1100.0)

    def test_convert_same_currency_returns_same_amount(self):
        result = CurrencyService.convert(100, "ARS", "ARS")
        self.assertEqual(result, Decimal("100"))

    def test_convert_ars_to_usd_uses_rate(self):
        mock_rates = {"mep": 1000.0}
        with patch.object(CurrencyService, "get_rates", return_value=mock_rates):
            result = CurrencyService.convert(1000, "ARS", "USD", rate_type="mep")
            self.assertEqual(result, Decimal("1.00"))

    def test_convert_usd_to_ars_uses_rate(self):
        mock_rates = {"mep": 1000.0}
        with patch.object(CurrencyService, "get_rates", return_value=mock_rates):
            result = CurrencyService.convert(1, "USD", "ARS", rate_type="mep")
            self.assertEqual(result, Decimal("1000.00"))

    def test_get_rates_uses_cache_on_second_call(self):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"casa": "mep", "venta": "1100"}]
        mock_response.raise_for_status = MagicMock()

        with patch("hotels.services.requests.get", return_value=mock_response) as mock_get:
            CurrencyService.get_rates()
            CurrencyService.get_rates()
            self.assertEqual(mock_get.call_count, 1)


class TestHotelService(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Hotel Test",
            address="Ushuaia 123",
            hotel_type="hotel",
            is_active=True,
        )
        Price.objects.create(
            hotel=self.hotel,
            platform="booking",
            platform_url="https://booking.com/1",
            price_per_night=Decimal("50000"),
            currency="ARS",
            is_available=True,
        )
        Price.objects.create(
            hotel=self.hotel,
            platform="airbnb",
            platform_url="https://airbnb.com/1",
            price_per_night=Decimal("20"),
            currency="USD",
            is_available=True,
        )

    def test_calculate_price_range_with_prices(self):
        with patch.object(CurrencyService, "get_rates", return_value={"mep": 1000.0}):
            price_range = HotelService.calculate_price_range(self.hotel.id)
            self.assertIsNotNone(price_range)
            self.assertIn("min_price", price_range)
            self.assertIn("max_price", price_range)
            self.assertEqual(price_range["currency"], "ARS")

    def test_calculate_price_range_no_prices_returns_none(self):
        Price.objects.all().update(is_available=False)
        result = HotelService.calculate_price_range(self.hotel.id)
        self.assertIsNone(result)

    def test_calculate_price_range_with_usd_target(self):
        with patch.object(CurrencyService, "get_rates", return_value={"mep": 1000.0}):
            price_range = HotelService.calculate_price_range(self.hotel.id, target_currency="USD")
            self.assertIsNotNone(price_range)
            self.assertEqual(price_range["currency"], "USD")

    def test_update_cached_min_price_updates_hotel(self):
        with patch.object(CurrencyService, "get_rates", return_value={"mep": 1000.0}):
            HotelService.update_cached_min_price(self.hotel.id)
            self.hotel.refresh_from_db()
            self.assertIsNotNone(self.hotel.cached_min_price)


class TestHealthCheckEndpoint(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_returns_200(self):
        url = reverse("health-check", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")
        self.assertEqual(response.data["database"], "ok")

    def test_health_check_returns_503_when_db_unavailable(self):
        with patch("hotels.views.connections") as mock_connections:
            from django.db.utils import OperationalError
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = OperationalError("Connection refused")
            mock_connections.__getitem__.return_value = mock_conn
            mock_connections.all.return_value = [mock_conn]

            url = reverse("health-check", kwargs={"version": "v1"})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


class TestHotelsAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.hotel = Hotel.objects.create(
            name="Hotel Glaciar",
            description="Hotel en el centro",
            address="Av. San Martin 123",
            hotel_type="hotel",
            location_type="centro",
            stars=4,
            pet_friendly=True,
            is_active=True,
            cached_min_price=Decimal("45000"),
        )
        self.price = Price.objects.create(
            hotel=self.hotel,
            platform="booking",
            platform_url="https://booking.com/hotel1",
            price_per_night=Decimal("45000"),
            currency="ARS",
            is_available=True,
        )
        self.inactive_hotel = Hotel.objects.create(
            name="Hotel Inactivo",
            address="Calle Falsa 456",
            is_active=False,
        )

    def test_list_hotels_returns_paginated_response(self):
        url = reverse("hotel-list", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_hotels_excludes_inactive(self):
        url = reverse("hotel-list", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.data["count"], 1)

    def test_hotel_detail_returns_full_data(self):
        url = reverse("hotel-detail", kwargs={"version": "v1", "pk": self.hotel.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Hotel Glaciar")
        self.assertEqual(response.data["stars"], 4)

    def test_hotel_detail_404_for_inactive(self):
        url = reverse("hotel-detail", kwargs={"version": "v1", "pk": self.inactive_hotel.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_hotel_type(self):
        url = reverse("hotel-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"hotel_type": "hotel"})
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(url, {"hotel_type": "hostel"})
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_pet_friendly(self):
        url = reverse("hotel-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"pet_friendly": "true"})
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_price_range(self):
        url = reverse("hotel-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"min_price": 40000, "max_price": 50000})
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(url, {"min_price": 100000})
        self.assertEqual(response.data["count"], 0)

    def test_search_by_name(self):
        url = reverse("hotel-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"search": "Glaciar"})
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(url, {"search": "Inexistente"})
        self.assertEqual(response.data["count"], 0)

    def test_prices_endpoint(self):
        url = reverse("price-list", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rates_endpoint(self):
        with patch.object(CurrencyService, "get_rates", return_value={"mep": 1000.0}):
            url = reverse("hotel-rates", kwargs={"version": "v1"})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_404_error_envelope(self):
        url = reverse("hotel-detail", kwargs={"version": "v1", "pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertIn("error", response.data)


class TestExceptionHandler(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_validation_error_when_invalid_pagination(self):
        url = reverse("hotel-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"page": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_internal_error_structure(self):
        with patch("hotels.views.HotelViewSet.list", side_effect=Exception("Unexpected")):
            url = reverse("hotel-list", kwargs={"version": "v1"})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertFalse(response.data["success"])
            self.assertIn("error", response.data)
            self.assertEqual(response.data["error"]["code"], "internal_error")


class TestRepositories(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Hotel Repo Test",
            address="Ushuaia 1",
            is_active=True,
        )
        self.price = Price.objects.create(
            hotel=self.hotel,
            platform="booking",
            platform_url="https://booking.com/repo",
            price_per_night=Decimal("30000"),
            currency="ARS",
            is_available=True,
        )

    def test_get_active_hotels_excludes_inactive(self):
        Hotel.objects.create(name="Inactivo", address="x", is_active=False)
        hotels = HotelRepository.get_active_hotels()
        self.assertEqual(hotels.count(), 1)

    def test_get_with_active_prices(self):
        hotels = HotelRepository.get_with_active_prices()
        self.assertEqual(hotels.count(), 1)

    def test_get_or_create_by_name_existing(self):
        hotel, created = HotelRepository.get_or_create_by_name(
            "Hotel Repo Test", defaults={"address": "Ushuaia 1", "stars": 5}
        )
        self.assertFalse(created)
        self.assertEqual(hotel.name, "Hotel Repo Test")

    def test_get_or_create_by_name_new(self):
        hotel, created = HotelRepository.get_or_create_by_name(
            "Hotel Nuevo", defaults={"address": "Ushuaia 99", "stars": 3}
        )
        self.assertTrue(created)
        self.assertEqual(hotel.name, "Hotel Nuevo")

    def test_get_active_prices_for_hotel(self):
        prices = PriceRepository.get_active_prices_for_hotel(self.hotel.id)
        self.assertEqual(prices.count(), 1)

    def test_get_min_price_for_hotel(self):
        min_price = PriceRepository.get_min_price_for_hotel(self.hotel.id)
        self.assertIsNotNone(min_price)
        self.assertEqual(min_price.price_per_night, Decimal("30000"))


class TestAppErrorExceptions(TestCase):
    def test_not_found_error_default_message(self):
        error = NotFoundError(resource="Hotel")
        self.assertEqual(error.message, "Hotel not found")
        self.assertEqual(error.http_status, 404)

    def test_validation_error_with_details(self):
        error = ValidationError(errors={"email": ["Required"]})
        self.assertEqual(error.http_status, 400)
        self.assertEqual(error.errors["email"], ["Required"])

    def test_external_service_error(self):
        error = ExternalServiceError(service="DolarAPI")
        self.assertEqual(error.http_status, 502)
        self.assertEqual(error.code, "external_service_error")