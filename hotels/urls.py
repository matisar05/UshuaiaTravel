from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, PriceViewSet

router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'prices', PriceViewSet, basename='price')

urlpatterns = [
    path('', include(router.urls)),
]
