from django.urls import path
from .views import ActivityListCreateAPIView, ActivityDetailAPIView

urlpatterns = [
    path(
        "",
        ActivityListCreateAPIView.as_view(),
        name="activity-list-create",
    ),
    path(
        "<int:activity_id>/",
        ActivityDetailAPIView.as_view(),
        name="activity-detail",
    ),
]
