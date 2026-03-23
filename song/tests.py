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
