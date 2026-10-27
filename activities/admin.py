from django.contrib import admin

from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "deal",
        "type",
        "assigned_to",
        "completed",
        "due_date",
        "created_at",
    )
