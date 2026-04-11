from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

urlpatterns = [
    path('token/',         TokenObtainPairView.as_view(),  name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
    path('sites/',         api_views.SiteListView.as_view(), name='api_sites'),
    path('me/',            api_views.MeView.as_view(),       name='api_me'),
]
