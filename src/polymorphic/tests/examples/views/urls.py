from django.urls import path
from .views import ProjectTypeSelectView, ProjectCreateView

urlpatterns = [
    path("select/", ProjectTypeSelectView.as_view(), name="project-select"),
    path("create/", ProjectCreateView.as_view(), name="project-create"),
]
