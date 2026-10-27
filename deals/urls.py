from django.urls import path
from .views import DealListCreateAPIView, DealDetailAPIView

urlpatterns = [
    path("", DealListCreateAPIView.as_view(), name="deal-list-create"),
    path("<int:deal_id>/", DealDetailAPIView.as_view(), name="deal-detail"),
]
