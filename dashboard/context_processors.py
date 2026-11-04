"""Context processor for newspaper template variables."""
from datetime import date
from django.conf import settings


def newspaper_context(request):
    """Add newspaper-specific variables to every template context."""
    today = date.today()
    return {
        'portal_name': 'The Sunwai',
        'portal_tagline': getattr(settings, 'PORTAL_TAGLINE',
                                  'The e-Portal for Case Management Hearings'),
        'portal_established': getattr(settings, 'PORTAL_ESTABLISHED', '2024'),
        'court_name': getattr(settings, 'COURT_NAME', 'The Sunwai e-Court'),
        'today_date': today,
        'volume_no': today.year - 2024 + 1,
        'issue_no': today.timetuple().tm_yday,
        'edition_date': today.strftime('%A, %B %d, %Y'),
        'jitsi_domain': getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si'),
    }
