"""Hearings URL configuration."""
from django.urls import path
from . import views

app_name = 'hearings'

urlpatterns = [
    path('<int:hearing_id>/', views.hearing_room, name='hearing_room'),
    path('checklist-item/<int:item_id>/toggle/', views.toggle_checklist_item, name='toggle_checklist_item'),
    path('<int:hearing_id>/note/', views.save_judge_note, name='save_judge_note'),
]
