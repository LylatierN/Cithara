from rest_framework import status
from rest_framework.test import APITestCase


class UserDomainCRUDTests(APITestCase):
    def setUp(self):
        self.prompt_payload = {
            'title': 'Prompt for user tests',
            'description': 'Prompt description',
            'occasion': 'Birthday',
            'genre': 'POP',
            'mood': 'HAPPY',
            'voice_type': 'Male',
            'lyrics': 'Some lyrics',
        }

    def _create_song(self):
        prompt_response = self.client.post(
            '/api/prompts/', self.prompt_payload, format='json')
        self.assertEqual(prompt_response.status_code, status.HTTP_201_CREATED)

        song_payload = {
            'title': 'Library Song',
            'description': 'Song for library testing',
            'prompt': prompt_response.data['id'],
            'status': 'GENERATING',
            'meta_data': {'origin': 'test'},
        }
        song_response = self.client.post(
            '/api/songs/', song_payload, format='json')
        self.assertEqual(song_response.status_code, status.HTTP_201_CREATED)
        return song_response.data['id']

    def test_user_crud(self):
        # Create
        create_response = self.client.post(
            '/api/users/',
            {'username': 'testuser1', 'password': 'securepass123',
             'email': 'testuser1@example.com'},
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        user_id = create_response.data['user']

        # Authenticate
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'testuser1', 'password': 'securepass123'},
            format='json',
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + login_response.data['access'])

        # List
        list_response = self.client.get('/api/users/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data['count'], 1)

        # Retrieve
        retrieve_response = self.client.get(f'/api/users/{user_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)

        # Update
        update_response = self.client.patch(
            f'/api/users/{user_id}/',
            {'library': []},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Delete
        delete_response = self.client.delete(f'/api/users/{user_id}/')
        self.assertEqual(delete_response.status_code,
                         status.HTTP_204_NO_CONTENT)

    def test_user_library_actions(self):
        # Create user profile
        create_response = self.client.post(
            '/api/users/',
            {'username': 'testuser2', 'password': 'securepass123',
             'email': 'testuser2@example.com'},
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        user_id = create_response.data['user']

        # Authenticate
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'testuser2', 'password': 'securepass123'},
            format='json',
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + login_response.data['access'])

        song_id = self._create_song()

        # Add song to library
        add_response = self.client.post(
            f'/api/users/{user_id}/add_song/',
            {'song_id': song_id},
            format='json',
        )
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)

        # Check library
        library_response = self.client.get(f'/api/users/{user_id}/library/')
        self.assertEqual(library_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(library_response.data), 1)

        # Remove song from library
        remove_response = self.client.post(
            f'/api/users/{user_id}/remove_song/',
            {'song_id': song_id},
            format='json',
        )
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)

        library_after = self.client.get(f'/api/users/{user_id}/library/')
        self.assertEqual(len(library_after.data), 0)
