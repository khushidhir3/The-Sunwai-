"""Accounts views — login, logout, role-based routing."""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    """Newspaper-styled login page."""
    if request.user.is_authenticated:
        return redirect('dashboard:front_page')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Log out and redirect to login."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile page."""
    return render(request, 'accounts/profile.html')
