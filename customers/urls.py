from django.urls import path
from .views import CustomerListCreateAPIView, CustomerDetailAPIView

urlpatterns = [
    path(
        "",
        CustomerListCreateAPIView.as_view(),
        name="customer-list-create",
    ),
    path(
        "<int:customer_id>/",
        CustomerDetailAPIView.as_view(),
        name="customer-detail",
    ),
]
