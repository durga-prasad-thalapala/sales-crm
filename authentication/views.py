from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .login_serializers import LoginSerializer
from .serializers import RegisterSerializer
from accounts.permissions import IsAdmin


class RegisterAPIView(APIView):

    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully.",
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginAPIView(TokenObtainPairView):

    serializer_class = LoginSerializer
