from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationRequest:
    """Data passed INTO the strategy"""
    prompt_id: int
    title: str
    occasion: str
    genre: str
    mood: str
    voice_type: str
    lyrics: str


@dataclass
class GenerationResult:
    """Data returned FROM the strategy"""
    task_id: Optional[str]      # Suno's taskId (None for mock)
    audio_url: Optional[str]    # Direct URL to audio
    status: str                 # e.g. PENDING, SUCCESS, FAILED
    raw_response: Optional[dict] = None  # full API response for debugging


class SongGeneratorStrategy(ABC):
    """Abstract base — all strategies must implement these two methods"""

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Start a generation job. Returns immediately with a task_id or result."""
        ...

    @abstractmethod
    def get_status(self, task_id: str) -> GenerationResult:
        """Poll the status of a previously started generation job."""
        ...
