from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Price
from .services import HotelService

@receiver(post_save, sender=Price)
def update_hotel_min_price(sender, instance, created, **kwargs):
    HotelService.update_cached_min_price(instance.hotel_id)
