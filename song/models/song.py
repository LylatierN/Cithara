from django.db import models

from .prompt import Prompt
from .song_status import SongStatus


class Song(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meta_data = models.JSONField(default=dict, blank=True)
    audio_file = models.FileField(upload_to='songs/', blank=True, null=True)
    url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=SongStatus.choices,
        default=SongStatus.GENERATING,
    )
    prompt = models.ForeignKey(
        Prompt,
        on_delete=models.CASCADE,
        related_name='songs',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
