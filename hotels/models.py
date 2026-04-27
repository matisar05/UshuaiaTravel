from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

class Hotel(BaseModel):
    LOCATION_CHOICES = [
        ('centro', 'Centro'),
        ('afueras', 'Afueras de la Ciudad'),
        ('montaña', 'Montaña'),
    ]
    
    TYPE_CHOICES = [
        ('hotel', 'Hotel'),
        ('hostel', 'Hostel'),
        ('apart', 'Apart Hotel'),
        ('cabaña', 'Cabaña'),
        ('casa', 'Casa/Departamento'),
    ]
    
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=500)
    
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        default='centro',
        db_index=True
    )
    hotel_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='hotel',
        db_index=True
    )
    stars = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
        db_index=True
    )
    
    pet_friendly = models.BooleanField(default=False, db_index=True)
    amenities = models.JSONField(default=dict, blank=True)
    contact_info = models.JSONField(default=dict, blank=True)
    images = models.JSONField(default=list, blank=True)
    main_image = models.URLField(max_length=1000, blank=True)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location = gis_models.PointField(geography=True, null=True, blank=True)
    
    source_platform = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    cached_min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True)
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['stars', 'pet_friendly', 'location_type']),
            GinIndex(fields=['search_vector']),
            gis_models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_hotel_type_display()})"
    
    def get_min_price(self):
        """Get minimum price across all platforms."""
        prices = self.prices.filter(is_available=True)
        if prices.exists():
            return prices.order_by('price_per_night').first().price_per_night
        return None
    
    def get_price_range(self):
        """Get price range for this hotel."""
        prices = self.prices.filter(is_available=True)
        if prices.exists():
            min_price = prices.order_by('price_per_night').first().price_per_night
            max_price = prices.order_by('-price_per_night').first().price_per_night
            return {'min': min_price, 'max': max_price}
        return None


class Price(models.Model):
    """Price information from different platforms for comparison."""
    
    PLATFORM_CHOICES = [
        ('booking', 'Booking.com'),
        ('airbnb', 'Airbnb'),
        ('tripadvisor', 'TripAdvisor'),
        ('local', 'Sitio Local'),
        ('direct', 'Sitio Oficial'),
    ]
    
    CURRENCY_CHOICES = [
        ('ARS', 'Peso Argentino'),
        ('USD', 'Dólar Estadounidense'),
        ('EUR', 'Euro'),
    ]
    
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='prices'
    )
    
    # Platform Information
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        db_index=True
    )
    platform_url = models.URLField(max_length=1000)
    
    # Price Information
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='ARS'
    )
    
    # Room Details
    room_type = models.CharField(max_length=200, blank=True)
    max_guests = models.IntegerField(default=2)
    
    # Availability
    is_available = models.BooleanField(default=True)
    last_checked = models.DateTimeField(auto_now=True, db_index=True)
    
    # Additional Info
    notes = models.TextField(
        blank=True,
        help_text="Precios incluyen desayuno, cancelación gratis, etc."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price_per_night']
        verbose_name = 'Precio'
        verbose_name_plural = 'Precios'
        indexes = [
            models.Index(fields=['platform', 'is_available']),
            models.Index(fields=['last_checked']),
        ]
    
    def __str__(self):
        return f"{self.hotel.name} - {self.get_platform_display()}: ${self.price_per_night}"


class PriceAlert(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='price_alerts')
    user_email = models.EmailField()
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
