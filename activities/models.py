from django.conf import settings
from django.db import models

from deals.models import Deal


class Activity(models.Model):

    class Type(models.TextChoices):
        CALL = "CALL", "Call"
        EMAIL = "EMAIL", "Email"
        MEETING = "MEETING", "Meeting"
        NOTE = "NOTE", "Note"
        FOLLOW_UP = "FOLLOW_UP", "Follow-up"
        TASK = "TASK", "Task"

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    due_date = models.DateTimeField(null=True, blank=True)

    completed = models.BooleanField(default=False)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_activities",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_activities",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
