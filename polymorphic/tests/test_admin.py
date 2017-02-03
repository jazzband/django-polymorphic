from django.contrib.admin import AdminSite
from django.test import TestCase

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from polymorphic.tests import Model2A, Model2B, Model2C, Model2D


class MultipleDatabasesTests(TestCase):

    def test_admin_registration(self):
        """
        Test how the registration works
        """
        class Model2Admin(PolymorphicParentModelAdmin):
            base_model = Model2A
            list_filter = (PolymorphicChildModelFilter,)
            child_models = (Model2B, Model2C, Model2D)

        class Model2ChildAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("Base fields", {
                    'fields': ('field1',)
                }),
            )

        admin_site = AdminSite()
        admin_site.register(Model2A, Model2Admin)
        admin_site.register(Model2B, Model2ChildAdmin)
        admin_site.register(Model2C, Model2ChildAdmin)
        admin_site.register(Model2D, Model2ChildAdmin)
