from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User


class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )

        self.admin = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
            role=User.Role.ADMIN,
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_invalid_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_register_creates_salesperson(self):
        self.client.force_authenticate(user=self.admin)


        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "NewPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )

        new_user = User.objects.get(username="newuser")

        self.assertEqual(
            new_user.role,
            User.Role.SALESPERSON,
        )



    def test_admin_can_register_sales_manager(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newmanager",
                "email": "manager@example.com",
                "password": "ManagerPassword123!",
                "role": "SALES_MANAGER",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        manager = User.objects.get(username="newmanager")

        self.assertEqual(
            manager.role,
            User.Role.SALES_MANAGER,
        )

        self.assertTrue(
            manager.check_password("ManagerPassword123!")
        )


    def test_anonymous_user_cannot_register(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "anonymoususer",
                "email": "anonymous@example.com",
                "password": "NewPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            User.objects.filter(username="anonymoususer").exists()
        )

    def test_salesperson_cannot_register(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "blockeduser",
                "email": "blocked@example.com",
                "password": "NewPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            User.objects.filter(username="blockeduser").exists()
        )


    def test_sales_manager_cannot_register(self):
        manager = User.objects.create_user(
            username="manageruser",
            email="manageruser@example.com",
            password="ManagerPassword123!",
            role=User.Role.SALES_MANAGER,
        )

        self.client.force_authenticate(user=manager)

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "blockedmanager",
                "email": "blockedmanager@example.com",
                "password": "NewPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            User.objects.filter(username="blockedmanager").exists()
        )



    def test_refresh_token_returns_new_access_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
            },
            format="json",
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)

    def test_refresh_token_rejects_invalid_token(self):
        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": "invalid-refresh-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_registration_cannot_create_admin(self):
        self.client.force_authenticate(user=self.admin)


        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "attempted_admin",
                "email": "attempted_admin@example.com",
                "password": "StrongPassword123!",
                "role": "ADMIN",
            },
            format="json",
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
        User.objects.filter(username="attempted_admin").exists()
        )



    def test_registration_rejects_invalid_role(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "invalidroleuser",
                "email": "invalidrole@example.com",
                "password": "StrongPassword123!",
                "role": "SUPERUSER",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User.objects.filter(username="invalidroleuser").exists()
        )


    def test_user_password_is_hashed(self):
        self.assertNotEqual(
            self.user.password,
            "TestPassword123!",
        )

        self.assertTrue(
            self.user.check_password("TestPassword123!")
        )