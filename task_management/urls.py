from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from core.views import homee, no_permission
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tasks/", include("tasks.urls")),  # ---> Include __ tasks app __ urls
    path("users/", include("users.urls")),  # ---> Include __ users app __ urls
    path("", homee, name="Home"),
    path("no-permission/", no_permission, name="no-permission"),
] + debug_toolbar_urls()


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
