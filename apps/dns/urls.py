from django.urls import path
from . import views
urlpatterns = [
    path('',              views.dns_list,    name='dns_list'),
    path('add/',          views.domain_add,  name='domain_add'),
    path('<int:pk>/edit/',   views.domain_edit,   name='domain_edit'),
    path('<int:pk>/delete/', views.domain_delete, name='domain_delete'),
    path('<int:pk>/payment/', views.domain_payment, name='domain_payment'),
]
