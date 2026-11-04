"""Dashboard views — the newspaper front page."""
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from cases.models import Case
from scheduling.models import HearingSlot
from directions.models import Direction, ComplianceTask
from hearings.models import Hearing


@login_required
def front_page(request):
    """The main newspaper-style front page dashboard."""
    today = date.today()
    user = request.user

    # ── Left Column: Cause List ──
    todays_hearings = HearingSlot.objects.filter(
        date=today,
        status__in=['scheduled', 'confirmed'],
    ).select_related('case', 'judge', 'courtroom').order_by('start_time')

    # ── Centre Column: Lead Story (next hearing) ──
    next_hearing = None
    if user.is_judge:
        next_slot = HearingSlot.objects.filter(
            judge=user,
            date__gte=today,
            status__in=['scheduled', 'confirmed'],
        ).select_related('case', 'courtroom').order_by('date', 'start_time').first()
    elif user.is_advocate:
        from cases.models import Party
        case_ids = Party.objects.filter(
            advocate=user,
        ).values_list('case_id', flat=True)
        next_slot = HearingSlot.objects.filter(
            case_id__in=case_ids,
            date__gte=today,
            status__in=['scheduled', 'confirmed'],
        ).select_related('case', 'judge', 'courtroom').order_by('date', 'start_time').first()
    else:
        next_slot = HearingSlot.objects.filter(
            date__gte=today,
            status__in=['scheduled', 'confirmed'],
        ).select_related('case', 'judge', 'courtroom').order_by('date', 'start_time').first()

    if next_slot:
        try:
            next_hearing = next_slot.hearing
        except Hearing.DoesNotExist:
            next_hearing = None

    # ── Right Column: Sidebar ──
    # Pending directions
    pending_directions = Direction.objects.filter(
        status__in=['issued', 'in_progress'],
    ).select_related('hearing__slot__case')[:5]

    # Overdue tasks
    overdue_tasks = ComplianceTask.objects.filter(
        status='pending',
        direction__deadline__lt=today,
    ).select_related('direction__hearing__slot__case')[:5]

    # Stats
    total_cases = Case.objects.filter(status__in=['active', 'pending']).count()
    todays_count = todays_hearings.count()
    pending_count = Direction.objects.filter(
        status__in=['issued', 'in_progress'],
    ).count()

    # Recent cases
    recent_cases = Case.objects.all()[:5]

    context = {
        'todays_hearings': todays_hearings,
        'next_slot': next_slot,
        'next_hearing': next_hearing,
        'pending_directions': pending_directions,
        'overdue_tasks': overdue_tasks,
        'total_cases': total_cases,
        'todays_count': todays_count,
        'pending_count': pending_count,
        'recent_cases': recent_cases,
    }
    return render(request, 'dashboard/front_page.html', context)
