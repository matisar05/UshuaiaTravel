from rest_framework import serializers
from .models import Hotel, Price


class PriceSerializer(serializers.ModelSerializer):
    """Serializer for Price model."""
    
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = Price
        fields = [
            'id',
            'platform',
            'platform_display',
            'platform_url',
            'price_per_night',
            'currency',
            'room_type',
            'max_guests',
            'is_available',
            'notes',
            'last_checked',
        ]


class HotelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for hotel listing."""
    
    min_price = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    location_display = serializers.CharField(source='get_location_type_display', read_only=True)
    type_display = serializers.CharField(source='get_hotel_type_display', read_only=True)
    
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
        ]
    
    def get_min_price(self, obj):
        """Get minimum available price."""
        return obj.get_min_price()
    
    def get_price_range(self, obj):
        """Get price range for this hotel."""
        return obj.get_price_range()


class HotelDetailSerializer(serializers.ModelSerializer):
    """Complete serializer for hotel detail view with all prices."""
    
    prices = PriceSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    location_display = serializers.CharField(source='get_location_type_display', read_only=True)
    type_display = serializers.CharField(source='get_hotel_type_display', read_only=True)
    
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
            'created_at',
            'updated_at',
        ]
    
    def get_min_price(self, obj):
        """Get minimum available price."""
        return obj.get_min_price()
    
    def get_price_range(self, obj):
        """Get price range for this hotel."""
        return obj.get_price_range()
