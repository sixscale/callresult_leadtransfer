from django.db import models


class CRMContact(models.Model):
    contact_id = models.IntegerField()
    phone = models.CharField(max_length=255)
