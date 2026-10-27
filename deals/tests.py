
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer
from .models import Deal

User = get_user_model()


class DealAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="salesperson",
            password="TestPassword123!",
            role="SALESPERSON",
        )

        self.other_user = User.objects.create_user(
            username="other_salesperson",
            password="TestPassword123!",
            role="SALESPERSON",
        )

        self.client.force_authenticate(user=self.user)

        self.list_url = "/api/deals/"

        self.customer = Customer.objects.create(
            name="Priya Sharma",
            company="ABC Technologies",
            email="priya@example.com",
            phone="9876543210",
            created_by=self.user,
        )

        self.deal = Deal.objects.create(
            customer=self.customer,
            title="Website Development Project",
            description="Build a company website",
            amount="150000.00",
            stage=Deal.Stage.PROPOSAL,
            assigned_to=self.user,
        )

    def test_list_deals(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_deal(self):
        data = {
            "customer": self.customer.id,
            "title": "Mobile App Development",
            "description": "Develop a mobile application",
            "amount": "250000.00",
            "stage": "NEW",
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        deal = Deal.objects.get(title="Mobile App Development")
        self.assertEqual(deal.assigned_to, self.user)


    def test_salesperson_cannot_create_deal_for_inaccessible_customer(self):
        private_customer = Customer.objects.create(
            name="Private Customer",
            company="Private Company",
            email="private@example.com",
            phone="9876500000",
            created_by=self.other_user,
        )

        data = {
            "customer": private_customer.id,
            "title": "Unauthorized Deal",
            "description": "This deal should not be created",
            "amount": "50000.00",
            "stage": "NEW",
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Deal.objects.filter(title="Unauthorized Deal").exists()
        )


    def test_retrieve_deal(self):
        response = self.client.get(
            f"{self.list_url}{self.deal.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["title"],
            "Website Development Project",
        )

    def test_update_deal(self):
        response = self.client.patch(
            f"{self.list_url}{self.deal.id}/",
            {"amount": "175000.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.deal.refresh_from_db()
        self.assertEqual(str(self.deal.amount), "175000.00")


    def test_admin_can_delete_deal(self):
        admin = User.objects.create_superuser(
            username="deal_admin",
            email="deal_admin@example.com",
            password="TestPassword123!",
            role="ADMIN",
        )
        self.client.force_authenticate(user=admin)

        response = self.client.delete(
            f"{self.list_url}{self.deal.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Deal.objects.filter(id=self.deal.id).exists()
        )

    def test_sales_manager_can_delete_deal(self):
        manager = User.objects.create_user(
            username="deal_manager",
            email="deal_manager@example.com",
            password="TestPassword123!",
            role="SALES_MANAGER",
        )
        self.client.force_authenticate(user=manager)

        response = self.client.delete(
            f"{self.list_url}{self.deal.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Deal.objects.filter(id=self.deal.id).exists()
        )

    def test_salesperson_cannot_delete_deal(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"{self.list_url}{self.deal.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Deal.objects.filter(id=self.deal.id).exists()
        )


    def test_filter_deals_by_stage(self):
        response = self.client.get(
            self.list_url,
            {"stage": "PROPOSAL"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_search_deals(self):
        response = self.client.get(
            self.list_url,
            {"search": "Website Development"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_salesperson_cannot_access_another_users_deal(self):
        self.deal.assigned_to = self.other_user
        self.deal.save()

        response = self.client.get(
            f"{self.list_url}{self.deal.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_salesperson_cannot_reassign_deal(self):
        response = self.client.patch(
            f"{self.list_url}{self.deal.id}/",
            {"assigned_to": self.other_user.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.deal.refresh_from_db()
        self.assertEqual(self.deal.assigned_to, self.user)

    def test_unauthenticated_request_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
