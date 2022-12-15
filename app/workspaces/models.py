from django.db import models

from core.models import AuditableModel
from .enums import WORKSPACE_STATUS


class WorkSpace(AuditableModel):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    state_or_province = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=WORKSPACE_STATUS, default='ACTIVE')
    is_active = models.BooleanField(default=True)


    class Meta:
            ordering = ('name',)

    def __str__(self):
        return self.name
