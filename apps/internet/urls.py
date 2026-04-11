from django.urls import path
from . import views
urlpatterns = [
    path('',              views.isp_list,   name='isp_list'),
    path('add/',          views.isp_add,    name='isp_add'),
    path('<int:pk>/edit/',   views.isp_edit,   name='isp_edit'),
    path('<int:pk>/delete/', views.isp_delete, name='isp_delete'),
]
