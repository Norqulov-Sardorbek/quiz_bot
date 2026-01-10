import requests
from shop.models import BillzToken
from django.utils import timezone
from decouple import config

def get_valid_token():
    token_obj = BillzToken.objects.last()

    # Agar token mavjud bo'lmasa → yangisini olish
    if not token_obj:
        return refresh_token_from_billz()

    # Token muddati tugaganmi?
    expires_in = token_obj.expires_in  # sekundlarda
    expiry_time = token_obj.created_datetime + timezone.timedelta(seconds=expires_in)

    if timezone.now() >= expiry_time:
        return refresh_token_from_billz()

    return token_obj.access_token


def refresh_token_from_billz():
    response = requests.post(
        "https://api-admin.billz.ai/v1/auth/login",
        json={
            "secret_token": config("BILLZ_SECRET_KEY")
        }
    )

    if response.status_code != 200:
        return None

    data = response.json().get("data", {})

    access_token = data.get("access_token")
    expires_in = data.get("expires_in", 3600)  # Default 1 hour

    # Saqlaymiz
    BillzToken.objects.create(
        access_token=access_token,
        expires_in=expires_in,
        created_datetime=timezone.now()
    )

    return access_token
