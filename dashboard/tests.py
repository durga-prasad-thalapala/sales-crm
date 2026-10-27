
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer
from leads.models import Lead
from deals.models import Deal
from activities.models import Activity

User = get_user_model()


class DashboardAPITests(APITestCase):

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
        self.dashboard_url = "/api/dashboard/"

        self.customer = Customer.objects.create(
            name="Priya Sharma",
            company="ABC Technologies",
            email="priya@example.com",
            phone="9876543210",
            created_by=self.user,
        )

        self.lead = Lead.objects.create(
            name="Rahul Kumar",
            company="Tech Solutions",
            email="rahul@example.com",
            phone="9876543211",
            status=Lead.Status.CONVERTED,
            assigned_to=self.user,
        )

        self.open_deal = Deal.objects.create(
            customer=self.customer,
            title="Open Project",
            amount=Decimal("150000.00"),
            stage=Deal.Stage.PROPOSAL,
            assigned_to=self.user,
        )

        self.won_deal = Deal.objects.create(
            customer=self.customer,
            title="Won Project",
            amount=Decimal("50000.00"),
            stage=Deal.Stage.WON,
            assigned_to=self.user,
        )

        self.lost_deal = Deal.objects.create(
            customer=self.customer,
            title="Lost Project",
            amount=Decimal("25000.00"),
            stage=Deal.Stage.LOST,
            assigned_to=self.user,
        )

        self.completed_activity = Activity.objects.create(
            deal=self.open_deal,
            type=Activity.Type.CALL,
            title="Completed Call",
            completed=True,
            assigned_to=self.user,
            created_by=self.user,
        )

        self.pending_activity = Activity.objects.create(
            deal=self.open_deal,
            type=Activity.Type.TASK,
            title="Pending Task",
            completed=False,
            assigned_to=self.user,
            created_by=self.user,
        )

    def test_dashboard_summary_structure(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            set(response.data.keys()),
            {"leads", "customers", "deals", "activities"},
        )

    def test_lead_metrics(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.data["leads"]["total"], 1)
        self.assertEqual(response.data["leads"]["converted"], 1)

    def test_customer_metrics(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.data["customers"]["total"], 1)

    def test_deal_metrics_and_pipeline_value(self):
        response = self.client.get(self.dashboard_url)

        deals = response.data["deals"]

        self.assertEqual(deals["total"], 3)
        self.assertEqual(deals["open"], 1)
        self.assertEqual(deals["won"], 1)
        self.assertEqual(deals["lost"], 1)
        self.assertEqual(
            Decimal(str(deals["pipeline_value"])),
            Decimal("150000.00"),
        )

    def test_activity_metrics(self):
        response = self.client.get(self.dashboard_url)

        activities = response.data["activities"]

        self.assertEqual(activities["total"], 2)
        self.assertEqual(activities["completed"], 1)
        self.assertEqual(activities["pending"], 1)

    def test_salesperson_sees_only_assigned_data(self):
        other_customer = Customer.objects.create(
            name="Other Customer",
            company="Other Company",
            email="other@example.com",
            phone="9876543212",
            created_by=self.other_user,
        )

        Lead.objects.create(
            name="Other Lead",
            company="Other Company",
            email="otherlead@example.com",
            phone="9876543213",
            assigned_to=self.other_user,
        )

        Deal.objects.create(
            customer=other_customer,
            title="Other Deal",
            amount=Decimal("90000.00"),
            assigned_to=self.other_user,
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["leads"]["total"], 1)
        self.assertEqual(response.data["customers"]["total"], 1)
        self.assertEqual(response.data["deals"]["total"], 3)
        self.assertEqual(response.data["activities"]["total"], 2)

    def test_unauthenticated_request_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_sales_manager_sees_all_data(self):
        manager = User.objects.create_user(
            username="dashboard_manager",
            password="TestPassword123!",
            role="SALES_MANAGER",
        )
        self.client.force_authenticate(user=manager)

        other_customer = Customer.objects.create(
            name="Other Customer",
            company="Other Company",
            email="other@example.com",
            phone="9876543212",
            created_by=self.other_user,
        )

        Lead.objects.create(
            name="Other Lead",
            company="Other Company",
            email="otherlead@example.com",
            phone="9876543213",
            assigned_to=self.other_user,
        )

        Deal.objects.create(
            customer=other_customer,
            title="Other Deal",
            amount=Decimal("90000.00"),
            assigned_to=self.other_user,
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["leads"]["total"], 2)
        self.assertEqual(response.data["customers"]["total"], 2)
        self.assertEqual(response.data["deals"]["total"], 4)
        self.assertEqual(response.data["activities"]["total"], 2)
