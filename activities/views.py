
from django.db.models import Q

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import (
    IsSalespersonOrAbove,
    IsSalesManagerOrAdmin,
)
from .models import Activity
from .serializers import ActivitySerializer


class ActivityListCreateAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get(self, request):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            activities = Activity.objects.all()
        else:
            activities = Activity.objects.filter(
                assigned_to=request.user
            )

        activities = activities.order_by("-created_at")

        # Search by title or description
        search_term = request.query_params.get("search")

        if search_term:
            activities = activities.filter(
                Q(title__icontains=search_term)
                | Q(description__icontains=search_term)
            )

        # Filter by activity type
        type_filter = request.query_params.get("type")

        if type_filter:
            activities = activities.filter(type=type_filter)

        # Filter by completion status
        completed_filter = request.query_params.get("completed")

        if completed_filter is not None:
            completed_value = completed_filter.lower()

            if completed_value in ["true", "false"]:
                activities = activities.filter(
                    completed=(completed_value == "true")
                )

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(
            activities,
            request,
            view=self,
        )

        serializer = ActivitySerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ActivitySerializer(data=request.data)

        if serializer.is_valid():
            if request.user.role == "SALESPERSON":
                activity = serializer.save(
                    assigned_to=request.user,
                    created_by=request.user,
                )
            else:
                activity = serializer.save(
                    created_by=request.user,
                )

            return Response(
                ActivitySerializer(activity).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ActivityDetailAPIView(APIView):
    permission_classes = [IsSalespersonOrAbove]

    def get_object(self, request, activity_id):
        if request.user.role in ["ADMIN", "SALES_MANAGER"]:
            return Activity.objects.filter(
                id=activity_id
            ).first()

        return Activity.objects.filter(
            id=activity_id,
            assigned_to=request.user,
        ).first()

    def get(self, request, activity_id):
        activity = self.get_object(request, activity_id)

        if not activity:
            return Response(
                {"detail": "Activity not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ActivitySerializer(activity)
        return Response(serializer.data)

    def patch(self, request, activity_id):
        activity = self.get_object(request, activity_id)

        if not activity:
            return Response(
                {"detail": "Activity not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        update_data = request.data.copy()

        if request.user.role == "SALESPERSON":
            update_data.pop("assigned_to", None)
            update_data.pop("created_by", None)

        serializer = ActivitySerializer(
            activity,
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


    def delete(self, request, activity_id):
        if not IsSalesManagerOrAdmin().has_permission(request, self):
            return Response(
                {
                    "detail": (
                        "You do not have permission to delete activities."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        activity = self.get_object(request, activity_id)

        if not activity:
            return Response(
                {"detail": "Activity not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        activity.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
