import uuid

from django.test import TestCase
from polymorphic.tests.models import (UUIDArtProject, UUIDProject,
                                      UUIDResearchProject)


class RegressionTests(TestCase):
    """
    https://github.com/django-polymorphic/django-polymorphic/issues/420
    """

    def test_unique_ids(self):
        UUIDProject.objects.create(
            uuid_primary_key=uuid.UUID('00000000-0000-0000-0000-000000000001')
        )
        UUIDArtProject.objects.create(
            uuid_primary_key=uuid.UUID('00000000-0000-0000-0000-000000000001')
        )
        UUIDResearchProject.objects.create(
            uuid_primary_key=uuid.UUID('00000000-0000-0000-0000-000000000001')
        )

        # works, print out:
        # [ <UUIDResearchProject: uuid_primary_key (UUIDField/pk)
        # "00000000-0000-0000..", topic (CharField) "", supervisor (CharField) "">
        # ]
        print(UUIDProject.objects.all())

        # polymorphic.models.PolymorphicTypeInvalid:
        # ContentType 70 for <class
        # 'polymorphic.tests.models.UUIDResearchProject'>
        # #00000000-0000-0000-0000-000000000001 does not point to a subclass!
        print(UUIDArtProject.objects.all())
        print(UUIDResearchProject.objects.all())
