from __future__ import annotations

import logging
from decimal import Decimal
from django.db import models, connection
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

logger = logging.getLogger(__name__)

try:
    from django.contrib.gis.db import models as gis_models
    HAS_GIS = True
except Exception:
    HAS_GIS = False
    logger.warning("GDAL not available. Geo-spatial features disabled.")


def _is_postgresql() -> bool:
    try:
        return connection.vendor == "postgresql"
    except Exception:
        return False


# PostgreSQL-only features
HAS_PG = _is_postgresql()

if HAS_PG:
    from django.contrib.postgres.search import SearchVectorField
    from django.contrib.postgres.indexes import GinIndex


class SoftDeleteQuerySet(models.QuerySet):
    def active(self) -> SoftDeleteQuerySet:
        return self.filter(deleted_at__isnull=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs) -> None:
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

    source_platform = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    cached_min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["stars", "pet_friendly", "location_type"], name="hotel_filter_idx"),
        ]


if HAS_PG:
    Hotel.add_to_class("search_vector", SearchVectorField(null=True))
    Hotel._meta.indexes.append(GinIndex(fields=["search_vector"], name="hotel_search_vector_gin"))

if HAS_GIS:
    Hotel.add_to_class(
        "location",
        gis_models.PointField(geography=True, null=True, blank=True),
    )
    Hotel._meta.indexes.append(gis_models.Index(fields=["location"], name="hotel_location_gist"))

    def __str__(self) -> str:
        return f"{self.name} ({self.get_hotel_type_display()})"

    def get_min_price(self) -> Decimal | None:
        prices = self.prices.filter(is_available=True)
        if prices.exists():
            return prices.order_by("price_per_night").first().price_per_night
        return None

    def get_price_range(self) -> dict | None:
        prices = self.prices.filter(is_available=True)
        if prices.exists():
            min_price = prices.order_by("price_per_night").first().price_per_night
            max_price = prices.order_by("-price_per_night").first().price_per_night
            return {"min": min_price, "max": max_price}
        return None


class Price(models.Model):
    """Price information from different platforms for comparison."""
    
    PLATFORM_CHOICES = [
        ('booking', 'Booking.com'),
        ('airbnb', 'Airbnb'),
        ('tripadvisor', 'TripAdvisor'),
        ('despegar', 'Despegar'),
        ('expedia', 'Expedia'),
        ('amadeus', 'Amadeus'),
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
            models.Index(fields=['platform', 'is_available'], name="price_platform_avail_idx"),
            models.Index(fields=['last_checked'], name="price_last_checked_idx"),
        ]
    
    def __str__(self) -> str:
        return f"{self.hotel.name} - {self.get_platform_display()}: ${self.price_per_night}"


class PriceAlert(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="price_alerts")
    user_email = models.EmailField()
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    target_currency = models.CharField(
        max_length=3,
        choices=Price.CURRENCY_CHOICES,
        default="ARS",
    )
    is_active = models.BooleanField(default=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alerta de Precio"
        verbose_name_plural = "Alertas de Precio"
        indexes = [
            models.Index(fields=["hotel", "is_active"], name="pricealert_hotel_active_idx"),
            models.Index(fields=["user_email"], name="pricealert_email_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user_email} - {self.hotel.name} < ${self.target_price}"


class PriceHistory(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="price_history")
    platform = models.CharField(
        max_length=20,
        choices=Price.PLATFORM_CHOICES,
        db_index=True,
    )
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=Price.CURRENCY_CHOICES,
        default="ARS",
    )
    recorded_at = models.DateTimeField(db_index=True)
    is_lowest_30d = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Historial de Precio"
        verbose_name_plural = "Historial de Precios"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["hotel", "platform", "recorded_at"], name="pricehist_hotel_plat_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.hotel.name} - {self.platform}: ${self.price_per_night} ({self.recorded_at.date()})"
