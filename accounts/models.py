from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SALES_MANAGER = "SALES_MANAGER", "Sales Manager"
        SALESPERSON = "SALESPERSON", "Salesperson"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SALESPERSON,
    )
