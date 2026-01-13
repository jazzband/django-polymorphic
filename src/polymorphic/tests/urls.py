from django.contrib import admin
from django.urls import path, include
from .models import Model2C

urlpatterns = [
    path("admin/", admin.site.urls),
    path("examples/views", include("polymorphic.tests.examples.views.urls")),
]

try:
    import extra_views  # noqa: F401

    urlpatterns.append(
        path(
            "examples/integrations/extra_views/",
            include(
                "polymorphic.tests.examples.integrations.extra_views.urls", namespace="extra_views"
            ),
        )
    )
except ImportError:
    pass
