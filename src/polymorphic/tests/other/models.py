from polymorphic.tests.models import Participant
from django.db import models


class UserProfile(Participant):
    participant = models.OneToOneField(
        Participant, parent_link=True, on_delete=models.CASCADE, related_name="other_userprofile"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
