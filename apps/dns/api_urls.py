from django.urls import path
from . import api_views
urlpatterns = [
    path('',          api_views.DomainListView.as_view(),   name='api_domain_list'),
    path('<int:pk>/', api_views.DomainDetailView.as_view(), name='api_domain_detail'),
]
