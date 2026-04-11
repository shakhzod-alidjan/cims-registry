from django.urls import path
from . import views
urlpatterns = [
    path('',              views.cloud_list,    name='cloud_list'),
    path('add/',          views.server_add,    name='server_add'),
    path('<int:pk>/edit/',   views.server_edit,   name='server_edit'),
    path('<int:pk>/delete/', views.server_delete, name='server_delete'),
]
