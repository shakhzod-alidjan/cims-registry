from django.urls import path
from . import api_views
urlpatterns = [
    path('',          api_views.ISPListView.as_view(),   name='api_isp_list'),
    path('<int:pk>/', api_views.ISPDetailView.as_view(), name='api_isp_detail'),
    path('operators/', api_views.OperatorListView.as_view(), name='api_operator_list'),
]
