from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TerminalViewSets, TerminalShipmentViewset, TerminalGroupViewset

app_name = 'tms'

router = DefaultRouter()

router.register('terminals', TerminalViewSets)
router.register('terminal_shipments', TerminalShipmentViewset)
router.register('terminal_group', TerminalGroupViewset)


urlpatterns = [
    path('', include(router.urls)),
]
