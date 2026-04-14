from .base import SongGeneratorStrategy, GenerationRequest, GenerationResult


class MockSongGeneratorStrategy(SongGeneratorStrategy):
    """
    Offline strategy for development/testing.
    Returns predictable dummy data without any network calls.
    """

    MOCK_AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    MOCK_TASK_ID = "mock-task-12345"

    def generate(self, request: GenerationRequest) -> GenerationResult:
        print(
            f"[MockStrategy] Generating song for prompt_id={request.prompt_id}")
        print(
            f"  Title: {request.title}, Genre: {request.genre}, Mood: {request.mood}")

        return GenerationResult(
            task_id=self.MOCK_TASK_ID,
            audio_url=self.MOCK_AUDIO_URL,
            status="SUCCESS",
            raw_response={
                "mock": True,
                "title": request.title,
                "genre": request.genre,
                "mood": request.mood,
            }
        )

    def get_status(self, task_id: str) -> GenerationResult:
        print(f"[MockStrategy] Checking status for task_id={task_id}")

        return GenerationResult(
            task_id=task_id,
            audio_url=self.MOCK_AUDIO_URL,
            status="SUCCESS",
            raw_response={"mock": True, "task_id": task_id}
        )
