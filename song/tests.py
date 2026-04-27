from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from song.generation.base import GenerationResult


def auth_header(user):
    token = RefreshToken.for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {str(token.access_token)}'}


def make_user(username='testuser', password='pass1234'):
    auth_user = AuthUser.objects.create_user(
        username=username, password=password)
    from user.models import User as UserProfile
    UserProfile.objects.create(user=auth_user)
    return auth_user


class PromptSongCRUDTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.auth = auth_header(self.user)
        self.prompt_payload = {
            'title': 'Birthday Prompt',
            'description': 'Generate an upbeat birthday song',
            'occasion': 'Birthday Party',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': 'Happy birthday to you',
        }

    def test_prompt_crud(self):
        create_response = self.client.post(
            '/api/prompts/', self.prompt_payload, format='json', **self.auth)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        prompt_id = create_response.data['id']

        list_response = self.client.get('/api/prompts/', **self.auth)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data['count'], 1)

        update_response = self.client.patch(
            f'/api/prompts/{prompt_id}/',
            {'title': 'Updated Birthday Prompt'},
            format='json',
            **self.auth,
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            update_response.data['title'], 'Updated Birthday Prompt')

        delete_response = self.client.delete(
            f'/api/prompts/{prompt_id}/', **self.auth)
        self.assertEqual(delete_response.status_code,
                         status.HTTP_204_NO_CONTENT)

    def test_song_crud(self):
        prompt_response = self.client.post(
            '/api/prompts/', self.prompt_payload, format='json', **self.auth)
        self.assertEqual(prompt_response.status_code, status.HTTP_201_CREATED)
        prompt_id = prompt_response.data['id']

        song_payload = {
            'title': 'Birthday Song',
            'description': 'Generated song',
            'prompt': prompt_id,
            'status': 'GENERATING',
            'url': 'https://example.com/song.mp3',
            'meta_data': {'source': 'test'},
        }

        create_response = self.client.post(
            '/api/songs/', song_payload, format='json', **self.auth)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        list_after_create = self.client.get('/api/songs/', **self.auth)
        self.assertEqual(list_after_create.status_code, status.HTTP_200_OK)
        song_id = list_after_create.data['results'][0]['id']

        update_response = self.client.patch(
            f'/api/songs/{song_id}/',
            {'status': 'READY', 'title': 'Updated Song Title',
                'description': 'Updated description'},
            format='json',
            **self.auth,
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['status'], 'READY')
        self.assertEqual(update_response.data['title'], 'Updated Song Title')
        self.assertEqual(
            update_response.data['description'], 'Updated description')

        delete_response = self.client.delete(
            f'/api/songs/{song_id}/', **self.auth)
        self.assertEqual(delete_response.status_code,
                         status.HTTP_204_NO_CONTENT)


