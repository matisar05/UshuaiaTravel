import logging
from decimal import Decimal
from django.core.mail import send_mail
from .models import PriceAlert

logger = logging.getLogger(__name__)


def check_price_drops_and_notify(hotel_id: int, new_price: Decimal | float) -> None:
    alerts = PriceAlert.objects.filter(
        hotel_id=hotel_id,
        target_price__gte=new_price,
        is_active=True,
    )

    for alert in alerts:
        try:
            send_mail(
                subject="UshuaiaTravel - ¡Precio bajo!",
                message=f"El precio bajó a ${new_price}",
                from_email="alerts@ushuaia.travel",
                recipient_list=[alert.user_email],
            )
            alert.is_active = False
            alert.save()
        except Exception as e:
            logger.error(f"Failed to send price alert to {alert.user_email}: {e}")
