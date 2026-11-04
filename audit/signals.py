"""Audit signals — auto-log all create, update, and status changes."""
import threading

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from cases.models import Case, Pleading
from scheduling.models import HearingSlot, ScheduleRequest
from hearings.models import Hearing, ChecklistItem
from directions.models import Direction, ComplianceTask, Order

from .models import AuditLog

# Thread-local for storing the current user
_thread_locals = threading.local()


def set_current_user(user):
    _thread_locals.user = user


def get_current_user():
    return getattr(_thread_locals, 'user', None)


# Models to audit
AUDITED_MODELS = [
    Case, Pleading, HearingSlot, ScheduleRequest,
    Hearing, ChecklistItem, Direction, ComplianceTask, Order,
]

# Fields that represent "status"
STATUS_FIELDS = {'status', 'stage', 'is_completed', 'signed', 'sent'}


def _get_changes(instance, model_class):
    """Compare current instance with database version."""
    if not instance.pk:
        return {}
    try:
        old = model_class.objects.get(pk=instance.pk)
    except model_class.DoesNotExist:
        return {}

    changes = {}
    for field in instance._meta.fields:
        old_val = getattr(old, field.attname)
        new_val = getattr(instance, field.attname)
        if old_val != new_val:
            changes[field.name] = {
                'old': str(old_val),
                'new': str(new_val),
            }
    return changes


@receiver(pre_save)
def capture_changes(sender, instance, **kwargs):
    """Store changes before save for comparison."""
    if sender not in AUDITED_MODELS:
        return
    instance._audit_changes = _get_changes(instance, sender)
    instance._audit_is_new = instance.pk is None


@receiver(post_save)
def log_change(sender, instance, created, **kwargs):
    """Create audit log entry after save."""
    if sender not in AUDITED_MODELS:
        return

    changes = getattr(instance, '_audit_changes', {})
    is_new = getattr(instance, '_audit_is_new', created)

    if is_new:
        action = AuditLog.Action.CREATE
    elif any(f in changes for f in STATUS_FIELDS):
        action = AuditLog.Action.STATUS_CHANGE
    elif changes:
        action = AuditLog.Action.UPDATE
    else:
        return  # No changes to log

    AuditLog.objects.create(
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance)[:300],
        user=get_current_user(),
        changes=changes if changes else {},
    )
