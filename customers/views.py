from django.db import models

from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import (
    IsSalespersonOrAbove,
    IsSalesManagerOrAdmin,
)

from .models import Customer
from .serializers import CustomerSerializer


class CustomerListCreateAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get(self, request):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            customers = Customer.objects.all().order_by("-created_at")

        else:
            customers = Customer.objects.filter(
                models.Q(deals__assigned_to=request.user)
                | models.Q(created_by=request.user)
            ).distinct().order_by("-created_at")

        # Search
        search = request.query_params.get("search")

        if search:
            customers = customers.filter(
                models.Q(name__icontains=search)
                | models.Q(company__icontains=search)
                | models.Q(email__icontains=search)
            )

        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(
            customers,
            request,
            view=self,
        )

        serializer = CustomerSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)

        if serializer.is_valid():
            customer = serializer.save(
                created_by=request.user
            )

            return Response(
                CustomerSerializer(customer).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class CustomerDetailAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get_object(self, request, customer_id):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            return Customer.objects.filter(
                id=customer_id
            ).first()

        return Customer.objects.filter(
            models.Q(id=customer_id),
            models.Q(deals__assigned_to=request.user)
            | models.Q(created_by=request.user)
        ).distinct().first()

    def get(self, request, customer_id):
        customer = self.get_object(request, customer_id)

        if not customer:
            return Response(
                {"detail": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CustomerSerializer(customer)

        return Response(serializer.data)

    def patch(self, request, customer_id):
        customer = self.get_object(request, customer_id)

        if not customer:
            return Response(
                {"detail": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CustomerSerializer(
            customer,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


    def delete(self, request, customer_id):
        if not IsSalesManagerOrAdmin().has_permission(request, self):
            return Response(
                {"detail": "You do not have permission to delete customers."},
                status=status.HTTP_403_FORBIDDEN,
            )

        customer = self.get_object(request, customer_id)

        if not customer:
            return Response(
                {"detail": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        customer.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