class SongShareDownloadTests(APITestCase):
    def setUp(self):
        self.user = make_user(username='shareuser')
        self.auth = auth_header(self.user)

        prompt_response = self.client.post('/api/prompts/', {
            'title': 'Share Download Prompt',
            'description': 'Test prompt',
            'occasion': 'Test',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': '',
        }, format='json', **self.auth)
        self.assertEqual(prompt_response.status_code, status.HTTP_201_CREATED)
        self.prompt_id = prompt_response.data['id']

        song_with_url = self.client.post('/api/songs/', {
            'title': 'Song With Audio',
            'description': 'Has a url',
            'prompt': self.prompt_id,
            'status': 'READY',
            'url': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
            'meta_data': {},
        }, format='json', **self.auth)
        self.assertEqual(song_with_url.status_code, status.HTTP_201_CREATED)
        self.song_with_url_id = song_with_url.data['id']

        song_no_url = self.client.post('/api/songs/', {
            'title': 'Song Without Audio',
            'description': 'No url yet',
            'prompt': self.prompt_id,
            'status': 'READY',
            'meta_data': {},
        }, format='json', **self.auth)
        self.assertEqual(song_no_url.status_code, status.HTTP_201_CREATED)
        self.song_no_url_id = song_no_url.data['id']

    def test_share_requires_authentication(self):
        response = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_share_returns_player_url_when_audio_exists(self):
        response = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('share_url', response.data)
        self.assertIn('/api/songs/play/', response.data['share_url'])

    def test_share_returns_404_when_no_audio(self):
        response = self.client.get(
            f'/api/songs/{self.song_no_url_id}/share/', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_play_accessible_without_authentication(self):
        share_response = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/', **self.auth)
        token = share_response.data['share_url'].rstrip('/').split('/')[-1]

        play_response = self.client.get(f'/api/songs/play/{token}/')
        self.assertEqual(play_response.status_code, status.HTTP_200_OK)
        self.assertIn('title', play_response.data)
        self.assertIn('audio_url', play_response.data)

    def test_play_does_not_expose_song_id(self):
        share_response = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/', **self.auth)
        token = share_response.data['share_url'].rstrip('/').split('/')[-1]

        play_response = self.client.get(f'/api/songs/play/{token}/')
        self.assertEqual(play_response.status_code, status.HTTP_200_OK)
        self.assertNotIn('id', play_response.data)
        self.assertNotIn('prompt', play_response.data)

    def test_play_returns_404_for_invalid_token(self):
        response = self.client.get(
            '/api/songs/play/00000000-0000-0000-0000-000000000000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_download_accessible_without_authentication(self):
        share_response = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/', **self.auth)
        token = share_response.data['share_url'].rstrip('/').split('/')[-1]

        download_response = self.client.get(
            f'/api/songs/download/{token}/', follow=False)
        self.assertEqual(download_response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            download_response['Location'],
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
        )

    def test_download_returns_404_for_invalid_token(self):
        response = self.client.get(
            '/api/songs/download/00000000-0000-0000-0000-000000000000/',
            follow=False,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_generates_same_token_on_repeated_calls(self):
        r1 = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/', **self.auth)
        r2 = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/', **self.auth)
        self.assertEqual(r1.data['share_url'], r2.data['share_url'])


class SongGenerationTimeoutTests(APITestCase):
    def setUp(self):
        self.user = make_user(username='timeoutuser')
        self.auth = auth_header(self.user)

        prompt_response = self.client.post('/api/prompts/', {
            'title': 'Timeout Test Prompt',
            'description': 'Test',
            'occasion': 'Test',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': '',
        }, format='json', **self.auth)
        self.prompt_id = prompt_response.data['id']

        song_response = self.client.post('/api/songs/', {
            'title': 'Timeout Song',
            'description': 'Will time out',
            'prompt': self.prompt_id,
            'status': 'READY',
            'meta_data': {},
        }, format='json', **self.auth)
        self.song_id = song_response.data['id']

    def _set_meta_data(self, started_at):
        from song.models import Song
        song = Song.objects.get(pk=self.song_id)
        song.meta_data = {
            'task_id': 'mock-task-12345',
            'generation_started_at': started_at.isoformat(),
        }
        song.save()

    def test_check_status_times_out_after_10_minutes(self):
        self._set_meta_data(started_at=timezone.now() - timedelta(minutes=11))

        response = self.client.get(
            f'/api/songs/{self.song_id}/check_status/', **self.auth)

        self.assertEqual(response.status_code, status.HTTP_408_REQUEST_TIMEOUT)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['suno_status'], 'FAILED')

        from song.models import Song
        song = Song.objects.get(pk=self.song_id)
        self.assertEqual(song.status, 'FAILED')
        self.assertTrue(song.meta_data.get('timeout'))

    def test_check_status_does_not_timeout_within_10_minutes(self):
        self._set_meta_data(started_at=timezone.now() - timedelta(minutes=5))

        response = self.client.get(
            f'/api/songs/{self.song_id}/check_status/', **self.auth)

        self.assertNotEqual(response.status_code,
                            status.HTTP_408_REQUEST_TIMEOUT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SongLibraryLimitTests(APITestCase):
    def setUp(self):
        self.user = make_user(username='libraryuser')
        self.auth = auth_header(self.user)
        self.profile = self.user.profile

        prompt_resp = self.client.post('/api/prompts/', {
            'title': 'Test Prompt',
            'description': 'desc',
            'occasion': 'Birthday',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': '',
        }, format='json', **self.auth)
        self.prompt_id = prompt_resp.data['id']

        song_resp = self.client.post('/api/songs/', {
            'title': 'Test Song',
            'description': '',
            'prompt': self.prompt_id,
            'status': 'READY',
            'meta_data': {},
        }, format='json', **self.auth)
        self.song_id = song_resp.data['id']

    def _fill_library(self):
        from song.models import Song, Prompt
        prompt = Prompt.objects.get(pk=self.prompt_id)
        for i in range(20):
            song = Song.objects.create(
                title=f'Library Song {i}',
                prompt=prompt,
                status='READY',
            )
            self.profile.library.add(song)

    def test_generate_blocked_when_library_full(self):
        self._fill_library()
        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('library is full', response.data['error'].lower())

    def test_generate_allowed_when_library_has_space(self):
        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_requires_authentication(self):
        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SongConcurrentGenerationLimitTests(APITestCase):
    def setUp(self):
        self.user = make_user(username='concurrentuser')
        self.auth = auth_header(self.user)

        prompt_resp = self.client.post('/api/prompts/', {
            'title': 'Concurrent Prompt',
            'description': 'desc',
            'occasion': 'Test',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': '',
        }, format='json', **self.auth)
        self.prompt_id = prompt_resp.data['id']

        song_resp = self.client.post('/api/songs/', {
            'title': 'Target Song',
            'description': '',
            'prompt': self.prompt_id,
            'status': 'READY',
            'meta_data': {},
        }, format='json', **self.auth)
        self.song_id = song_resp.data['id']

    def _create_generating_songs(self, count):
        from song.models import Song, Prompt
        prompt = Prompt.objects.get(pk=self.prompt_id)
        for i in range(count):
            Song.objects.create(
                title=f'Generating Song {i}',
                prompt=prompt,
                status='GENERATING',
            )

    def test_generate_blocked_when_3_already_generating(self):
        self._create_generating_songs(3)
        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
            **self.auth,
        )
        self.assertEqual(response.status_code,
                         status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.data)

    def test_generate_allowed_when_fewer_than_3_generating(self):
        self._create_generating_songs(2)
        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
            **self.auth,
        )
        self.assertNotEqual(response.status_code,
                            status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_allowed_when_none_generating(self):
        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
            **self.auth,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SongGenerationRetryTests(APITestCase):
    def setUp(self):
        self.user = make_user(username='retryuser')
        self.auth = auth_header(self.user)

        prompt_resp = self.client.post('/api/prompts/', {
            'title': 'Retry Prompt',
            'description': 'desc',
            'occasion': 'Test',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': '',
        }, format='json', **self.auth)
        self.prompt_id = prompt_resp.data['id']

        song_resp = self.client.post('/api/songs/', {
            'title': 'Retry Song',
            'description': '',
            'prompt': self.prompt_id,
            'status': 'READY',
            'meta_data': {},
        }, format='json', **self.auth)
        self.song_id = song_resp.data['id']

        from song.models import Song
        song = Song.objects.get(pk=self.song_id)
        song.meta_data = {
            'task_id': 'original-task-id',
            'generation_started_at': timezone.now().isoformat(),
        }
        song.save()

    @patch('song.services.get_song_generator')
    def test_check_status_retries_once_on_failure(self, mock_factory):
        mock_generator = MagicMock()
        mock_generator.get_status.return_value = GenerationResult(
            task_id='original-task-id',
            audio_url=None,
            status='FAILED',
            raw_response={'error': 'Suno failed'},
        )
        mock_generator.generate.return_value = GenerationResult(
            task_id='retry-task-id',
            audio_url=None,
            status='PENDING',
            raw_response={'retried': True},
        )
        mock_factory.return_value = mock_generator

        response = self.client.get(
            f'/api/songs/{self.song_id}/check_status/', **self.auth)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('retried'))
        self.assertEqual(response.data['task_id'], 'retry-task-id')

        from song.models import Song
        song = Song.objects.get(pk=self.song_id)
        self.assertTrue(song.meta_data.get('retried'))

    @patch('song.services.get_song_generator')
    def test_check_status_marks_failed_when_retry_also_fails(self, mock_factory):
        mock_generator = MagicMock()
        mock_generator.get_status.return_value = GenerationResult(
            task_id='original-task-id',
            audio_url=None,
            status='FAILED',
            raw_response={'error': 'Suno failed'},
        )
        mock_generator.generate.return_value = GenerationResult(
            task_id=None,
            audio_url=None,
            status='FAILED',
            raw_response={'error': 'Retry also failed'},
        )
        mock_factory.return_value = mock_generator

        response = self.client.get(
            f'/api/songs/{self.song_id}/check_status/', **self.auth)

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['suno_status'], 'FAILED')

        from song.models import Song
        song = Song.objects.get(pk=self.song_id)
        self.assertEqual(song.status, 'FAILED')

    @patch('song.services.get_song_generator')
    def test_check_status_does_not_retry_twice(self, mock_factory):
        from song.models import Song
        song = Song.objects.get(pk=self.song_id)
        song.meta_data['retried'] = True
        song.save()

        mock_generator = MagicMock()
        mock_generator.get_status.return_value = GenerationResult(
            task_id='original-task-id',
            audio_url=None,
            status='FAILED',
            raw_response={'error': 'Still failed'},
        )
        mock_factory.return_value = mock_generator

        self.client.get(
            f'/api/songs/{self.song_id}/check_status/', **self.auth)

        mock_generator.generate.assert_not_called()

        song.refresh_from_db()
        self.assertEqual(song.status, 'FAILED')


