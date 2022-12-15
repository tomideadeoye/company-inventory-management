import uuid
from datetime import datetime, timezone

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.crypto import get_random_string

from .enums import USER_ROLE, TOKEN_TYPE, STATUS_OPTIONS
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    image = models.FileField(upload_to='users/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=USER_ROLE)
    workspace = models.ManyToManyField('workspaces.WorkSpace', related_name='user_workspace')    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    mac_address = models.CharField(max_length=20, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ('fullname',)

    def __str__(self):
        return self.email

    def save_last_login(self):
        self.last_login = datetime.now()
        self.save()

    @property
    def status(self):
        if self.is_active and self.verified:
            return 'ACTIVE'
        elif not self.is_active and self.verified:
            return 'ARCHIVE'
        elif not self.is_active and not self.verified:
            return "PENDING"


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True)
    token_type = models.CharField(
        max_length=100, choices=TOKEN_TYPE, default='ACCOUNT_VERIFICATION')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.user)} {self.token}"

    def is_valid(self):
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60 * 60)
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def verify_user(self):
        self.user.verified = True
        self.user.is_active = True
        self.user.save()

    def generate(self):
        if not self.token:
            self.token = get_random_string(120)
            self.save()

    def reset_user_password(self, password):
        self.user.set_password(password)
        self.user.save()
