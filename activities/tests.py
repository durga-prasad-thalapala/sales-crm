
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer
from deals.models import Deal
from .models import Activity

User = get_user_model()


class ActivityAPITests(APITestCase):

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

        self.list_url = "/api/activities/"

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
            amount="150000.00",
            stage=Deal.Stage.PROPOSAL,
            assigned_to=self.user,
        )

        self.activity = Activity.objects.create(
            deal=self.deal,
            type=Activity.Type.CALL,
            title="Follow up with customer",
            description="Discuss project requirements",
            completed=False,
            assigned_to=self.user,
            created_by=self.user,
        )

    def test_list_activities(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_activity(self):
        data = {
            "deal": self.deal.id,
            "type": "MEETING",
            "title": "Project Discussion",
            "description": "Discuss project timeline",
            "completed": False,
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

        activity = Activity.objects.get(title="Project Discussion")
        self.assertEqual(activity.assigned_to, self.user)
        self.assertEqual(activity.created_by, self.user)

    def test_retrieve_activity(self):
        response = self.client.get(
            f"{self.list_url}{self.activity.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["title"],
            "Follow up with customer",
        )

    def test_update_activity(self):
        response = self.client.patch(
            f"{self.list_url}{self.activity.id}/",
            {"title": "Updated Follow-up"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.activity.refresh_from_db()
        self.assertEqual(self.activity.title, "Updated Follow-up")

    def test_mark_activity_completed(self):
        response = self.client.patch(
            f"{self.list_url}{self.activity.id}/",
            {"completed": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.activity.refresh_from_db()
        self.assertTrue(self.activity.completed)


    def test_admin_can_delete_activity(self):
        admin = User.objects.create_superuser(
            username="activity_admin",
            email="activity_admin@example.com",
            password="TestPassword123!",
            role="ADMIN",
        )
        self.client.force_authenticate(user=admin)

        response = self.client.delete(
            f"{self.list_url}{self.activity.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Activity.objects.filter(id=self.activity.id).exists()
        )

    def test_sales_manager_can_delete_activity(self):
        manager = User.objects.create_user(
            username="activity_manager",
            email="activity_manager@example.com",
            password="TestPassword123!",
            role="SALES_MANAGER",
        )
        self.client.force_authenticate(user=manager)

        response = self.client.delete(
            f"{self.list_url}{self.activity.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Activity.objects.filter(id=self.activity.id).exists()
        )

    def test_salesperson_cannot_delete_activity(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"{self.list_url}{self.activity.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Activity.objects.filter(id=self.activity.id).exists()
        )


    def test_filter_activities_by_type(self):
        response = self.client.get(
            self.list_url,
            {"type": "CALL"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_activities_by_completion(self):
        response = self.client.get(
            self.list_url,
            {"completed": "false"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_search_activities(self):
        response = self.client.get(
            self.list_url,
            {"search": "Follow up"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_salesperson_cannot_access_another_users_activity(self):
        self.activity.assigned_to = self.other_user
        self.activity.save()

        response = self.client.get(
            f"{self.list_url}{self.activity.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_salesperson_cannot_reassign_activity(self):
        response = self.client.patch(
            f"{self.list_url}{self.activity.id}/",
            {
                "assigned_to": self.other_user.id,
                "created_by": self.other_user.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.activity.refresh_from_db()
        self.assertEqual(self.activity.assigned_to, self.user)
        self.assertEqual(self.activity.created_by, self.user)

    def test_unauthenticated_request_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
