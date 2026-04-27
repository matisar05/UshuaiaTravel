from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Hotel, Price
from .serializers import HotelListSerializer, HotelDetailSerializer, PriceSerializer


class HotelFilter(django_filters.FilterSet):
    """Custom filter for hotels with price range and other criteria."""
    
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    min_stars = django_filters.NumberFilter(field_name='stars', lookup_expr='gte')
    
    class Meta:
        model = Hotel
        fields = {
            'hotel_type': ['exact'],
            'location_type': ['exact'],
            'stars': ['exact'],
            'pet_friendly': ['exact'],
        }
    
    def filter_min_price(self, queryset, name, value):
        """Filter hotels with minimum price above value."""
        hotel_ids = []
        for hotel in queryset:
            min_price = hotel.get_min_price()
            if min_price and min_price >= value:
                hotel_ids.append(hotel.id)
        return queryset.filter(id__in=hotel_ids)
    
    def filter_max_price(self, queryset, name, value):
        """Filter hotels with minimum price below value."""
        hotel_ids = []
        for hotel in queryset:
            min_price = hotel.get_min_price()
            if min_price and min_price <= value:
                hotel_ids.append(hotel.id)
        return queryset.filter(id__in=hotel_ids)


from django.db.models import Min

class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for hotels.
    
    Provides list and detail views with filtering, searching, and ordering.
    
    **Filters:**
    - hotel_type: hotel, hostel, apart, cabaña, casa
    - location_type: centro, afueras, montaña
    - stars: 0-5
    - min_stars: minimum star rating
    - pet_friendly: true/false
    - min_price: minimum price filter
    - max_price: maximum price filter
    
    **Search:**
    - name, address, description
    
    **Ordering:**
    - name (default), stars, -stars, min_price, -min_price, created_at
    """
    
    queryset = Hotel.objects.filter(is_active=True).prefetch_related('prices')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HotelFilter
    search_fields = ['name', 'address', 'description']
    ordering_fields = ['name', 'stars', 'min_price', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Annotate queryset with minimum price for ordering."""
        return super().get_queryset().annotate(min_price=Min('prices__price_per_night'))
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == 'list':
            return HotelListSerializer
        return HotelDetailSerializer
    
    @action(detail=True, methods=['get'])
    def compare_prices(self, request, pk=None):
        """
        Get price comparison across all platforms for a specific hotel.
        
        Returns prices grouped by platform with availability status.
        """
        hotel = self.get_object()
        prices = hotel.prices.filter(is_available=True).order_by('price_per_night')
        
        # Group by platform
        comparison = {}
        for price in prices:
            platform = price.get_platform_display()
            if platform not in comparison:
                comparison[platform] = []
            comparison[platform].append(PriceSerializer(price).data)
        
        return Response({
            'hotel_id': hotel.id,
            'hotel_name': hotel.name,
            'comparison': comparison,
            'cheapest': PriceSerializer(prices.first()).data if prices.exists() else None
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured hotels (highest rated with available prices)."""
        hotels = self.queryset.filter(stars__gte=4).order_by('-stars', 'name')[:10]
        serializer = self.get_serializer(hotels, many=True)
        return Response(serializer.data)


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
