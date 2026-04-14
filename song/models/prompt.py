from django.db import models

from .genre import Genre
from .mood import Mood


class Prompt(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    occasion = models.CharField(max_length=255)
    genre = models.CharField(max_length=20, choices=Genre.choices)
    mood = models.CharField(max_length=20, choices=Mood.choices)
    voice_type = models.CharField(max_length=100)
    lyrics = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
