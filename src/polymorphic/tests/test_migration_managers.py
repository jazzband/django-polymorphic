from django.test import TestCase

from django_test_migrations.contrib.unittest_case import MigratorTestCase
from django_test_migrations.migrator import Migrator

from polymorphic.managers import PolymorphicManager


class TestRelatedManagersInMigrationState(MigratorTestCase):
    """
    Test that only non-polymorphic managers are used in migrations.
    """

    app = "tests"
    migrate_from = (app, None)
    migrate_to = (app, "0001_initial")

    def test_migration_managers_are_nonpoly(self):
        migrator = Migrator(database="default")

        # Apply migrations up to the state you care about and get the historical apps registry.
        state = migrator.apply_initial_migration(self.migrate_to)
        apps = state.apps

        ChildModelWithManager = apps.get_model("tests", "ChildModelWithManager")
        ParentModelWithManager = apps.get_model("tests", "ParentModelWithManager")
        pm = ParentModelWithManager.objects.create()
        ChildModelWithManager.objects.create(field1="test", fk=pm)

        assert not isinstance(ParentModelWithManager.objects, PolymorphicManager)
        assert not isinstance(ChildModelWithManager.objects, PolymorphicManager)
        assert not isinstance(ChildModelWithManager._meta.base_manager, PolymorphicManager)
        assert not isinstance(ParentModelWithManager._meta.base_manager, PolymorphicManager)
        assert not isinstance(pm.childmodel_set, PolymorphicManager)

        One2OneRelatingModel = apps.get_model("tests", "One2OneRelatingModel")
        One2OneRelatingModelDerived = apps.get_model("tests", "One2OneRelatingModelDerived")
        Model2A = apps.get_model("tests", "Model2A")
        Model2BFiltered = apps.get_model("tests", "Model2BFiltered")
        Model2CFiltered = apps.get_model("tests", "Model2CFiltered")
        Model2CNamedManagers = apps.get_model("tests", "Model2CNamedManagers")
        Model2CNamedDefault = apps.get_model("tests", "Model2CNamedDefault")
        ManagerTest = apps.get_model("tests", "ManagerTest")
        ManagerTestChild = apps.get_model("tests", "ManagerTestChild")
        RelatingModel = apps.get_model("tests", "RelatingModel")

        assert not isinstance(Model2BFiltered._meta.base_manager, PolymorphicManager)
        assert not isinstance(Model2CFiltered._meta.base_manager, PolymorphicManager)
        assert not isinstance(Model2CNamedManagers._meta.base_manager, PolymorphicManager)
        assert not isinstance(Model2CNamedDefault._meta.base_manager, PolymorphicManager)
        assert not isinstance(Model2BFiltered._meta.default_manager, PolymorphicManager)
        assert not isinstance(Model2CFiltered._meta.default_manager, PolymorphicManager)
        assert not isinstance(Model2CNamedManagers._meta.default_manager, PolymorphicManager)
        assert not isinstance(Model2CNamedDefault._meta.default_manager, PolymorphicManager)
        assert not isinstance(Model2BFiltered.objects, PolymorphicManager)
        assert not isinstance(Model2CFiltered.objects, PolymorphicManager)
        assert not isinstance(Model2CNamedManagers.objects, PolymorphicManager)
        assert not isinstance(Model2CNamedDefault.objects, PolymorphicManager)

        assert not isinstance(ManagerTest._meta.base_manager, PolymorphicManager)
        assert not isinstance(ManagerTest._meta.default_manager, PolymorphicManager)
        assert not isinstance(ManagerTestChild._meta.base_manager, PolymorphicManager)
        assert not isinstance(ManagerTestChild._meta.default_manager, PolymorphicManager)

        b2 = Model2BFiltered.objects.create(field1="testB1", field2="testB2")
        b2_2 = Model2BFiltered.objects.create(field1="testB12", field2="testB22")
        o2o1 = One2OneRelatingModel.objects.create(field1="relating1", one2one=b2)
        o2o2 = One2OneRelatingModelDerived.objects.create(
            field1="relating2", field2="relating2", one2one=b2_2
        )

        o2o1.refresh_from_db()
        o2o2.refresh_from_db()

        assert o2o1.one2one.__class__ is Model2A
        assert o2o2.one2one.__class__ is Model2A

        a2 = Model2A.objects.create(field1="testA1")

        rel = RelatingModel.objects.create()
        assert not isinstance(rel.many2many, PolymorphicManager)
        rel.many2many.add(b2)
        rel.many2many.add(b2_2)
        rel.many2many.add(a2)

        rel.refresh_from_db()
        assert set(rel.many2many.all()) == {
            Model2A.objects.get(pk=b2.pk),
            Model2A.objects.get(pk=b2_2.pk),
            a2,
        }
