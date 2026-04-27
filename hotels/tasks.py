from django.core.mail import send_mail
from .models import Hotel, PriceAlert

def check_price_drops_and_notify(hotel_id, new_price):
    alerts = PriceAlert.objects.filter(
        hotel_id=hotel_id,
        target_price__gte=new_price,
        is_active=True
    )
    
    for alert in alerts:
        send_mail(
            subject="UshuaiaTravel",
            message=str(new_price),
            from_email="alerts@ushuaia.travel",
            recipient_list=[alert.user_email],
        )
        alert.is_active = False
        alert.save()
