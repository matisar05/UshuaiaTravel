from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from django.db.models import Prefetch
from .models import Hotel, Price
from .serializers import HotelListSerializer, HotelDetailSerializer, PriceSerializer
from .services import CurrencyService


class HotelFilter(django_filters.FilterSet):
    """Custom filter for hotels with price range and other criteria."""
    
    min_price = django_filters.NumberFilter(field_name='cached_min_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='cached_min_price', lookup_expr='lte')
    min_stars = django_filters.NumberFilter(field_name='stars', lookup_expr='gte')
    
    class Meta:
        model = Hotel
        fields = {
            'hotel_type': ['exact'],
            'location_type': ['exact'],
            'stars': ['exact'],
            'pet_friendly': ['exact'],
        }


class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for hotels.
    Supports currency conversion via ?currency=USD query parameter.
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HotelFilter
    search_fields = ['name', 'description']
    ordering_fields = ['cached_min_price', 'stars', 'name']
    ordering = ['cached_min_price']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HotelDetailSerializer
        return HotelListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency'] = self.request.query_params.get('currency', 'ARS')
        return context

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        active_prices = Price.objects.filter(is_available=True)
        return Hotel.objects.prefetch_related(
            Prefetch('prices', queryset=active_prices),
        ).filter(is_active=True)

    @action(detail=False, methods=['get'])
    def rates(self, request):
        """Get current exchange rates from DolarAPI."""
        rates = CurrencyService.get_rates()
        return Response(rates)


class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for prices.
    Read-only access to price information.
    """
    
    queryset = Price.objects.filter(is_available=True).select_related('hotel')
    serializer_class = PriceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['platform', 'hotel', 'currency']
    ordering_fields = ['price_per_night', 'last_checked']
    ordering = ['price_per_night']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency'] = self.request.query_params.get('currency', 'ARS')
        return context
