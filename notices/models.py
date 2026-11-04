"""
notices — Hearing notices and email reminders.
"""
from django.conf import settings
from django.db import models


class HearingNotice(models.Model):
    """Generated PDF hearing notice."""

    slot = models.ForeignKey(
        'scheduling.HearingSlot',
        on_delete=models.CASCADE,
        related_name='notices',
    )
    pdf_file = models.FileField(
        upload_to='notices/%Y/%m/',
        blank=True,
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f'Notice for {self.slot}'


class Reminder(models.Model):
    """Email reminder tracking."""

    class ReminderType(models.TextChoices):
        T_MINUS_7 = 't7', '7 Days Before'
        T_MINUS_2 = 't2', '2 Days Before'
        T_MINUS_1 = 't1', '1 Day Before'

    slot = models.ForeignKey(
        'scheduling.HearingSlot',
        on_delete=models.CASCADE,
        related_name='reminders',
    )
    reminder_type = models.CharField(max_length=5, choices=ReminderType.choices)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['slot', 'reminder_type', 'recipient']

    def __str__(self):
        return f'{self.get_reminder_type_display()} for {self.recipient}'
