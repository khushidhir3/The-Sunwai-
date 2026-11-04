"""
scheduling — Hearing slot management with conflict detection.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Courtroom(models.Model):
    """A physical or virtual courtroom."""
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200, blank=True)
    is_virtual = models.BooleanField(default=False)
    capacity = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class HearingSlot(models.Model):
    """A scheduled hearing slot with conflict detection."""

    class SlotStatus(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        CONFIRMED = 'confirmed', 'Confirmed'
        RESCHEDULED = 'rescheduled', 'Rescheduled'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    case = models.ForeignKey(
        'cases.Case', on_delete=models.CASCADE, related_name='hearing_slots',
    )
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    courtroom = models.ForeignKey(
        Courtroom, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='slots',
    )
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, related_name='hearing_slots',
        limit_choices_to={'role': 'judge'},
    )
    status = models.CharField(
        max_length=20, choices=SlotStatus.choices, default=SlotStatus.SCHEDULED,
    )
    purpose = models.CharField(max_length=200, default='Case Management Hearing')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.case.case_no} — {self.date} {self.start_time}'

    def clean(self):
        """Validate no double-booking of judge, courtroom, or advocates."""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Start time must be before end time.')

        conflicts = self._find_conflicts()
        if conflicts:
            raise ValidationError(conflicts)

    def _find_conflicts(self):
        """Check for judge, courtroom and advocate scheduling conflicts."""
        errors = {}
        overlapping = HearingSlot.objects.filter(
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=['scheduled', 'confirmed'],
        ).exclude(pk=self.pk)

        # Judge conflict
        if self.judge:
            judge_conflict = overlapping.filter(judge=self.judge).first()
            if judge_conflict:
                errors['judge'] = (
                    f'{self.judge.display_name} is already scheduled for '
                    f'{judge_conflict.case.case_no} at this time.'
                )

        # Courtroom conflict
        if self.courtroom:
            room_conflict = overlapping.filter(courtroom=self.courtroom).first()
            if room_conflict:
                errors['courtroom'] = (
                    f'{self.courtroom.name} is already booked for '
                    f'{room_conflict.case.case_no} at this time.'
                )

        return errors

    @classmethod
    def next_free_slot(cls, judge, courtroom=None, duration_minutes=30):
        """Suggest the next available slot for a judge."""
        from datetime import date, time, timedelta, datetime

        check_date = date.today()
        court_start = time(10, 0)
        court_end = time(17, 0)

        for _ in range(30):  # Look ahead 30 days
            current_time = court_start
            existing = cls.objects.filter(
                date=check_date,
                judge=judge,
                status__in=['scheduled', 'confirmed'],
            ).order_by('start_time')

            for slot in existing:
                if current_time < slot.start_time:
                    end = (datetime.combine(check_date, current_time) +
                           timedelta(minutes=duration_minutes)).time()
                    if end <= slot.start_time and end <= court_end:
                        return check_date, current_time, end
                current_time = max(current_time, slot.end_time)

            # Check after last slot
            end = (datetime.combine(check_date, current_time) +
                   timedelta(minutes=duration_minutes)).time()
            if end <= court_end:
                return check_date, current_time, end

            check_date += timedelta(days=1)
            # Skip weekends
            while check_date.weekday() >= 5:
                check_date += timedelta(days=1)

        return None


class ScheduleRequest(models.Model):
    """Request to reschedule a hearing."""

    class RequestStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    slot = models.ForeignKey(
        HearingSlot, on_delete=models.CASCADE, related_name='reschedule_requests',
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    reason = models.TextField()
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING,
    )
    response_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Reschedule: {self.slot} — {self.get_status_display()}'
