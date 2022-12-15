from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AuthViewSets, CustomObtainTokenPairView, CreateTokenView)
from rest_framework_simplejwt.views import (TokenRefreshView, TokenVerifyView)

app_name = 'user'

router = DefaultRouter()
router.register('users', AuthViewSets)

urlpatterns = [
    path('login/', CustomObtainTokenPairView.as_view(), name='login'),
    path('', include(router.urls)),
]
