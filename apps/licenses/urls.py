from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.license_list,            name='license_list'),
    path('add/',                views.license_add,             name='license_add'),
    path('<int:pk>/',           views.license_detail,          name='license_detail'),
    path('<int:pk>/edit/',      views.license_edit,            name='license_edit'),
    path('<int:pk>/delete/',    views.license_delete,          name='license_delete'),
    path('export/xlsx/',        views.export_licenses_xlsx,    name='license_export_xlsx'),
    path('suggest-category/',   views.suggest_category_ajax,   name='suggest_category'),
]
