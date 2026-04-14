from django.conf import settings
from .base import SongGeneratorStrategy
from .mock_strategy import MockSongGeneratorStrategy
from .suno_strategy import SunoSongGeneratorStrategy


def get_song_generator() -> SongGeneratorStrategy:
    """
    Reads GENERATOR_STRATEGY from Django settings (set via env var).
    Returns the correct strategy instance.
    This is the ONLY place in the codebase that decides which strategy to use.
    """
    strategy = getattr(settings, "GENERATOR_STRATEGY", "mock").lower()

    if strategy == "suno":
        return SunoSongGeneratorStrategy()
    else:
        return MockSongGeneratorStrategy()
