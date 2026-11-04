"""Directions views — recording directions, compliance tracking, order PDFs."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string

from .models import Direction, ComplianceTask, Order, DirectionTemplate
from hearings.models import Hearing


@login_required
def directions_list(request):
    """List all pending directions."""
    directions = Direction.objects.select_related(
        'hearing__slot__case', 'assigned_to',
    ).all()

    status = request.GET.get('status')
    if status:
        directions = directions.filter(status=status)

    context = {
        'directions': directions[:50],
        'status_choices': Direction.DirectionStatus.choices,
        'current_status': status,
    }
    return render(request, 'directions/directions_list.html', context)


@login_required
def record_directions(request, hearing_id):
    """Judge records directions from a template."""
    if not request.user.is_judge:
        messages.error(request, 'Only judges can record directions.')
        return redirect('dashboard:front_page')

    hearing = get_object_or_404(Hearing, pk=hearing_id)
    templates = DirectionTemplate.objects.filter(is_active=True)

    if request.method == 'POST':
        # Process submitted directions
        from django.db.models import Max
        current_max = Direction.objects.filter(hearing=hearing).aggregate(Max('serial_no'))['serial_no__max'] or 0
        idx = 1
        while f'direction_{idx}' in request.POST:
            text = request.POST.get(f'direction_{idx}', '').strip()
            deadline = request.POST.get(f'deadline_{idx}')
            if text:
                current_max += 1
                dir_obj = Direction.objects.create(
                    hearing=hearing,
                    serial_no=current_max,
                    text=text,
                    deadline=deadline if deadline else None,
                    status=Direction.DirectionStatus.ISSUED,
                )
                # Create compliance task
                ComplianceTask.objects.create(
                    direction=dir_obj,
                    description=f'Comply with Direction #{current_max}',
                    assigned_to=request.user,
                )
            idx += 1

        messages.success(request, 'Directions recorded successfully.')
        return redirect('hearings:hearing_room', hearing_id=hearing_id)

    context = {
        'hearing': hearing,
        'case': hearing.slot.case,
        'templates': templates,
    }
    return render(request, 'directions/record_directions.html', context)


@login_required
def order_pdf(request, hearing_id):
    """Generate and serve order PDF via WeasyPrint."""
    hearing = get_object_or_404(
        Hearing.objects.select_related('slot__case', 'slot__judge'),
        pk=hearing_id,
    )
    directions = hearing.directions.all()

    context = {
        'hearing': hearing,
        'case': hearing.slot.case,
        'judge': hearing.slot.judge,
        'directions': directions,
        'generated_at': timezone.now(),
    }

    html_string = render_to_string('pdf/order.html', context)

    try:
        from weasyprint import HTML
        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'inline; filename="order_{hearing.slot.case.case_no}.pdf"'
        )
        return response
    except ImportError:
        # WeasyPrint not available — return HTML preview
        return HttpResponse(html_string)
