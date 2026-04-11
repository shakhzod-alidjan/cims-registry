from django.urls import path
from . import api_views
urlpatterns = [
    path('',          api_views.CloudServerListView.as_view(),   name='api_cloud_list'),
    path('<int:pk>/', api_views.CloudServerDetailView.as_view(), name='api_cloud_detail'),
    path('providers/', api_views.ProviderListView.as_view(),     name='api_provider_list'),
]
