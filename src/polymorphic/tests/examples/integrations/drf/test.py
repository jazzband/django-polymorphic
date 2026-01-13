from django.core.exceptions import ImproperlyConfigured

import pytest

try:
    from rest_framework import serializers
    from rest_framework.test import APIClient

    from polymorphic.contrib.drf.serializers import PolymorphicSerializer
    from .serializers import (
        BlogBaseSerializer,
        BlogOneSerializer,
        BlogPolymorphicSerializer,
    )

    from .models import (
        BlogBase,
        BlogOne,
        BlogTwo,
        Project,
        ArtProject,
        ResearchProject,
    )
except ImportError:
    pytest.skip("djangorestframework is not installed", allow_module_level=True)


pytestmark = pytest.mark.django_db


class TestPolymorphicSerializer:
    def test_model_serializer_mapping_is_none(self):
        class EmptyPolymorphicSerializer(PolymorphicSerializer):
            pass

        with pytest.raises(ImproperlyConfigured) as excinfo:
            EmptyPolymorphicSerializer()

        assert str(excinfo.value) == (
            "`EmptyPolymorphicSerializer` is missing a "
            "`EmptyPolymorphicSerializer.model_serializer_mapping` attribute"
        )

    def test_resource_type_field_name_is_not_string(self, mocker):
        class NotStringPolymorphicSerializer(PolymorphicSerializer):
            model_serializer_mapping = mocker.MagicMock
            resource_type_field_name = 1

        with pytest.raises(ImproperlyConfigured) as excinfo:
            NotStringPolymorphicSerializer()

        assert str(excinfo.value) == (
            "`NotStringPolymorphicSerializer.resource_type_field_name` must be a string"
        )

    def test_each_serializer_has_context(self, mocker):
        context = mocker.MagicMock()
        serializer = BlogPolymorphicSerializer(context=context)
        for inner_serializer in serializer.model_serializer_mapping.values():
            assert inner_serializer.context == context

    def test_non_callable_serializer_in_mapping(self):
        # Test the case where serializer is already instantiated (not callable)
        # This tests the else branch of the callable(serializer) check

        # Create an already-instantiated serializer
        blog_base_serializer_instance = BlogBaseSerializer()

        class TestPolymorphicSerializer(PolymorphicSerializer):
            model_serializer_mapping = {
                BlogBase: blog_base_serializer_instance,  # Already an instance
                BlogOne: BlogOneSerializer,  # Still a class (callable)
            }

        serializer = TestPolymorphicSerializer()

        # The instance should be used directly without re-instantiation
        assert serializer.model_serializer_mapping[BlogBase] is blog_base_serializer_instance

        # The callable should be instantiated
        assert isinstance(serializer.model_serializer_mapping[BlogOne], BlogOneSerializer)
        assert serializer.model_serializer_mapping[BlogOne] is not BlogOneSerializer

        # Both should be in resource_type_model_mapping
        assert serializer.resource_type_model_mapping["BlogBase"] == BlogBase
        assert serializer.resource_type_model_mapping["BlogOne"] == BlogOne

        # Now test that serialization actually works with the non-callable serializer
        base_instance = BlogBase.objects.create(name="base", slug="base-slug")
        one_instance = BlogOne.objects.create(name="one", slug="one-slug", info="info")

        # Serialize BlogBase (using the pre-instantiated serializer)
        base_serializer = TestPolymorphicSerializer(base_instance)
        base_data = base_serializer.data
        assert base_data == {
            "name": "base",
            "slug": "base-slug",
            "resourcetype": "BlogBase",
        }

        # Serialize BlogOne (using the callable serializer that was instantiated)
        one_serializer = TestPolymorphicSerializer(one_instance)
        one_data = one_serializer.data
        assert one_data == {
            "name": "one",
            "slug": "one-slug",
            "info": "info",
            "resourcetype": "BlogOne",
        }

        # Test serialization of multiple instances (many=True)
        instances = [base_instance, one_instance]
        many_serializer = TestPolymorphicSerializer(instances, many=True)
        many_data = many_serializer.data
        assert len(many_data) == 2
        assert many_data[0]["resourcetype"] == "BlogBase"
        assert many_data[1]["resourcetype"] == "BlogOne"
        assert many_data[0]["name"] == "base"
        assert many_data[1]["name"] == "one"
        assert many_data[1]["info"] == "info"

    def test_serialize(self):
        instance = BlogBase.objects.create(name="blog", slug="blog")
        serializer = BlogPolymorphicSerializer(instance)
        assert serializer.data == {
            "name": "blog",
            "slug": "blog",
            "resourcetype": "BlogBase",
        }

    def test_deserialize(self):
        data = {
            "name": "blog",
            "slug": "blog",
            "resourcetype": "BlogBase",
        }
        serializers = BlogPolymorphicSerializer(data=data)
        assert serializers.is_valid()
        assert serializers.data == data

    def test_deserialize_with_invalid_resourcetype(self):
        data = {
            "name": "blog",
            "resourcetype": "Invalid",
        }
        serializers = BlogPolymorphicSerializer(data=data)
        assert not serializers.is_valid()

    def test_create(self):
        data = [
            {"name": "a", "slug": "a", "resourcetype": "BlogBase"},
            {"name": "b", "slug": "b", "info": "info", "resourcetype": "BlogOne"},
            {"name": "c", "slug": "c", "resourcetype": "BlogTwo"},
        ]
        serializer = BlogPolymorphicSerializer(data=data, many=True)
        assert serializer.is_valid()

        instances = serializer.save()
        assert len(instances) == 3
        assert [item.name for item in instances] == ["a", "b", "c"]

        assert BlogBase.objects.count() == 3
        assert BlogBase.objects.instance_of(BlogOne).count() == 1
        assert BlogBase.objects.instance_of(BlogTwo).count() == 1

        assert serializer.data == data

    def test_update(self):
        instance = BlogBase.objects.create(name="blog", slug="blog")
        data = {"name": "new-blog", "slug": "blog", "resourcetype": "BlogBase"}

        serializer = BlogPolymorphicSerializer(instance, data=data)
        assert serializer.is_valid()

        serializer.save()
        assert instance.name == "new-blog"
        assert instance.slug == "blog"

    def test_partial_update(self):
        instance = BlogBase.objects.create(name="blog", slug="blog")
        data = {"name": "new-blog", "resourcetype": "BlogBase"}

        serializer = BlogPolymorphicSerializer(instance, data=data, partial=True)
        assert serializer.is_valid()

        serializer.save()
        assert instance.name == "new-blog"
        assert instance.slug == "blog"

    def test_partial_update_without_resourcetype(self):
        instance = BlogBase.objects.create(name="blog", slug="blog")
        data = {"name": "new-blog"}

        serializer = BlogPolymorphicSerializer(instance, data=data, partial=True)
        assert serializer.is_valid()

        serializer.save()
        assert instance.name == "new-blog"
        assert instance.slug == "blog"

    def test_object_validators_are_applied(self):
        data = {
            "name": "test-blog",
            "slug": "test-blog-slug",
            "info": "test-blog-info",
            "about": "test-blog-about",
            "resourcetype": "BlogThree",
        }
        serializer = BlogPolymorphicSerializer(data=data)
        assert serializer.is_valid()
        serializer.save()

        data["slug"] = "test-blog-slug-new"
        duplicate = BlogPolymorphicSerializer(data=data)

        assert not duplicate.is_valid()
        assert "non_field_errors" in duplicate.errors
        err = duplicate.errors["non_field_errors"]

        assert err == ["The fields info, about must make a unique set."]

    def test_to_internal_value_with_valid_data(self):
        data = {
            "name": "blog",
            "slug": "blog",
            "resourcetype": "BlogBase",
        }
        serializer = BlogPolymorphicSerializer(data=data)
        internal_value = serializer.to_internal_value(data)

        assert internal_value["name"] == "blog"
        assert internal_value["slug"] == "blog"
        assert internal_value["resourcetype"] == "BlogBase"

    def test_to_internal_value_with_missing_resourcetype(self):
        from rest_framework.exceptions import ValidationError

        data = {
            "name": "blog",
            "slug": "blog",
        }
        serializer = BlogPolymorphicSerializer(data=data)

        with pytest.raises(ValidationError) as excinfo:
            serializer.to_internal_value(data)

        assert "resourcetype" in excinfo.value.detail
        assert excinfo.value.detail["resourcetype"] == "This field is required"

    def test_to_internal_value_with_partial_update(self):
        instance = BlogBase.objects.create(name="blog", slug="blog")
        data = {"name": "new-blog"}

        serializer = BlogPolymorphicSerializer(instance, data=data, partial=True)
        internal_value = serializer.to_internal_value(data)

        assert internal_value["name"] == "new-blog"
        assert internal_value["resourcetype"] == "BlogBase"

    def test_get_serializer_from_model_or_instance_raises_keyerror(self):
        from polymorphic.models import PolymorphicModel

        # Create a model that is not in the mapping
        class UnmappedModel(PolymorphicModel):
            class Meta:
                app_label = "drf"

        serializer = BlogPolymorphicSerializer()

        with pytest.raises(KeyError) as excinfo:
            serializer._get_serializer_from_model_or_instance(UnmappedModel)

        assert "model_serializer_mapping" in str(excinfo.value)
        assert "UnmappedModel" in str(excinfo.value)

    def test_get_serializer_from_resource_type_keyerror_propagation(self):
        # This tests the case where _get_serializer_from_resource_type
        # successfully finds a resource_type in the mapping, but then
        # _get_serializer_from_model_or_instance raises a KeyError
        # when trying to find the serializer for that model.
        #
        # However, looking at the code, this scenario is actually not possible
        # in normal operation because resource_type_model_mapping and
        # model_serializer_mapping are populated together in __init__.
        #
        # The KeyError in _get_serializer_from_resource_type would only
        # occur if the resource_type is not in resource_type_model_mapping,
        # which is already caught and converted to ValidationError at line 149.
        #
        # So we'll test that the ValidationError is raised properly instead.
        from rest_framework.exceptions import ValidationError

        data = {
            "name": "blog",
            "slug": "blog",
            "resourcetype": "InvalidResourceType",
        }
        serializer = BlogPolymorphicSerializer(data=data)

        with pytest.raises(ValidationError) as excinfo:
            serializer._get_serializer_from_resource_type("InvalidResourceType")

        assert "resourcetype" in excinfo.value.detail
        assert "Invalid resourcetype" in str(excinfo.value.detail["resourcetype"])

    def test_validate_method_modifications_are_preserved(self):
        """Test that modifications made in child serializer's validate() method are preserved."""
        # Track whether the extra_field was present during create
        created_with_extra_field = []

        # Create a custom serializer that adds a field in validate()
        class CustomBlogOneSerializer(BlogOneSerializer):
            extra_field = serializers.CharField(required=False, allow_null=True)

            class Meta(BlogOneSerializer.Meta):
                fields = BlogOneSerializer.Meta.fields + ("extra_field",)

            def validate(self, attrs):
                attrs = super().validate(attrs)
                # Simulate adding data in validate(), like adding the current user
                attrs["extra_field"] = "added_in_validate"
                return attrs

            def create(self, validated_data):
                # Record whether extra_field was in validated_data
                created_with_extra_field.append("extra_field" in validated_data)
                # Remove extra_field before creating the model instance
                validated_data.pop("extra_field", None)
                return super().create(validated_data)

        class CustomBlogPolymorphicSerializer(PolymorphicSerializer):
            model_serializer_mapping = {
                BlogBase: BlogBaseSerializer,
                BlogOne: CustomBlogOneSerializer,
            }

        # Create data without the extra_field
        data = {
            "name": "test",
            "slug": "test-slug",
            "info": "test-info",
            "resourcetype": "BlogOne",
        }

        serializer = CustomBlogPolymorphicSerializer(data=data)
        assert serializer.is_valid(), f"Validation errors: {serializer.errors}"

        # Verify that the extra_field added in validate() is in validated_data
        assert "extra_field" in serializer.validated_data
        assert serializer.validated_data["extra_field"] == "added_in_validate"

        # Verify that resource_type field is still preserved in parent's validated_data
        assert "resourcetype" in serializer.validated_data
        assert serializer.validated_data["resourcetype"] == "BlogOne"

        # Save and verify that the field was present during create
        # Note: This would fail before the fix because the parent's _validated_data
        # wasn't updated with the child's _validated_data after calling child.is_valid()
        instance = serializer.save()

        # Verify that extra_field was indeed present when create() was called
        assert created_with_extra_field == [True], (
            "extra_field should have been in validated_data when create() was called"
        )

        # Verify the instance was created successfully
        assert instance.name == "test"
        assert instance.slug == "test-slug"
        assert instance.info == "test-info"


