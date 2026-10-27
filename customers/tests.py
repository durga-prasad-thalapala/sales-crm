
from django.core.serializers import python
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from .models import Customer


class CustomerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="customer_test_user",
            email="customer_test@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.customer = Customer.objects.create(
            name="Test Customer",
            company="Test Company",
            email="customer@example.com",
            phone="9876543210",
            created_by=self.user,
        )

        self.list_url = "/api/customers/"
        self.detail_url = f"/api/customers/{self.customer.id}/"

    def test_list_customers(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_customer(self):
        payload = {
            "name": "New Customer",
            "company": "New Company",
            "email": "newcustomer@example.com",
            "phone": "9876501234",
            "address": "Test address",
        }

        response = self.client.post(
            self.list_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            Customer.objects.filter(
                email="newcustomer@example.com"
            ).exists()
        )

    def test_retrieve_customer(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Customer")

    def test_update_customer(self):
        response = self.client.patch(
            self.detail_url,
            {"name": "Updated Customer"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Updated Customer")


    def test_admin_can_delete_customer(self):
        admin = User.objects.create_superuser(
            username="customer_admin",
            email="admin@example.com",
            password="TestPassword123!",
            role="ADMIN",
        )

        self.client.force_authenticate(user=admin)

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Customer.objects.filter(id=self.customer.id).exists()
        )

    def test_sales_manager_can_delete_customer(self):
        manager = User.objects.create_user(
            username="customer_manager",
            email="manager@example.com",
            password="TestPassword123!",
            role="SALES_MANAGER",
        )
        self.client.force_authenticate(user=manager)

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Customer.objects.filter(id=self.customer.id).exists()
        )

    def test_salesperson_cannot_delete_customer(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Customer.objects.filter(id=self.customer.id).exists()
        )


    def test_unauthenticated_request_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )



    def test_salesperson_cannot_access_another_users_customer(self):
        another_user = User.objects.create_user(
            username="another_salesperson",
            email="another@example.com",
            password="TestPassword123!",
        )

        private_customer = Customer.objects.create(
            name="Private Customer",
            company="Private Company",
            email="private@example.com",
            phone="9876500000",
            created_by=another_user,
        )

        response = self.client.get(
            f"/api/customers/{private_customer.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_salesperson_cannot_see_another_users_customer_in_list(self):
        another_user = User.objects.create_user(
            username="another_salesperson_list",
            email="anotherlist@example.com",
            password="TestPassword123!",
        )

        Customer.objects.create(
            name="Private List Customer",
            company="Private List Company",
            email="privatelist@example.com",
            phone="9876500001",
            created_by=another_user,
        )

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        customer_names = [
            customer["name"]
            for customer in response.data["results"]
        ]

        self.assertNotIn(
            "Private List Customer",
            customer_names,
        )
