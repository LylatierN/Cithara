from rest_framework import status
from rest_framework.test import APITestCase


class PromptSongCRUDTests(APITestCase):
    def setUp(self):
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
            '/api/prompts/', self.prompt_payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        prompt_id = create_response.data['id']

        list_response = self.client.get('/api/prompts/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data['count'], 1)

        update_response = self.client.patch(
            f'/api/prompts/{prompt_id}/',
            {'title': 'Updated Birthday Prompt'},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            update_response.data['title'], 'Updated Birthday Prompt')

        delete_response = self.client.delete(f'/api/prompts/{prompt_id}/')
        self.assertEqual(delete_response.status_code,
                         status.HTTP_204_NO_CONTENT)

    def test_song_crud(self):
        prompt_response = self.client.post(
            '/api/prompts/', self.prompt_payload, format='json')
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
            '/api/songs/', song_payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        list_after_create = self.client.get('/api/songs/')
        self.assertEqual(list_after_create.status_code, status.HTTP_200_OK)
        song_id = list_after_create.data['results'][0]['id']

        list_response = self.client.get('/api/songs/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data['count'], 1)

        update_response = self.client.patch(
            f'/api/songs/{song_id}/',
            {'status': 'READY', 'title': 'Updated Song Title',
                'description': 'Updated description'},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['status'], 'READY')
        self.assertEqual(update_response.data['title'], 'Updated Song Title')
        self.assertEqual(
            update_response.data['description'], 'Updated description')

        delete_response = self.client.delete(f'/api/songs/{song_id}/')
        self.assertEqual(delete_response.status_code,
                         status.HTTP_204_NO_CONTENT)


class SongShareDownloadTests(APITestCase):
    """
    Tests for FR-12 (download) and FR-13 (share).
    We create a prompt and two songs:
      - one WITH a url  (happy path)
      - one WITHOUT a url (no audio yet — error path)
    """

    def setUp(self):
        # Create a prompt first — Song requires a linked Prompt (FK)
        prompt_response = self.client.post('/api/prompts/', {
            'title': 'Share Download Prompt',
            'description': 'Test prompt',
            'occasion': 'Test',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Female',
            'lyrics': '',
        }, format='json')
        self.assertEqual(prompt_response.status_code, status.HTTP_201_CREATED)
        self.prompt_id = prompt_response.data['id']

        # Song WITH a url — simulates a song that has been generated
        # This is the happy path for both share and download
        song_with_url = self.client.post('/api/songs/', {
            'title': 'Song With Audio',
            'description': 'Has a url',
            'prompt': self.prompt_id,
            'status': 'READY',
            'url': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
            'meta_data': {},
        }, format='json')
        self.assertEqual(song_with_url.status_code, status.HTTP_201_CREATED)
        self.song_with_url_id = song_with_url.data['id']

        # Song WITHOUT a url — simulates a song still generating (no audio yet)
        # This is the error path for both share and download
        song_no_url = self.client.post('/api/songs/', {
            'title': 'Song Without Audio',
            'description': 'No url yet',
            'prompt': self.prompt_id,
            'status': 'GENERATING',
            'meta_data': {},
        }, format='json')
        self.assertEqual(song_no_url.status_code, status.HTTP_201_CREATED)
        self.song_no_url_id = song_no_url.data['id']

    # ------------------------------------------------------------------ #
    # FR-13  share                                                         #
    # ------------------------------------------------------------------ #

    def test_share_returns_url_when_audio_exists(self):
        """
        FR-13 happy path:
        GET /api/songs/{id}/share/ on a song that has a url
        should return 200 with a 'share_url' key in the response body.
        """
        response = self.client.get(
            f'/api/songs/{self.song_with_url_id}/share/')

        # 200 OK — the endpoint found an audio URL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The response body must contain 'share_url'
        self.assertIn('share_url', response.data)

        # The value must actually be the URL we stored on the song
        self.assertEqual(
            response.data['share_url'],
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'
        )

    def test_share_returns_404_when_no_audio(self):
        """
        FR-13 error path:
        GET /api/songs/{id}/share/ on a song with no url and no audio_file
        should return 404 with an 'error' key explaining why.
        """
        response = self.client.get(
            f'/api/songs/{self.song_no_url_id}/share/')

        # 404 Not Found — no audio available yet
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # The response body must contain 'error'
        self.assertIn('error', response.data)

    # ------------------------------------------------------------------ #
    # FR-12  download                                                      #
    # ------------------------------------------------------------------ #

    def test_download_redirects_when_audio_exists(self):
        """
        FR-12 happy path:
        GET /api/songs/{id}/download/ on a song that has a url
        should return 302 (redirect) pointing to the audio file.

        We pass follow=False so the test client does NOT follow the redirect —
        we want to assert the redirect itself, not what's at the other end.
        """
        response = self.client.get(
            f'/api/songs/{self.song_with_url_id}/download/',
            follow=False,   # don't follow the redirect — inspect the 302 itself
        )

        # 302 Found — browser should follow this to download the file
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # The Location header tells the browser where to go
        # It must match the url we stored on the song
        self.assertEqual(
            response['Location'],
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'
        )

    def test_download_returns_404_when_no_audio(self):
        """
        FR-12 error path:
        GET /api/songs/{id}/download/ on a song with no url and no audio_file
        should return 404 with an 'error' key explaining why.
        """
        response = self.client.get(
            f'/api/songs/{self.song_no_url_id}/download/',
            follow=False,
        )

        # 404 Not Found — no audio to redirect to
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # The response body must contain 'error'
        self.assertIn('error', response.data)
