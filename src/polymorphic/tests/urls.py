from django.contrib import admin
from django.urls import path, include
from .models import Model2C

urlpatterns = [
    path("admin/", admin.site.urls),
    path("examples/views", include("polymorphic.tests.examples.views.urls")),
]
