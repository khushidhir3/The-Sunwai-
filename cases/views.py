"""Cases views — case list, detail, case bundle."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from .models import Case, Pleading


@login_required
def case_list(request):
    """List all cases (newspaper style)."""
    cases = Case.objects.select_related('judge').all()

    # Filter by status
    status = request.GET.get('status')
    if status:
        cases = cases.filter(status=status)

    # Filter by type
    case_type = request.GET.get('type')
    if case_type:
        cases = cases.filter(case_type=case_type)

    context = {
        'cases': cases[:50],
        'status_choices': Case.Status.choices,
        'type_choices': Case.CaseType.choices,
        'current_status': status,
        'current_type': case_type,
    }
    return render(request, 'cases/case_list.html', context)


@login_required
def case_detail(request, case_no):
    """Case detail with parties, pleadings, and hearing history."""
    case = get_object_or_404(Case, case_no=case_no)
    pleadings = case.pleadings.select_related('uploaded_by').all()
    hearing_slots = case.hearing_slots.select_related('judge', 'courtroom').all()

    context = {
        'case': case,
        'petitioners': case.petitioners.select_related('advocate'),
        'respondents': case.respondents.select_related('advocate'),
        'pleadings': pleadings,
        'hearing_slots': hearing_slots,
    }
    return render(request, 'cases/case_detail.html', context)


@login_required
def case_bundle(request, case_no):
    """Case bundle viewer — all documents for a case."""
    case = get_object_or_404(Case, case_no=case_no)
    pleadings = case.pleadings.select_related('uploaded_by').all()

    context = {
        'case': case,
        'pleadings': pleadings,
    }
    return render(request, 'cases/case_bundle.html', context)
