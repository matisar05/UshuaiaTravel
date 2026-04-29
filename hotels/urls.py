from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, PriceViewSet, health_check, create_price_alert, create_donation

router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'prices', PriceViewSet, basename='price')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('alerts/', create_price_alert, name='price-alert-create'),
    path('donations/', create_donation, name='donation-create'),
    path('', include(router.urls)),
]
