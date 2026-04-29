"""
MercadoPago Checkout Pro integration for donations.
Creates a payment preference and returns the init_point URL.
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SANDBOX_URL = "https://api.mercadopago.com/checkout/preferences"
PROD_URL = "https://api.mercadopago.com/checkout/preferences"


def create_donation_preference(amount: float, description: str = "Donación Ushuaia Travel",
                                payer_email: str = "") -> dict:
    access_token = settings.MERCADOPAGO_ACCESS_TOKEN
    if not access_token:
        raise ValueError("MERCADOPAGO_ACCESS_TOKEN no configurado")

    preference: dict = {
        "items": [
            {
                "title": description,
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(amount),
            }
        ],
    }

    back_url = settings.MERCADOPAGO_SUCCESS_URL
    if back_url and back_url.startswith("http"):
        preference["back_urls"] = {
            "success": back_url,
            "failure": back_url,
            "pending": back_url,
        }

    if payer_email:
        preference["payer"] = {"email": payer_email}

    resp = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        json=preference,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    logger.info(f"MercadoPago preference created: {data.get('id')}")
    return {
        "preference_id": data["id"],
        "init_point": data["init_point"],
        "sandbox_init_point": data.get("sandbox_init_point", data["init_point"]),
    }
