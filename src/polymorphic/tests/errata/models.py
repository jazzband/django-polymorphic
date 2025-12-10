from django.db import models


class BadModel(models.Model):
    instance_of = models.CharField(max_length=100)
    not_instance_of = models.IntegerField()
