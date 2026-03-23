from django.contrib.auth.models import User as AuthUser
from django.db import models

from song.models import Song


class User(models.Model):
    """
    User profile that extends Django's built-in auth User.
    Can own a library of up to 20 songs.
    """

    user = models.OneToOneField(
        AuthUser,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    library = models.ManyToManyField(
        Song,
        related_name='users',
        blank=True,
        help_text='Song library (max 20 songs)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.user.username

    def song_count(self):
        return self.library.count()

    def can_add_songs(self):
        return self.library.count() < 20
