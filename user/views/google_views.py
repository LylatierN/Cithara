from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User


class GoogleAuthRedirectView(APIView):
    def get(self, request):
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': 'http://localhost:8000/api/auth/google/callback/',
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
        }
        from urllib.parse import urlencode
        google_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + \
            urlencode(params)
        from django.shortcuts import redirect
        return redirect(google_url)


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)

        import requests as http_requests
        token_response = http_requests.post('https://oauth2.googleapis.com/token', data={
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': 'http://localhost:8000/api/auth/google/callback/',
            'grant_type': 'authorization_code',
        })
        token_data = token_response.json()

        if 'error' in token_data:
            return Response({'error': token_data['error']}, status=status.HTTP_400_BAD_REQUEST)

        id_info = id_token.verify_oauth2_token(
            token_data['id_token'],
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        email = id_info.get('email')
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')

        auth_user, created = AuthUser.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': first_name,
                      'last_name': last_name}
        )

        if created:
            auth_user.set_unusable_password()
            auth_user.save()
            User.objects.create(user=auth_user)

        refresh = RefreshToken.for_user(auth_user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': auth_user.pk,
            'username': auth_user.username,
            'created': created,
        })
