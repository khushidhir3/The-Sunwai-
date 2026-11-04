"""Audit URL configuration."""
from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_log_view, name='audit_log'),
]
