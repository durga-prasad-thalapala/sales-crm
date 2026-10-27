from rest_framework import serializers

from .models import Deal


class DealSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deal
        fields = [
            "id",
            "customer",
            "title",
            "description",
            "amount",
            "stage",
            "expected_close_date",
            "assigned_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
