"""Audit views — read-only log viewer."""
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .models import AuditLog


@login_required
@staff_member_required
def audit_log_view(request):
    """Read-only audit log viewer (staff only)."""
    logs = AuditLog.objects.select_related('user').all()

    # Filters
    model_name = request.GET.get('model')
    if model_name:
        logs = logs.filter(model_name=model_name)

    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)

    # Get unique model names for filter dropdown
    model_names = AuditLog.objects.values_list(
        'model_name', flat=True,
    ).distinct().order_by('model_name')

    context = {
        'logs': logs[:100],
        'model_names': model_names,
        'action_choices': AuditLog.Action.choices,
        'current_model': model_name,
        'current_action': action,
    }
    return render(request, 'audit/audit_log.html', context)
