from rest_framework import serializers

from .models import Lead


class LeadSerializer(serializers.ModelSerializer):

    def validate_status(self, value):
        if value == Lead.Status.CONVERTED:
            raise serializers.ValidationError(
                "Use the lead conversion endpoint to convert a lead."
            )

        return value

    class Meta:
        model = Lead
        fields = [
            "id",
            "name",
            "company",
            "email",
            "phone",
            "source",
            "status",
            "assigned_to",
            "converted_customer",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "converted_customer",
            "created_at",
            "updated_at",
        ]
