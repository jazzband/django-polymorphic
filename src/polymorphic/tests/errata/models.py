from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from django.db import models
from django.db.models import Manager
from django.db.models.query import QuerySet


class BadModel(PolymorphicModel):
    instance_of = models.CharField(max_length=100)
    not_instance_of = models.IntegerField()


class PolymorphicMigrationManager(PolymorphicManager):
    use_in_migrations = True


class OkMigrationManager(Manager):
    use_in_migrations = True


class GoodMigrationManager(PolymorphicModel):
    objects = PolymorphicManager()
    migration_manager = OkMigrationManager()


class BadMigrationManager(PolymorphicModel):
    objects = PolymorphicMigrationManager()


class BadManager(PolymorphicModel):
    objects = models.Manager()  # not polymorphic


class BadQuerySet(PolymorphicModel):
    default_objects = PolymorphicManager().from_queryset(QuerySet)
