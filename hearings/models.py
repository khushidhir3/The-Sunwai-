"""
hearings — Pre-hearing checklist, hearing room, chat, and judge notes.
"""
from django.conf import settings
from django.db import models


class Hearing(models.Model):
    """A hearing session linked to a scheduled slot."""

    class HearingStatus(models.TextChoices):
        UPCOMING = 'upcoming', 'Upcoming'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        ADJOURNED = 'adjourned', 'Adjourned'

    slot = models.OneToOneField(
        'scheduling.HearingSlot',
        on_delete=models.CASCADE,
        related_name='hearing',
    )
    status = models.CharField(
        max_length=20,
        choices=HearingStatus.choices,
        default=HearingStatus.UPCOMING,
    )
    jitsi_room_name = models.CharField(max_length=200, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True, help_text='Post-hearing summary')

    class Meta:
        ordering = ['-slot__date', '-slot__start_time']

    def __str__(self):
        return f'Hearing: {self.slot}'

    def save(self, *args, **kwargs):
        if not self.jitsi_room_name:
            case_no = self.slot.case.case_no.replace('/', '-').replace(' ', '')
            self.jitsi_room_name = f'sunwai-{case_no}-{self.slot.date}'
        super().save(*args, **kwargs)

    @property
    def jitsi_url(self):
        domain = getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si')
        return f'https://{domain}/{self.jitsi_room_name}'


class PreHearingChecklist(models.Model):
    """Pre-hearing checklist for a case hearing."""

    hearing = models.OneToOneField(
        Hearing, on_delete=models.CASCADE, related_name='checklist',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Checklist for {self.hearing}'

    @property
    def completion_percentage(self):
        items = self.items.all()
        if not items:
            return 0
        completed = items.filter(is_completed=True).count()
        return int((completed / items.count()) * 100)


class ChecklistItem(models.Model):
    """Individual item in a pre-hearing checklist."""

    class ItemCategory(models.TextChoices):
        PLEADINGS = 'pleadings', 'Pleadings Filed'
        ISSUES = 'issues', 'Issues Framed'
        ADMISSIONS = 'admissions', 'Admissions/Denials'
        WITNESS_LIST = 'witness_list', 'Witness List'
        JOINT_TIMETABLE = 'timetable', 'Joint Timetable'

    checklist = models.ForeignKey(
        PreHearingChecklist, on_delete=models.CASCADE, related_name='items',
    )
    category = models.CharField(max_length=20, choices=ItemCategory.choices)
    description = models.CharField(max_length=300)
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['category', 'pk']

    def __str__(self):
        status = '✓' if self.is_completed else '○'
        return f'{status} {self.description}'


class HearingNote(models.Model):
    """Judge-only private notes during a hearing."""

    hearing = models.ForeignKey(
        Hearing, on_delete=models.CASCADE, related_name='notes',
    )
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'judge'},
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Note by {self.judge.display_name} — {self.created_at}'


class ChatMessage(models.Model):
    """Live chat message during a hearing."""

    hearing = models.ForeignKey(
        Hearing, on_delete=models.CASCADE, related_name='chat_messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender.display_name}: {self.message[:50]}'
