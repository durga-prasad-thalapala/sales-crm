from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "id",
            "deal",
            "type",
            "title",
            "description",
            "due_date",
            "completed",
            "assigned_to",
            "created_by",
            "created_at",
        ]
