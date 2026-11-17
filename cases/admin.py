from django.contrib import admin
from .models import Case, Party, Pleading


class PartyInline(admin.TabularInline):
    model = Party
    extra = 2
    fields = ('name', 'party_type', 'user', 'advocate')


class PleadingInline(admin.StackedInline):
    model = Pleading
    extra = 1
    fields = ('title', 'doc_type', 'file', 'uploaded_by', 'description')


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_no', 'title', 'case_type', 'status', 'stage', 'judge', 'filing_date')
    list_filter = ('case_type', 'status', 'stage', 'judge')
    search_fields = ('case_no', 'title', 'description')
    inlines = [PartyInline, PleadingInline]
    date_hierarchy = 'filing_date'


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'party_type', 'case', 'advocate')
    list_filter = ('party_type',)
    search_fields = ('name', 'case__case_no', 'case__title')


@admin.register(Pleading)
class PleadingAdmin(admin.ModelAdmin):
    list_display = ('title', 'case', 'doc_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('doc_type', 'uploaded_at')
    search_fields = ('title', 'case__case_no')
