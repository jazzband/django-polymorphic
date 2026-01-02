from _typeshed import Incomplete
from django_stubs.db import models

class BadModel(models.Model):
    instance_of: models.CharField
    not_instance_of: models.IntegerField
