from django.db import models


class Genre(models.TextChoices):
    POP = 'POP', 'Pop'
    ROCK = 'ROCK', 'Rock'
    JAZZ = 'JAZZ', 'Jazz'
    CLASSICAL = 'CLASSICAL', 'Classical'
    RNB = 'RNB', 'R&B'
