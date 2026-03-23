from django.db import models


class Mood(models.TextChoices):
    HAPPY = 'HAPPY', 'Happy'
    SAD = 'SAD', 'Sad'
    ENERGETIC = 'ENERGETIC', 'Energetic'
    RELAXED = 'RELAXED', 'Relaxed'
