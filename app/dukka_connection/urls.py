from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MerchantViewSets

app_name = 'dukka_connection'

router = DefaultRouter()
router.register('', MerchantViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
