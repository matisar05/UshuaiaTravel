from rest_framework import serializers
from .models import Hotel, Price
from .services import HotelService, CurrencyService


class PriceSerializer(serializers.ModelSerializer):
    """Serializer for Price model with currency conversion."""
    
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    price_converted = serializers.SerializerMethodField()
    
    class Meta:
        model = Price
        fields = [
            'id',
            'platform',
            'platform_display',
            'platform_url',
            'price_per_night',
            'currency',
            'price_converted',
            'room_type',
            'max_guests',
            'is_available',
            'notes',
            'last_checked',
        ]

    def get_price_converted(self, obj):
        target_currency = self.context.get('currency', 'ARS')
        if obj.currency == target_currency:
            return obj.price_per_night
        
        return CurrencyService.convert(
            obj.price_per_night, 
            obj.currency, 
            target_currency
        )


class HotelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for hotel listing with currency support."""
    
    min_price = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    location_display = serializers.CharField(source='get_location_type_display', read_only=True)
    type_display = serializers.CharField(source='get_hotel_type_display', read_only=True)
    target_currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id',
            'name',
            'hotel_type',
            'type_display',
            'location_type',
            'location_display',
            'stars',
            'pet_friendly',
            'main_image',
            'address',
            'min_price',
            'price_range',
            'target_currency',
        ]
    
    def get_target_currency(self, obj):
        return self.context.get('currency', 'ARS')

    def get_min_price(self, obj):
        currency = self.context.get('currency', 'ARS')
        price_data = HotelService.calculate_price_range(obj.id, target_currency=currency)
        return price_data['min_price'] if price_data else None
    
    def get_price_range(self, obj):
        currency = self.context.get('currency', 'ARS')
        return HotelService.calculate_price_range(obj.id, target_currency=currency)


class HotelDetailSerializer(serializers.ModelSerializer):
    """Complete serializer for hotel detail view with all prices and currency support."""
    
    prices = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    location_display = serializers.CharField(source='get_location_type_display', read_only=True)
    type_display = serializers.CharField(source='get_hotel_type_display', read_only=True)
    target_currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id',
            'name',
            'description',
            'address',
            'hotel_type',
            'type_display',
            'location_type',
            'location_display',
            'stars',
            'pet_friendly',
            'amenities',
            'contact_info',
            'images',
            'main_image',
            'latitude',
            'longitude',
            'prices',
            'min_price',
            'price_range',
            'target_currency',
            'created_at',
            'updated_at',
        ]
    
    def get_target_currency(self, obj):
        return self.context.get('currency', 'ARS')

    def get_prices(self, obj):
        prices = obj.prices.filter(is_available=True)
        return PriceSerializer(prices, many=True, context=self.context).data

    def get_min_price(self, obj):
        currency = self.context.get('currency', 'ARS')
        price_data = HotelService.calculate_price_range(obj.id, target_currency=currency)
        return price_data['min_price'] if price_data else None
    
    def get_price_range(self, obj):
        currency = self.context.get('currency', 'ARS')
        return HotelService.calculate_price_range(obj.id, target_currency=currency)
