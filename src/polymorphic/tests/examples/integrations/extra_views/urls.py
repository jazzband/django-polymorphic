from django.urls import path
from .views import ArticleFormSetView

app_name = "extra_views"

urlpatterns = [
    path("articles/", ArticleFormSetView.as_view(), name="articles"),
]
