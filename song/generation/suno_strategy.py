import requests
from django.conf import settings
from .base import SongGeneratorStrategy, GenerationRequest, GenerationResult


class SunoSongGeneratorStrategy(SongGeneratorStrategy):

    BASE_URL = "https://api.sunoapi.org/api/v1"

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {settings.SUNO_API_KEY}",
            "Content-Type": "application/json",
        }

    def generate(self, request: GenerationRequest) -> GenerationResult:
        # Use non-custom mode (simplest) - only prompt required
        callback_url = getattr(settings, "SUNO_CALLBACK_URL", "http://localhost:8000/api/songs/callback/")
        payload = {
            "customMode": True,
            "instrumental": False,
            "model": "V4",
            "title": request.title,
            "prompt": request.lyrics.strip() or f"A {request.mood.lower()} {request.genre.lower()} song titled '{request.title}' for {request.occasion}.",
            "style": f"{request.mood} {request.genre} {request.voice_type}",
            "callBackUrl": callback_url,
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/generate",
                headers=self._get_headers(),
                json=payload,
                timeout=30,
            )
            data = response.json()

            if data is None:
                raise ValueError("Empty response from Suno API")

            if data.get("code") != 200:
                raise ValueError(
                    f"Suno API error: {data.get('msg', 'unknown error')}")

            task_id = data["data"]["taskId"]

            # Check if Suno rejected it immediately with an error status
            if data["data"].get("status") not in [None, "PENDING", "SUCCESS"]:
                return GenerationResult(
                    task_id=None,
                    audio_url=None,
                    status="FAILED",
                    raw_response={
                        "error": f"Suno rejected: {data['data'].get('status')}"},
                )

            return GenerationResult(
                task_id=task_id,
                audio_url=None,
                status="PENDING",
                raw_response=data,
            )

        except Exception as e:
            return GenerationResult(
                task_id=None,
                audio_url=None,
                status="FAILED",
                raw_response={"error": str(e)},
            )

    def get_status(self, task_id: str) -> GenerationResult:
        try:
            response = requests.get(
                f"{self.BASE_URL}/generate/record-info",
                headers=self._get_headers(),
                params={"taskId": task_id},
                timeout=30,
            )
            data = response.json()

            if data is None:
                raise ValueError("Empty response from Suno API")

            if data.get("code") != 200:
                raise ValueError(
                    f"Suno API error: {data.get('msg', 'unknown error')}")

            record = data["data"]
            suno_status = record.get("status", "PENDING")
            audio_url = None

            # Map any unknown Suno status to FAILED
            if suno_status not in ["SUCCESS", "PENDING", "FAILED"]:
                suno_status = "FAILED"

            # Audio URL is inside data.response.sunoData[0].audioUrl
            # response can be null (None) while PENDING, so use `or {}` not default=
            suno_data = (record.get("response") or {}).get("sunoData", [])
            if suno_data and suno_status == "SUCCESS":
                audio_url = suno_data[0].get("audioUrl")

            return GenerationResult(
                task_id=task_id,
                audio_url=audio_url,
                status=suno_status,
                raw_response=data,
            )

        except Exception as e:
            return GenerationResult(
                task_id=None,
                audio_url=None,
                status="FAILED",
                raw_response={"error": str(e)},
            )
