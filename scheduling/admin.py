from django.contrib import admin
from .models import Courtroom, HearingSlot


@admin.register(Courtroom)
class CourtroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_virtual', 'is_active')
    list_filter = ('is_virtual', 'is_active')


@admin.register(HearingSlot)
class HearingSlotAdmin(admin.ModelAdmin):
    list_display = ('case', 'date', 'start_time', 'end_time', 'judge', 'courtroom', 'status')
    list_filter = ('status', 'date', 'judge', 'courtroom')
    search_fields = ('case__case_no', 'case__title')
