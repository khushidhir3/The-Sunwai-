"""
directions — Judge directions, compliance tasks, and order PDFs.
"""
from django.conf import settings
from django.db import models


class DirectionTemplate(models.Model):
    """Reusable direction templates."""
    title = models.CharField(max_length=200)
    body = models.TextField(help_text='Template text with {placeholders}')
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return self.title


class Direction(models.Model):
    """A specific direction issued by a judge."""

    class DirectionStatus(models.TextChoices):
        ISSUED = 'issued', 'Issued'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLIED = 'complied', 'Complied'
        OVERDUE = 'overdue', 'Overdue'

    hearing = models.ForeignKey(
        'hearings.Hearing',
        on_delete=models.CASCADE,
        related_name='directions',
    )
    serial_no = models.PositiveIntegerField()
    text = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_directions',
    )
    status = models.CharField(
        max_length=20,
        choices=DirectionStatus.choices,
        default=DirectionStatus.ISSUED,
    )
    template = models.ForeignKey(
        DirectionTemplate,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hearing', 'serial_no']
        unique_together = ['hearing', 'serial_no']

    def __str__(self):
        return f'Direction #{self.serial_no} — {self.hearing}'


class ComplianceTask(models.Model):
    """Tracks compliance with a direction."""

    class TaskStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUBMITTED = 'submitted', 'Submitted'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    direction = models.ForeignKey(
        Direction, on_delete=models.CASCADE, related_name='tasks',
    )
    description = models.CharField(max_length=300)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='compliance_tasks',
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )
    evidence_file = models.FileField(
        upload_to='compliance/%Y/%m/', blank=True,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_tasks',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-direction__deadline']

    def __str__(self):
        return f'Task: {self.description[:50]}'


class Order(models.Model):
    """Final order exported as PDF."""

    hearing = models.ForeignKey(
        'hearings.Hearing',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    title = models.CharField(max_length=200, default='Order')
    body = models.TextField()
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'judge'},
    )
    pdf_file = models.FileField(
        upload_to='orders/%Y/%m/', blank=True,
    )
    signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.hearing}'
