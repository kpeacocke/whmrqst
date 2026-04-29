from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", include("campaign.urls")),
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
]
