from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", include("conversations.urls")),
    # OpenAPI Schema (JSON)
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    # Redoc UI
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
