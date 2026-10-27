
from django.db.models import Q

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import (
    IsSalespersonOrAbove,
    IsSalesManagerOrAdmin,
)
from .models import Deal
from .serializers import DealSerializer
from customers.models import Customer


class DealListCreateAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get(self, request):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            deals = Deal.objects.all()
        else:
            deals = Deal.objects.filter(assigned_to=request.user)

        deals = deals.order_by("-created_at")

        # Search by title or description
        search_term = request.query_params.get("search")

        if search_term:
            deals = deals.filter(
                Q(title__icontains=search_term)
                | Q(description__icontains=search_term)
            )

        # Filter by stage
        stage_filter = request.query_params.get("stage")

        if stage_filter:
            deals = deals.filter(stage=stage_filter)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(
            deals,
            request,
            view=self,
        )

        serializer = DealSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)



    def post(self, request):
        serializer = DealSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = serializer.validated_data["customer"]

        if request.user.role == "SALESPERSON":
            can_access_customer = (
                Customer.objects.filter(
                    id=customer.id,
                    created_by=request.user,
                ).exists()
                or Deal.objects.filter(
                    customer=customer,
                    assigned_to=request.user,
                ).exists()
            )


            if not can_access_customer:
                return Response(
                    {
                        "detail": (
                            "You can only create deals for customers "
                            "you are authorized to access."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            deal = serializer.save(assigned_to=request.user)
        else:
            deal = serializer.save()

        return Response(
            DealSerializer(deal).data,
            status=status.HTTP_201_CREATED,
        )




class DealDetailAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get_object(self, request, deal_id):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            return Deal.objects.filter(id=deal_id).first()

        return Deal.objects.filter(
            id=deal_id,
            assigned_to=request.user,
        ).first()

    def get(self, request, deal_id):
        deal = self.get_object(request, deal_id)

        if not deal:
            return Response(
                {"detail": "Deal not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DealSerializer(deal)
        return Response(serializer.data)

    def patch(self, request, deal_id):
        deal = self.get_object(request, deal_id)

        if not deal:
            return Response(
                {"detail": "Deal not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Salespersons cannot reassign a deal to another user.
        update_data = request.data.copy()

        if request.user.role == "SALESPERSON":
            update_data.pop("assigned_to", None)

        serializer = DealSerializer(
            deal,
            data=update_data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


    def delete(self, request, deal_id):
        if not IsSalesManagerOrAdmin().has_permission(request, self):
            return Response(
                {"detail": "You do not have permission to delete deals."},
                status=status.HTTP_403_FORBIDDEN,
            )

        deal = self.get_object(request, deal_id)

        if not deal:
            return Response(
                {"detail": "Deal not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        deal.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )