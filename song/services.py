from django.utils import timezone

from .generation.content_filter import ContentFilter
from .generation.base import GenerationRequest
from .generation.factory import get_song_generator
from .models import Song, SongStatus

MAX_CONCURRENT_GENERATING = 3


def check_concurrent_limit():
    count = Song.objects.filter(status=SongStatus.GENERATING).count()
    if count >= MAX_CONCURRENT_GENERATING:
        return (
            f'The system is currently generating the maximum number of songs '
            f'({MAX_CONCURRENT_GENERATING}). Please wait and try again shortly.'
        )
    return None


def check_library_limit(user):
    try:
        if not user.profile.can_add_songs():
            return 'Your library is full (max 20 songs). Please delete a song before generating a new one.'
    except Exception:
        pass
    return None


def check_content(prompt):
    result = ContentFilter().check_prompt(prompt)
    if not result.passed:
        return result.reason
    return None


def build_gen_request(prompt):
    return GenerationRequest(
        prompt_id=prompt.id,
        title=prompt.title,
        occasion=prompt.occasion,
        genre=prompt.genre,
        mood=prompt.mood,
        voice_type=prompt.voice_type,
        lyrics=prompt.lyrics,
    )


def run_generation(song):
    generator = get_song_generator()
    result = generator.generate(build_gen_request(song.prompt))

    song.meta_data = result.raw_response or {}
    if result.task_id:
        song.meta_data['task_id'] = result.task_id
        song.meta_data['generation_started_at'] = timezone.now().isoformat()
    if result.audio_url:
        song.url = result.audio_url
    if result.status == 'SUCCESS':
        song.status = SongStatus.READY
    elif result.status == 'FAILED':
        song.status = SongStatus.FAILED

    song.save()
    return result


def check_generation_timeout(song):
    from datetime import datetime
    TIMEOUT_MINUTES = 10
    started_at_str = song.meta_data.get('generation_started_at')
    if not started_at_str:
        return False
    started_at = datetime.fromisoformat(started_at_str)
    elapsed = (timezone.now() - started_at).total_seconds()
    if elapsed > TIMEOUT_MINUTES * 60:
        song.status = SongStatus.FAILED
        song.meta_data['timeout'] = True
        song.save()
        return True
    return False


def poll_and_maybe_retry(song):
    generator = get_song_generator()
    result = generator.get_status(song.meta_data['task_id'])

    if result.status == 'FAILED' and not song.meta_data.get('retried'):
        return _retry_generation(song, generator)

    if result.audio_url:
        song.url = result.audio_url
    if result.status == 'SUCCESS':
        song.status = SongStatus.READY
    elif result.status == 'FAILED':
        song.status = SongStatus.FAILED

    song.meta_data.update(result.raw_response or {})
    song.save()
    return result, False


def _retry_generation(song, generator):
    retry_result = generator.generate(build_gen_request(song.prompt))
    song.meta_data['retried'] = True

    if retry_result.status == 'FAILED':
        song.status = SongStatus.FAILED
        song.meta_data.update(retry_result.raw_response or {})
        song.save()
        return retry_result, True

    if retry_result.task_id:
        song.meta_data['task_id'] = retry_result.task_id
        song.meta_data['generation_started_at'] = timezone.now().isoformat()
    if retry_result.audio_url:
        song.url = retry_result.audio_url
    if retry_result.status == 'SUCCESS':
        song.status = SongStatus.READY

    song.save()
    return retry_result, True
