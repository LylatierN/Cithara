from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from song.models import Song


class SongCreator(models.Model):
    """
    SongCreator profile that extends User.
    Owns a library of songs (0-20 songs).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='song_creator',
        primary_key=True
    )
    library = models.ManyToManyField(
        Song,
        related_name='creators',
        blank=True,
        help_text='Song library (max 20 songs)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Song Creator'
        verbose_name_plural = 'Song Creators'

    def __str__(self):
        return f"Creator: {self.user.username}"

    def song_count(self):
        """Return the number of songs in library"""
        return self.library.count()

    def can_add_songs(self):
        """Check if creator can add more songs (max 20)"""
        return self.library.count() < 20


class SongListener(models.Model):
    """
    SongListener profile that extends User.
    Can listen to songs but cannot create them.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='song_listener',
        primary_key=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Song Listener'
        verbose_name_plural = 'Song Listeners'

    def __str__(self):
        return f"Listener: {self.user.username}"
