from django.db import models
from django.contrib.auth.models import User


class Genre(models.TextChoices):
    POP = 'POP', 'Pop'
    ROCK = 'ROCK', 'Rock'
    JAZZ = 'JAZZ', 'Jazz'
    CLASSICAL = 'CLASSICAL', 'Classical'
    RNB = 'RNB', 'R&B'


class Mood(models.TextChoices):
    HAPPY = 'HAPPY', 'Happy'
    SAD = 'SAD', 'Sad'
    ENERGETIC = 'ENERGETIC', 'Energetic'
    RELAXED = 'RELAXED', 'Relaxed'


class SongStatus(models.TextChoices):
    GENERATING = 'GENERATING', 'Generating'
    READY = 'READY', 'Ready'
    FAILED = 'FAILED', 'Failed'


class Prompt(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    occasion = models.CharField(max_length=255)
    genre = models.CharField(max_length=20, choices=Genre.choices)
    mood = models.CharField(max_length=20, choices=Mood.choices)
    voice_type = models.CharField(max_length=100)
    lyrics = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Song(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meta_data = models.JSONField(default=dict, blank=True)
    audio_file = models.FileField(upload_to='songs/', blank=True, null=True)
    url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20, choices=SongStatus.choices, default=SongStatus.GENERATING)
    prompt = models.ForeignKey(
        Prompt, on_delete=models.CASCADE, related_name='songs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tit
