from .filter_serializers import AnnotationSerializer
from .models import Data, AiModelAnnotator
from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
import django_filters


class DataFilterSet(django_filters.FilterSet):
    """FilterSet for Data model with polymorphic annotator filtering."""

    annotator__ai_model = django_filters.CharFilter(method="filter_by_ai_model")

    class Meta:
        model = Data
        fields = ["annotator"]

    def filter_by_ai_model(self, queryset, name, value):
        return queryset.filter(
            annotator__in=AiModelAnnotator.objects.filter(ai_model=value)
        )


class AnnotationTrainingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Data.objects.all()
    serializer_class = AnnotationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DataFilterSet

    # this does not work
    # filterset_fields = ["annotator", "annotator___AiModelAnnotator__ai_model"]
