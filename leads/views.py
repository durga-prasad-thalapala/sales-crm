
from rest_framework.pagination import PageNumberPagination
from accounts.permissions import IsSalespersonOrAbove
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lead
from .serializers import LeadSerializer
from .services import convert_lead_to_customer


class LeadListCreateAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get(self, request):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            leads = Lead.objects.all().order_by("-created_at")
        else:
            leads = Lead.objects.filter(
                assigned_to=request.user
            ).order_by("-created_at")

        # Search
        search = request.query_params.get("search")

        if search:
            leads = leads.filter(
                name__icontains=search
            ) | leads.filter(
                company__icontains=search
            ) | leads.filter(
                email__icontains=search
            )

        # Status filter
        status_filter = request.query_params.get("status")

        if status_filter:
            leads = leads.filter(status=status_filter)

        # Source filter
        source_filter = request.query_params.get("source")

        if source_filter:
            leads = leads.filter(source=source_filter)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(
            leads,
            request,
            view=self,
        )

        serializer = LeadSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )


    def post(self, request):
        serializer = LeadSerializer(data=request.data)

        if serializer.is_valid():
            if request.user.role == "SALESPERSON":
                lead = serializer.save(assigned_to=request.user)
            else:
                lead = serializer.save()

            return Response(
                LeadSerializer(lead).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )



class LeadConvertAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def post(self, request, lead_id):
        try:
            lead = Lead.objects.get(id=lead_id)

            if (
                request.user.role == "SALESPERSON"
                and lead.assigned_to_id != request.user.id
            ):
                return Response(
                    {
                        "error": "You can only convert your assigned leads."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            customer = convert_lead_to_customer(lead_id)

            return Response(
                {
                    "message": "Lead converted successfully.",
                    "customer_id": customer.id,
                },
                status=status.HTTP_200_OK,
            )

        except Lead.DoesNotExist:
            return Response(
                {"error": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LeadDetailAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get_object(self, request, lead_id):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            return Lead.objects.filter(id=lead_id).first()

        return Lead.objects.filter(
            id=lead_id,
            assigned_to=request.user,
        ).first()

    def get(self, request, lead_id):
        lead = self.get_object(request, lead_id)

        if not lead:
            return Response(
                {"detail": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LeadSerializer(lead)
        return Response(serializer.data)


    def patch(self, request, lead_id):
        lead = self.get_object(request, lead_id)

        if not lead:
            return Response(
                {"detail": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        update_data = request.data.copy()

        if request.user.role == "SALESPERSON":
            update_data.pop("assigned_to", None)

        serializer = LeadSerializer(
            lead,
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



    def delete(self, request, lead_id):
        lead = self.get_object(request, lead_id)

        if not lead:
            return Response(
                {"detail": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        lead.delete()

        return Response(
            {"message": "Lead deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
