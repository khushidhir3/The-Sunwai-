"""Hearings views — hearing room, checklist, notes."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from .models import Hearing, PreHearingChecklist, ChecklistItem, HearingNote


@login_required
def hearing_room(request, hearing_id):
    """Virtual hearing room with Jitsi, chat, and judge notes."""
    hearing = get_object_or_404(
        Hearing.objects.select_related('slot__case', 'slot__judge', 'slot__courtroom'),
        pk=hearing_id,
    )

    # Get or create checklist
    checklist, _ = PreHearingChecklist.objects.get_or_create(hearing=hearing)

    # Create default checklist items if none exist
    if not checklist.items.exists():
        default_items = [
            (ChecklistItem.ItemCategory.PLEADINGS, 'All pleadings filed and served'),
            (ChecklistItem.ItemCategory.ISSUES, 'Issues framed and agreed upon'),
            (ChecklistItem.ItemCategory.ADMISSIONS, 'Admissions and denials recorded'),
            (ChecklistItem.ItemCategory.WITNESS_LIST, 'Witness list exchanged'),
            (ChecklistItem.ItemCategory.JOINT_TIMETABLE, 'Joint timetable proposed'),
        ]
        for category, desc in default_items:
            ChecklistItem.objects.create(
                checklist=checklist,
                category=category,
                description=desc,
            )

    checklist_items = checklist.items.all()
    chat_messages = hearing.chat_messages.select_related('sender').all()[:50]

    # Judge notes (only for judges)
    judge_notes = []
    if request.user.is_judge:
        judge_notes = hearing.notes.filter(judge=request.user)

    context = {
        'hearing': hearing,
        'case': hearing.slot.case,
        'checklist': checklist,
        'checklist_items': checklist_items,
        'chat_messages': chat_messages,
        'judge_notes': judge_notes,
        'jitsi_domain': getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si'),
        'is_judge': request.user.is_judge,
    }
    return render(request, 'hearings/hearing_room.html', context)


@login_required
def toggle_checklist_item(request, item_id):
    """HTMX: toggle a checklist item completion."""
    item = get_object_or_404(ChecklistItem, pk=item_id)

    if request.method == 'POST':
        item.is_completed = not item.is_completed
        if item.is_completed:
            item.completed_by = request.user
            item.completed_at = timezone.now()
        else:
            item.completed_by = None
            item.completed_at = None
        item.save()

    return render(request, 'hearings/_checklist_item.html', {'item': item})


@login_required
def save_judge_note(request, hearing_id):
    """HTMX: save a judge's private note."""
    if not request.user.is_judge:
        return JsonResponse({'error': 'Judges only'}, status=403)

    hearing = get_object_or_404(Hearing, pk=hearing_id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            HearingNote.objects.create(
                hearing=hearing,
                judge=request.user,
                content=content,
            )

    notes = hearing.notes.filter(judge=request.user)
    return render(request, 'hearings/_judge_notes.html', {'judge_notes': notes})
