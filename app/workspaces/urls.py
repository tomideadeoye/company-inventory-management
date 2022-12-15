from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkSpaceViewSets

app_name = 'workspaces'

router = DefaultRouter()
router.register('', WorkSpaceViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
