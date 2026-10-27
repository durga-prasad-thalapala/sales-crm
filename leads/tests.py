
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Lead

User = get_user_model()


class LeadAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="salesperson",
            password="TestPassword123!",
            role="SALESPERSON",
        )

        self.client.force_authenticate(user=self.user)

        self.list_url = "/api/leads/"

        self.lead = Lead.objects.create(
            name="Priya Sharma",
            company="ABC Technologies",
            email="priya@example.com",
            phone="9876543210",
            source=Lead.Source.WEBSITE,
            status=Lead.Status.NEW,
            assigned_to=self.user,
        )

    def test_list_leads(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_lead(self):
        data = {
            "name": "Rahul Kumar",
            "company": "Tech Solutions",
            "email": "rahul@example.com",
            "phone": "9876543211",
            "source": "REFERRAL",
            "status": "NEW",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Lead.objects.filter(email="rahul@example.com").exists()
        )
        self.assertEqual(
            Lead.objects.get(email="rahul@example.com").assigned_to,
            self.user,
        )

    def test_retrieve_lead(self):
        response = self.client.get(f"{self.list_url}{self.lead.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Priya Sharma")

    def test_update_lead_status(self):
        response = self.client.patch(
            f"{self.list_url}{self.lead.id}/",
            {"status": "CONTACTED"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.CONTACTED)


    def test_cannot_set_converted_status_directly(self):
        response = self.client.patch(
            f"{self.list_url}{self.lead.id}/",
            {"status": "CONVERTED"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.NEW)
        self.assertIsNone(self.lead.converted_customer_id)



    def test_delete_lead(self):
        response = self.client.delete(f"{self.list_url}{self.lead.id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(Lead.objects.filter(id=self.lead.id).exists())

    def test_filter_leads_by_status(self):
        response = self.client.get(
            self.list_url,
            {"status": "NEW"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_leads_by_source(self):
        response = self.client.get(
            self.list_url,
            {"source": "WEBSITE"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_search_leads(self):
        response = self.client.get(
            self.list_url,
            {"search": "Priya"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_unauthenticated_request_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_convert_qualified_lead(self):
        self.lead.status = Lead.Status.QUALIFIED
        self.lead.save()

        response = self.client.post(
            f"{self.list_url}{self.lead.id}/convert/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.CONVERTED)
        self.assertIsNotNone(self.lead.converted_customer_id)

        self.assertEqual(
            self.lead.converted_customer.name,
            "Priya Sharma",
        )

    def test_cannot_convert_unqualified_lead(self):
        response = self.client.post(
            f"{self.list_url}{self.lead.id}/convert/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.NEW)
        self.assertIsNone(self.lead.converted_customer_id)

    def test_cannot_convert_lead_twice(self):
        self.lead.status = Lead.Status.QUALIFIED
        self.lead.save()

        first_response = self.client.post(
            f"{self.list_url}{self.lead.id}/convert/"
        )
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.post(
            f"{self.list_url}{self.lead.id}/convert/"
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_converted_customer_is_visible_to_assigned_salesperson(self):
        self.lead.status = Lead.Status.QUALIFIED
        self.lead.save()

        conversion_response = self.client.post(
            f"{self.list_url}{self.lead.id}/convert/"
        )

        self.assertEqual(
            conversion_response.status_code,
            status.HTTP_200_OK,
        )

        customer_id = conversion_response.data["customer_id"]

        customer_response = self.client.get("/api/customers/")

        self.assertEqual(
            customer_response.status_code,
            status.HTTP_200_OK,
        )

        visible_customer_ids = [
            customer["id"]
            for customer in customer_response.data["results"]
        ]

        self.assertIn(customer_id, visible_customer_ids)

    def test_salesperson_cannot_access_another_users_lead(self):
        another_user = User.objects.create_user(
            username="another_salesperson",
            password="TestPassword123!",
            role="SALESPERSON",
        )

        other_lead = Lead.objects.create(
            name="Private Lead",
            company="Private Company",
            email="private@example.com",
            phone="9876500000",
            source=Lead.Source.WEBSITE,
            status=Lead.Status.NEW,
            assigned_to=another_user,
        )

        response = self.client.get(
            f"{self.list_url}{other_lead.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_salesperson_cannot_reassign_lead(self):
        another_user = User.objects.create_user(
            username="reassignment_target",
            password="TestPassword123!",
            role="SALESPERSON",
        )

        response = self.client.patch(
            f"{self.list_url}{self.lead.id}/",
            {"assigned_to": another_user.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.lead.refresh_from_db()

        self.assertEqual(
            self.lead.assigned_to,
            self.user,
        )
