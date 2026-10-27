from django.contrib import admin

from .models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "customer",
        "amount",
        "stage",
        "assigned_to",
        "expected_close_date",
        "created_at",
    )
