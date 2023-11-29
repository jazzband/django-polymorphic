from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"), permanent=False)),
]
