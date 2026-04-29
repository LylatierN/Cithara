from django.conf import settings
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


class GoogleAuthRedirectView(APIView):
    permission_classes = [AllowAny]

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
