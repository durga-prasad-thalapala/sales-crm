from django.urls import path
from .views import LeadListCreateAPIView, LeadConvertAPIView, LeadDetailAPIView

urlpatterns = [
    path("", LeadListCreateAPIView.as_view(), name="lead-list-create"),
    path("<int:lead_id>/", LeadDetailAPIView.as_view(), name="lead-detail"),
    path("<int:lead_id>/convert/", LeadConvertAPIView.as_view(), name="lead-convert"),
]
