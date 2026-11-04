"""Scheduling views — slots, conflicts, rescheduling."""
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import HearingSlot, Courtroom, ScheduleRequest


@login_required
def cause_list(request):
    """Today's cause list."""
    selected_date = request.GET.get('date', str(date.today()))
    slots = HearingSlot.objects.filter(
        date=selected_date,
        status__in=['scheduled', 'confirmed'],
    ).select_related('case', 'judge', 'courtroom').order_by('start_time')

    context = {
        'slots': slots,
        'selected_date': selected_date,
    }
    return render(request, 'scheduling/cause_list.html', context)


@login_required
def schedule_hearing(request):
    """Schedule a new hearing slot (registrar / admin only)."""
    if request.method == 'POST':
        from cases.models import Case
        from accounts.models import User

        try:
            case = Case.objects.get(case_no=request.POST.get('case_no'))
            judge = User.objects.get(pk=request.POST.get('judge'))
            courtroom = Courtroom.objects.get(pk=request.POST.get('courtroom'))

            slot = HearingSlot(
                case=case,
                date=request.POST.get('date'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
                judge=judge,
                courtroom=courtroom,
                purpose=request.POST.get('purpose', 'Case Management Hearing'),
            )
            slot.full_clean()
            slot.save()

            # Create hearing object
            from hearings.models import Hearing
            Hearing.objects.create(slot=slot)

            messages.success(request, f'Hearing scheduled: {slot}')
            return redirect('scheduling:cause_list')
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error scheduling hearing: {e}')

    from accounts.models import User
    context = {
        'judges': User.objects.filter(role='judge', is_active=True),
        'courtrooms': Courtroom.objects.filter(is_active=True),
    }
    return render(request, 'scheduling/schedule_hearing.html', context)


@login_required
def suggest_slot(request):
    """HTMX endpoint: suggest the next free slot for a judge."""
    from accounts.models import User

    judge_id = request.GET.get('judge')
    if not judge_id:
        return render(request, 'scheduling/_slot_suggestion.html', {})

    try:
        judge = User.objects.get(pk=judge_id, role='judge')
        result = HearingSlot.next_free_slot(judge)
        if result:
            suggested_date, start, end = result
            context = {
                'suggested_date': suggested_date,
                'suggested_start': start,
                'suggested_end': end,
            }
        else:
            context = {'no_slots': True}
    except User.DoesNotExist:
        context = {}

    return render(request, 'scheduling/_slot_suggestion.html', context)
