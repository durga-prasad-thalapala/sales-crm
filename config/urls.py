from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/customers/", include("customers.urls")),
    path("api/leads/", include("leads.urls")),
    path("api/deals/", include("deals.urls")),
    path("api/activities/", include("activities.urls")),
    path("api/dashboard/", include("dashboard.urls")),
]
