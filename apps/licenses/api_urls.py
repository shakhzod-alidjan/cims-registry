from django.urls import path
from . import api_views

urlpatterns = [
    path('',          api_views.LicenseListView.as_view(),   name='api_license_list'),
    path('<int:pk>/', api_views.LicenseDetailView.as_view(), name='api_license_detail'),
    path('apps/',     api_views.BusinessAppListView.as_view(), name='api_app_list'),
    path('vendors/',  api_views.VendorListView.as_view(),    name='api_vendor_list'),
]