class TestProjectViewSet:
    """Test the example Project ViewSet with polymorphic serializers."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def base_project(self):
        return Project.objects.create(topic="General Project")

    @pytest.fixture
    def art_project(self):
        return ArtProject.objects.create(topic="Art", artist="Picasso")

    @pytest.fixture
    def research_project(self):
        return ResearchProject.objects.create(topic="Research", supervisor="Dr. Smith")

    def test_list_projects(self, client, base_project, art_project, research_project):
        response = client.get("/examples/integrations/drf/projects/")
        assert response.status_code == 200
        assert len(response.data) == 3

        topics = {item["topic"] for item in response.data}
        assert topics == {"General Project", "Art", "Research"}

    def test_retrieve_base_project(self, client, base_project):
        response = client.get(f"/examples/integrations/drf/projects/{base_project.pk}/")
        assert response.status_code == 200
        assert response.data["topic"] == "General Project"
        assert response.data["resourcetype"] == "Project"

    def test_retrieve_art_project(self, client, art_project):
        response = client.get(f"/examples/integrations/drf/projects/{art_project.pk}/")
        assert response.status_code == 200
        assert response.data["topic"] == "Art"
        assert response.data["artist"] == "Picasso"
        assert response.data["resourcetype"] == "ArtProject"
        assert "url" in response.data

    def test_retrieve_research_project(self, client, research_project):
        response = client.get(f"/examples/integrations/drf/projects/{research_project.pk}/")
        assert response.status_code == 200
        assert response.data["topic"] == "Research"
        assert response.data["supervisor"] == "Dr. Smith"
        assert response.data["resourcetype"] == "ResearchProject"

    def test_create_base_project(self, client):
        data = {"topic": "New Project", "resourcetype": "Project"}
        response = client.post("/examples/integrations/drf/projects/", data, format="json")
        assert response.status_code == 201
        assert response.data["topic"] == "New Project"
        assert response.data["resourcetype"] == "Project"

        assert Project.objects.count() == 1
        project = Project.objects.first()
        assert project.topic == "New Project"
        assert type(project) is Project

    def test_create_art_project(self, client):
        data = {
            "topic": "Sculpture",
            "artist": "Michelangelo",
            "resourcetype": "ArtProject",
        }
        response = client.post("/examples/integrations/drf/projects/", data, format="json")
        assert response.status_code == 201
        assert response.data["topic"] == "Sculpture"
        assert response.data["artist"] == "Michelangelo"
        assert response.data["resourcetype"] == "ArtProject"
        assert "url" in response.data

        assert Project.objects.count() == 1
        project = Project.objects.first()
        assert isinstance(project, ArtProject)
        assert project.artist == "Michelangelo"

    def test_create_research_project(self, client):
        data = {
            "topic": "AI Research",
            "supervisor": "Dr. Johnson",
            "resourcetype": "ResearchProject",
        }
        response = client.post("/examples/integrations/drf/projects/", data, format="json")
        assert response.status_code == 201
        assert response.data["topic"] == "AI Research"
        assert response.data["supervisor"] == "Dr. Johnson"
        assert response.data["resourcetype"] == "ResearchProject"

        assert Project.objects.count() == 1
        project = Project.objects.first()
        assert isinstance(project, ResearchProject)
        assert project.supervisor == "Dr. Johnson"

    def test_update_project(self, client, base_project):
        data = {"topic": "Updated Project", "resourcetype": "Project"}
        response = client.put(
            f"/examples/integrations/drf/projects/{base_project.pk}/", data, format="json"
        )
        assert response.status_code == 200
        assert response.data["topic"] == "Updated Project"

        base_project.refresh_from_db()
        assert base_project.topic == "Updated Project"

    def test_partial_update_art_project(self, client, art_project):
        data = {"artist": "Van Gogh"}
        response = client.patch(
            f"/examples/integrations/drf/projects/{art_project.pk}/", data, format="json"
        )
        assert response.status_code == 200
        assert response.data["artist"] == "Van Gogh"
        assert response.data["topic"] == "Art"  # unchanged

        art_project.refresh_from_db()
        assert art_project.artist == "Van Gogh"
        assert art_project.topic == "Art"

    def test_partial_update_research_project(self, client, research_project):
        data = {"supervisor": "Dr. Williams"}
        response = client.patch(
            f"/examples/integrations/drf/projects/{research_project.pk}/", data, format="json"
        )
        assert response.status_code == 200
        assert response.data["supervisor"] == "Dr. Williams"
        assert response.data["topic"] == "Research"  # unchanged

        research_project.refresh_from_db()
        assert research_project.supervisor == "Dr. Williams"
        assert research_project.topic == "Research"

    def test_delete_project(self, client, base_project):
        project_id = base_project.pk
        response = client.delete(f"/examples/integrations/drf/projects/{project_id}/")
        assert response.status_code == 204

        assert not Project.objects.filter(pk=project_id).exists()

    def test_create_with_invalid_resourcetype(self, client):
        data = {"topic": "Test", "resourcetype": "InvalidType"}
        response = client.post("/examples/integrations/drf/projects/", data, format="json")
        assert response.status_code == 400


class TestDjangoFiltersViewSet:
    """Test django-filter integration with polymorphic models (issue #520)."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def user(self, django_user_model):
        return django_user_model.objects.create_user(username="testuser", password="testpass")

    @pytest.fixture
    def user_annotator(self, user):
        from .models import UserAnnotator

        return UserAnnotator.objects.create(user=user)

    @pytest.fixture
    def ai_annotator_gpt4(self):
        from .models import AiModelAnnotator

        return AiModelAnnotator.objects.create(ai_model="gpt-4", version="1.0")

    @pytest.fixture
    def ai_annotator_claude(self):
        from .models import AiModelAnnotator

        return AiModelAnnotator.objects.create(ai_model="claude-3", version="2.0")

    @pytest.fixture
    def data_by_user(self, user_annotator):
        from .models import Data

        return Data.objects.create(annotator=user_annotator)

    @pytest.fixture
    def data_by_gpt4(self, ai_annotator_gpt4):
        from .models import Data

        return Data.objects.create(annotator=ai_annotator_gpt4)

    @pytest.fixture
    def data_by_claude(self, ai_annotator_claude):
        from .models import Data

        return Data.objects.create(annotator=ai_annotator_claude)

    def test_list_all_annotations(self, client, data_by_user, data_by_gpt4, data_by_claude):
        """Test listing all annotation data without filters."""
        response = client.get("/examples/integrations/drf/annotations/")
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_filter_by_annotator(self, client, data_by_user, data_by_gpt4, ai_annotator_gpt4):
        """Test filtering by annotator ID."""
        response = client.get(
            f"/examples/integrations/drf/annotations/?annotator={ai_annotator_gpt4.pk}"
        )
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == data_by_gpt4.pk

    def test_filter_by_ai_model(self, client, data_by_user, data_by_gpt4, data_by_claude):
        """Test filtering by annotator__ai_model field (issue #520)."""
        # This is the key test - filtering by a field on the polymorphic child model
        response = client.get("/examples/integrations/drf/annotations/?annotator__ai_model=gpt-4")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == data_by_gpt4.pk

    def test_filter_by_different_ai_model(
        self, client, data_by_user, data_by_gpt4, data_by_claude
    ):
        """Test filtering by a different AI model."""
        response = client.get(
            "/examples/integrations/drf/annotations/?annotator__ai_model=claude-3"
        )
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == data_by_claude.pk

    def test_filter_by_nonexistent_ai_model(
        self, client, data_by_user, data_by_gpt4, data_by_claude
    ):
        """Test filtering by an AI model that doesn't exist."""
        response = client.get(
            "/examples/integrations/drf/annotations/?annotator__ai_model=nonexistent"
        )
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_filter_excludes_non_ai_annotators(
        self, client, data_by_user, data_by_gpt4, data_by_claude
    ):
        """Test that filtering by ai_model excludes UserAnnotator instances."""
        # When filtering by annotator__ai_model, only AiModelAnnotator results should be returned
        # UserAnnotator doesn't have ai_model field, so data_by_user should not appear
        response = client.get("/examples/integrations/drf/annotations/?annotator__ai_model=gpt-4")
        assert response.status_code == 200
        assert len(response.data) == 1
        # Verify the user-annotated data is not in results
        assert all(item["id"] != data_by_user.pk for item in response.data)

    def test_retrieve_annotation(self, client, data_by_gpt4):
        """Test retrieving a single annotation."""
        response = client.get(f"/examples/integrations/drf/annotations/{data_by_gpt4.pk}/")
        assert response.status_code == 200
        assert response.data["id"] == data_by_gpt4.pk

    def test_create_annotation_with_user_annotator(self, client, user_annotator):
        """Test creating annotation data with a UserAnnotator."""
        data = {"annotator": user_annotator.pk}
        response = client.post("/examples/integrations/drf/annotations/", data, format="json")
        assert response.status_code == 201
        assert response.data["annotator"] == user_annotator.pk

        from .models import Data

        assert Data.objects.count() == 1
        created = Data.objects.first()
        assert created.annotator.pk == user_annotator.pk

    def test_create_annotation_with_ai_annotator(self, client, ai_annotator_gpt4):
        """Test creating annotation data with an AiModelAnnotator."""
        data = {"annotator": ai_annotator_gpt4.pk}
        response = client.post("/examples/integrations/drf/annotations/", data, format="json")
        assert response.status_code == 201
        assert response.data["annotator"] == ai_annotator_gpt4.pk

        from .models import Data

        assert Data.objects.count() == 1
        created = Data.objects.first()
        assert created.annotator.pk == ai_annotator_gpt4.pk
