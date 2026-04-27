from django.contrib import admin
from .models import Hotel, Price


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    """Admin interface for Hotel model."""
    
    list_display = [
        'name',
        'hotel_type',
        'stars',
        'location_type',
        'pet_friendly',
        'is_active',
        'get_min_price_display',
        'updated_at'
    ]
    
    list_filter = [
        'hotel_type',
        'location_type',
        'stars',
        'pet_friendly',
        'is_active',
        'created_at'
    ]
    
    search_fields = ['name', 'address', 'description']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'address')
        }),
        ('Clasificación', {
            'fields': ('hotel_type', 'location_type', 'stars', 'pet_friendly')
        }),
        ('Características', {
            'fields': ('amenities', 'contact_info'),
            'classes': ('collapse',)
        }),
        ('Imágenes', {
            'fields': ('main_image', 'images'),
            'classes': ('collapse',)
        }),
        ('Geolocalización', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('source_platform', 'external_id', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_min_price_display(self, obj):
        """Display minimum price in admin."""
        min_price = obj.get_min_price()
        if min_price:
            return f"${min_price:,.0f} ARS"
        return "Sin precios"
    get_min_price_display.short_description = 'Precio Mínimo'


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Admin interface for Price model."""
    
    list_display = [
        'hotel',
        'platform',
        'price_per_night',
        'currency',
        'room_type',
        'max_guests',
        'is_available',
        'last_checked'
    ]
    
    list_filter = [
        'platform',
        'currency',
        'is_available',
        'last_checked'
    ]
    
    search_fields = ['hotel__name', 'room_type', 'platform_url']
    
    fieldsets = (
        ('Hotel', {
            'fields': ('hotel',)
        }),
        ('Plataforma', {
            'fields': ('platform', 'platform_url')
        }),
        ('Precio', {
            'fields': ('price_per_night', 'currency')
        }),
        ('Detalles de la Habitación', {
            'fields': ('room_type', 'max_guests', 'notes')
        }),
        ('Disponibilidad', {
            'fields': ('is_available', 'last_checked')
        }),
    )
    
    readonly_fields = ['last_checked', 'created_at']
    
    date_hierarchy = 'last_checked'
