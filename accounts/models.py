"""
accounts — Custom User model with role-based access.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user with email login and court roles."""

    class Role(models.TextChoices):
        JUDGE = 'judge', 'Judge'
        REGISTRAR = 'registrar', 'Registrar'
        ADVOCATE = 'advocate', 'Advocate'
        LITIGANT = 'litigant', 'Litigant'
        ADMIN = 'admin', 'Admin'

    username = None  # Remove username field
    email = models.EmailField('email address', unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LITIGANT,
    )
    bar_number = models.CharField(
        max_length=50, blank=True,
        help_text='Bar Council enrollment number (advocates only)',
    )
    court_designation = models.CharField(
        max_length=200, blank=True,
        help_text='Court/bench designation (judges only)',
    )
    phone = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'

    @property
    def display_name(self):
        if self.role == self.Role.JUDGE:
            return f'Hon. {self.get_full_name()}'
        elif self.role == self.Role.ADVOCATE:
            return f'Adv. {self.get_full_name()}'
        return self.get_full_name()

    @property
    def is_judge(self):
        return self.role == self.Role.JUDGE

    @property
    def is_registrar(self):
        return self.role == self.Role.REGISTRAR

    @property
    def is_advocate(self):
        return self.role == self.Role.ADVOCATE

    @property
    def is_litigant(self):
        return self.role == self.Role.LITIGANT
