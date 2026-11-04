"""Audit middleware to capture the current user for signals."""
from audit.signals import set_current_user


class AuditMiddleware:
    """Store the current request user for audit logging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)
        response = self.get_response(request)
        set_current_user(None)
        return response
