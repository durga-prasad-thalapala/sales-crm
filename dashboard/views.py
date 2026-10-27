
from django.db import models
from django.db.models import Sum

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSalespersonOrAbove
from customers.models import Customer
from leads.models import Lead
from deals.models import Deal
from activities.models import Activity


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get(self, request):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            leads = Lead.objects.all()
            customers = Customer.objects.all()
            deals = Deal.objects.all()
            activities = Activity.objects.all()

        else:
            leads = Lead.objects.filter(
                assigned_to=request.user
            )

            deals = Deal.objects.filter(
                assigned_to=request.user
            )

            activities = Activity.objects.filter(
                assigned_to=request.user
            )

            customers = Customer.objects.filter(
                models.Q(deals__assigned_to=request.user)
                | models.Q(created_by=request.user)
            ).distinct()

        # Lead metrics
        total_leads = leads.count()

        converted_leads = leads.filter(
            status=Lead.Status.CONVERTED
        ).count()

        # Customer metrics
        total_customers = customers.count()

        # Deal metrics
        total_deals = deals.count()

        won_deals = deals.filter(
            stage=Deal.Stage.WON
        ).count()

        lost_deals = deals.filter(
            stage=Deal.Stage.LOST
        ).count()

        open_deals = deals.exclude(
            stage__in=[
                Deal.Stage.WON,
                Deal.Stage.LOST,
            ]
        ).count()

        pipeline_value = deals.exclude(
            stage__in=[
                Deal.Stage.WON,
                Deal.Stage.LOST,
            ]
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        # Activity metrics
        total_activities = activities.count()

        completed_activities = activities.filter(
            completed=True
        ).count()

        pending_activities = activities.filter(
            completed=False
        ).count()

        return Response({
            "leads": {
                "total": total_leads,
                "converted": converted_leads,
            },
            "customers": {
                "total": total_customers,
            },
            "deals": {
                 "total": total_deals,
                "open": open_deals,
                "won": won_deals,
                "lost": lost_deals,
                "pipeline_value": pipeline_value,
            },
            "activities": {
                "total": total_activities,
                "completed": completed_activities,
                "pending": pending_activities,
            },
        })