class SongGenerationFailureTests(APITestCase):
    def setUp(self):
        self.user = make_user(username='failureuser')
        self.auth = auth_header(self.user)

        prompt_resp = self.client.post('/api/prompts/', {
            'title': 'Test Prompt',
            'description': 'desc',
            'occasion': 'Birthday',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': '',
        }, format='json', **self.auth)
        self.prompt_id = prompt_resp.data['id']

        song_resp = self.client.post('/api/songs/', {
            'title': 'Test Song',
            'description': '',
            'prompt': self.prompt_id,
            'status': 'READY',
            'meta_data': {},
        }, format='json', **self.auth)
        self.song_id = song_resp.data['id']

    @patch('song.services.get_song_generator')
    def test_generate_returns_error_message_on_failure(self, mock_factory):
        mock_generator = MagicMock()
        mock_generator.generate.return_value = GenerationResult(
            task_id=None,
            audio_url=None,
            status='FAILED',
            raw_response={'error': 'Upstream API error'},
        )
        mock_factory.return_value = mock_generator

        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
            **self.auth,
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn('error', response.data)
        self.assertIn('failed', response.data['error'].lower())

        from song.models import Song
        song = Song.objects.get(pk=self.song_id)
        self.assertEqual(song.status, 'FAILED')

    @patch('song.services.get_song_generator')
    def test_generate_returns_200_on_success(self, mock_factory):
        mock_generator = MagicMock()
        mock_generator.generate.return_value = GenerationResult(
            task_id='task-abc',
            audio_url='https://example.com/song.mp3',
            status='SUCCESS',
            raw_response={'mock': True},
        )
        mock_factory.return_value = mock_generator

        response = self.client.post(
            f'/api/songs/{self.song_id}/generate/',
            format='json',
            **self.auth,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('error', response.data)
