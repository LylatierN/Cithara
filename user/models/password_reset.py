import uuid
from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone


class PasswordResetToken(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at
