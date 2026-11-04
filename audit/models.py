"""
audit — Append-only audit log via signals.
"""
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Immutable audit trail for all model changes."""

    class Action(models.TextChoices):
        CREATE = 'create', 'Created'
        UPDATE = 'update', 'Updated'
        STATUS_CHANGE = 'status_change', 'Status Changed'
        DELETE = 'delete', 'Deleted'

    action = models.CharField(max_length=20, choices=Action.choices)
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.CharField(max_length=100, db_index=True)
    object_repr = models.CharField(max_length=300)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    changes = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log Entry'
        verbose_name_plural = 'Audit Log'
        # Prevent modifications
        managed = True

    def __str__(self):
        return f'{self.get_action_display()} {self.model_name} #{self.object_id}'

    def save(self, *args, **kwargs):
        """Only allow creation, never updates."""
        if self.pk:
            raise ValueError('Audit log entries cannot be modified.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of audit entries."""
        raise ValueError('Audit log entries cannot be deleted.')
