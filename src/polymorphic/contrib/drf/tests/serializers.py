from rest_framework import serializers

from rest_polymorphic.serializers import PolymorphicSerializer

from tests.models import BlogBase, BlogOne, BlogTwo


class BlogBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogBase
        fields = ('name', )


class BlogOneSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogOne
        fields = ('name', 'info', )


class BlogTwoSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogTwo
        fields = ('name', )


class BlogPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        BlogBase: BlogBaseSerializer,
        BlogOne: BlogOneSerializer,
        BlogTwo: BlogTwoSerializer
    }
