from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import uuid

class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):  # Add this - makes Django admin much nicer
        return self.name
    
    class Meta:  # Add this - better pluralization
        verbose_name_plural = "Businesses"

class UserManager(BaseUserManager):
    def create_user(self, email: str, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    is_business_admin = models.BooleanField(default=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_users', null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Role(models.TextChoices):
        ADVISOR = 'ADVISOR', 'Financial Advisor'
        PARA_PLANNER = 'PARA_PLANNER', 'Paraplanner'
        ADMIN_STAFF = 'ADMIN_STAFF', 'Administrative Staff'
        COMPLIANCE = 'COMPLIANCE', 'Compliance Officer'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADVISOR)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']