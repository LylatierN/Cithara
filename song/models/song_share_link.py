import uuid
from django.db import models
from .song import Song


class SongShareLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    song = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name='share_link',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        from django.utils import timezone
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def __str__(self):
        return f'ShareLink({self.token}) → {self.song.title}'
