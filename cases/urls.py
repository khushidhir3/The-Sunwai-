"""Cases URL configuration."""
from django.urls import path
from . import views

app_name = 'cases'

urlpatterns = [
    path('', views.case_list, name='case_list'),
    path('new/', views.case_create, name='case_create'),
    path('<path:case_no>/bundle/', views.case_bundle, name='case_bundle'),
    path('<path:case_no>/', views.case_detail, name='case_detail'),
]
