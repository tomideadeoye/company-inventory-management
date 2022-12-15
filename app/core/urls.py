from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('api/v1/auth/', include('user.urls')),
    path("api/v1/workspace/", include("workspaces.urls")),
    path("api/v1/tms/", include("tms.urls")),
    path("api/v1/merchants/", include("dukka_connection.urls")),
]
