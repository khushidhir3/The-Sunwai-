"""Celery tasks for sending hearing reminders."""
from datetime import date, timedelta
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_scheduled_reminders():
    """Check for upcoming hearings and send reminders at T-7, T-2, T-1."""
    from scheduling.models import HearingSlot
    from notices.models import Reminder
    from cases.models import Party

    today = date.today()
    reminder_days = {
        7: Reminder.ReminderType.T_MINUS_7,
        2: Reminder.ReminderType.T_MINUS_2,
        1: Reminder.ReminderType.T_MINUS_1,
    }

    for days, reminder_type in reminder_days.items():
        target_date = today + timedelta(days=days)
        slots = HearingSlot.objects.filter(
            date=target_date,
            status__in=['scheduled', 'confirmed'],
        ).select_related('case', 'judge')

        for slot in slots:
            # Collect recipients: judge, advocates, litigants
            recipients = set()
            if slot.judge:
                recipients.add(slot.judge)

            parties = Party.objects.filter(case=slot.case).select_related(
                'user', 'advocate',
            )
            for party in parties:
                if party.advocate:
                    recipients.add(party.advocate)
                if party.user:
                    recipients.add(party.user)

            for user in recipients:
                reminder, created = Reminder.objects.get_or_create(
                    slot=slot,
                    reminder_type=reminder_type,
                    recipient=user,
                )
                if created:
                    send_hearing_reminder.delay(reminder.pk)


@shared_task
def send_hearing_reminder(reminder_id):
    """Send an individual hearing reminder email."""
    from notices.models import Reminder
    from django.utils import timezone

    try:
        reminder = Reminder.objects.select_related(
            'slot__case', 'recipient',
        ).get(pk=reminder_id, sent=False)
    except Reminder.DoesNotExist:
        return

    slot = reminder.slot
    case = slot.case

    subject = f'[The Sunwai] Hearing Reminder: {case.case_no}'
    message = (
        f'Dear {reminder.recipient.display_name},\n\n'
        f'This is a reminder for the upcoming hearing:\n\n'
        f'Case: {case.case_no} — {case.title}\n'
        f'Date: {slot.date.strftime("%d %B %Y")}\n'
        f'Time: {slot.start_time.strftime("%I:%M %p")}\n'
        f'Purpose: {slot.purpose}\n\n'
        f'Please ensure all pre-hearing requirements are completed.\n\n'
        f'— The Sunwai Court Registry'
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'registry@thesunwai.court'),
            recipient_list=[reminder.recipient.email],
            fail_silently=False,
        )
        reminder.sent = True
        reminder.sent_at = timezone.now()
        reminder.save()
    except Exception as e:
        print(f'Failed to send reminder {reminder_id}: {e}')
