from .models import AiModelAnnotator, UserAnnotator, Annotator, Data
from rest_framework import serializers
from polymorphic.contrib.drf.serializers import PolymorphicSerializer


class AiModelAnnotatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiModelAnnotator
        fields = "__all__"


class UserAnnotatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnnotator
        fields = "__all__"


class AnnotatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotator
        fields = "__all__"


class AnnotatorPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Annotator: AnnotatorSerializer,
        AiModelAnnotator: AiModelAnnotatorSerializer,
        UserAnnotator: UserAnnotatorSerializer,
    }


class AnnotationSerializer(serializers.ModelSerializer):
    annotator = serializers.PrimaryKeyRelatedField(queryset=Annotator.objects.all())

    class Meta:
        model = Data
        fields = "__all__"
