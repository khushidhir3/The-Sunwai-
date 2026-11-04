"""Scheduling URL configuration."""
from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    path('cause-list/', views.cause_list, name='cause_list'),
    path('schedule/', views.schedule_hearing, name='schedule_hearing'),
    path('suggest-slot/', views.suggest_slot, name='suggest_slot'),
]
