
from rest_framework import serializers
from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    role = serializers.ChoiceField(
        choices=[
            (User.Role.SALESPERSON, "Salesperson"),
            (User.Role.SALES_MANAGER, "Sales Manager"),
        ],
        default=User.Role.SALESPERSON,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.pop("role", User.Role.SALESPERSON)

        user = User.objects.create_user(
            password=password,
            role=role,
            **validated_data,
        )

        return user
