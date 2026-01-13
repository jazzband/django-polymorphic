from collections.abc import Mapping

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from rest_framework import serializers
from rest_framework.fields import empty


class PolymorphicSerializer(serializers.Serializer):
    model_serializer_mapping = None
    resource_type_field_name = "resourcetype"

    def __new__(cls, *args, **kwargs):
        if cls.model_serializer_mapping is None:
            raise ImproperlyConfigured(
                "`{cls}` is missing a `{cls}.model_serializer_mapping` attribute".format(
                    cls=cls.__name__
                )
            )
        if not isinstance(cls.resource_type_field_name, str):
            raise ImproperlyConfigured(
                "`{cls}.resource_type_field_name` must be a string".format(cls=cls.__name__)
            )
        return super(PolymorphicSerializer, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(PolymorphicSerializer, self).__init__(*args, **kwargs)

        model_serializer_mapping = self.model_serializer_mapping
        self.model_serializer_mapping = {}
        self.resource_type_model_mapping = {}

        for model, serializer in model_serializer_mapping.items():
            resource_type = self.to_resource_type(model)
            if callable(serializer):
                serializer = serializer(*args, **kwargs)
                serializer.parent = self

            self.resource_type_model_mapping[resource_type] = model
            self.model_serializer_mapping[model] = serializer

    # ----------
    # Public API

    def to_resource_type(self, model_or_instance):
        return model_or_instance._meta.object_name

    def to_representation(self, instance):
        if isinstance(instance, Mapping):
            resource_type = self._get_resource_type_from_mapping(instance)
            serializer = self._get_serializer_from_resource_type(resource_type)
        else:
            resource_type = self.to_resource_type(instance)
            serializer = self._get_serializer_from_model_or_instance(instance)

        ret = serializer.to_representation(instance)
        ret[self.resource_type_field_name] = resource_type
        return ret

    def to_internal_value(self, data):
        if self.partial and self.instance:
            resource_type = self.to_resource_type(self.instance)
            serializer = self._get_serializer_from_model_or_instance(self.instance)
        else:
            resource_type = self._get_resource_type_from_mapping(data)
            serializer = self._get_serializer_from_resource_type(resource_type)

        ret = serializer.to_internal_value(data)
        ret[self.resource_type_field_name] = resource_type
        return ret

    def create(self, validated_data):
        resource_type = validated_data.pop(self.resource_type_field_name)
        serializer = self._get_serializer_from_resource_type(resource_type)
        return serializer.create(validated_data)

    def update(self, instance, validated_data):
        resource_type = validated_data.pop(self.resource_type_field_name)
        serializer = self._get_serializer_from_resource_type(resource_type)
        return serializer.update(instance, validated_data)

    def is_valid(self, *args, **kwargs):
        valid = super(PolymorphicSerializer, self).is_valid(*args, **kwargs)
        try:
            if self.partial and self.instance:
                resource_type = self.to_resource_type(self.instance)
                serializer = self._get_serializer_from_model_or_instance(self.instance)
            else:
                resource_type = self._get_resource_type_from_mapping(self.initial_data)
                serializer = self._get_serializer_from_resource_type(resource_type)

        except serializers.ValidationError:
            child_valid = False
        else:
            child_valid = serializer.is_valid(*args, **kwargs)
            # Update parent's validated_data with child's validated_data
            # to preserve any modifications made in child's validate() method
            if child_valid and hasattr(self, "_validated_data"):
                self._validated_data.update(serializer._validated_data)
            self._errors.update(serializer.errors)
        return valid and child_valid

    def run_validation(self, data=empty):
        if self.partial and self.instance:
            resource_type = self.to_resource_type(self.instance)
            serializer = self._get_serializer_from_model_or_instance(self.instance)
        else:
            resource_type = self._get_resource_type_from_mapping(data)
            serializer = self._get_serializer_from_resource_type(resource_type)

        validated_data = serializer.run_validation(data)
        validated_data[self.resource_type_field_name] = resource_type
        return validated_data

    # --------------
    # Implementation

    def _to_model(self, model_or_instance):
        return (
            model_or_instance.__class__
            if isinstance(model_or_instance, models.Model)
            else model_or_instance
        )

    def _get_resource_type_from_mapping(self, mapping):
        try:
            return mapping[self.resource_type_field_name]
        except KeyError:
            raise serializers.ValidationError(
                {
                    self.resource_type_field_name: "This field is required",
                }
            )

    def _get_serializer_from_model_or_instance(self, model_or_instance):
        model = self._to_model(model_or_instance)

        for klass in model.mro():
            if klass in self.model_serializer_mapping:
                return self.model_serializer_mapping[klass]

        raise KeyError(
            "`{cls}.model_serializer_mapping` is missing "
            "a corresponding serializer for `{model}` model".format(
                cls=self.__class__.__name__, model=model.__name__
            )
        )

    def _get_serializer_from_resource_type(self, resource_type):
        try:
            model = self.resource_type_model_mapping[resource_type]
        except KeyError:
            raise serializers.ValidationError(
                {
                    self.resource_type_field_name: "Invalid {0}".format(
                        self.resource_type_field_name
                    )
                }
            )

        return self._get_serializer_from_model_or_instance(model)
