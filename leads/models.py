from django.conf import settings
from django.db import models


class Lead(models.Model):

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        CONTACTED = "CONTACTED", "Contacted"
        QUALIFIED = "QUALIFIED", "Qualified"
        CONVERTED = "CONVERTED", "Converted"
        LOST = "LOST", "Lost"

    class Source(models.TextChoices):
        WEBSITE = "WEBSITE", "Website"
        REFERRAL = "REFERRAL", "Referral"
        LINKEDIN = "LINKEDIN", "LinkedIn"
        EMAIL = "EMAIL", "Email"
        COLD_CALL = "COLD_CALL", "Cold Call"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=100)
    company = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.OTHER,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
    )


    converted_customer = models.OneToOneField(
    "customers.Customer",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="source_lead",
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
