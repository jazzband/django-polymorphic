from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet
from .filter_views import AnnotationTrainingViewSet

app_name = "drf"

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"annotations", AnnotationTrainingViewSet)

urlpatterns = router.urls
