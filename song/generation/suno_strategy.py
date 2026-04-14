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
        payload = {
            "customMode": False,
            "instrumental": False,
            "model": "V4",
            "prompt": f"{request.mood} {request.genre} song about {request.occasion}. {request.lyrics}".strip(),
            "callBackUrl": "https://example.com/callback",  # dummies urls
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

            # Audio URL is inside data.response.sunoData[0].audioUrl
            suno_data = record.get("response", {}).get("sunoData", [])
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
