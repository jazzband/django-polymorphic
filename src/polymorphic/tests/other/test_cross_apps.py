from django.test import TestCase
from django.core.exceptions import FieldError


class TestCrossAppSubclasses(TestCase):
    def test_samename_different_app_subclasses(self):
        from polymorphic.tests.other.models import UserProfile as OtherUserProfile
        from polymorphic.tests.models import Participant, UserProfile

        p1 = Participant.objects.create()
        p2 = UserProfile.objects.create(name="userprofile1")
        p3 = OtherUserProfile.objects.create(name="otheruserprofile1")

        assert set(Participant.objects.all()) == {p1, p2, p3}

        with self.assertRaises(FieldError):
            Participant.objects.filter(UserProfile___name="otheruserprofile1")

        assert set(Participant.objects.filter(other__UserProfile___name="otheruserprofile1")) == {
            p3
        }
