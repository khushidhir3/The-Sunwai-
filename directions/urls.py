"""Directions URL configuration."""
from django.urls import path
from . import views

app_name = 'directions'

urlpatterns = [
    path('', views.directions_list, name='directions_list'),
    path('record/<int:hearing_id>/', views.record_directions, name='record_directions'),
    path('order/<int:hearing_id>/pdf/', views.order_pdf, name='order_pdf'),
]
