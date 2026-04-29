from datetime import timedelta

from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from ..models import PasswordResetToken


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_user = AuthUser.objects.get(email=email)
        except AuthUser.DoesNotExist:
            return Response({'message': 'If that email exists, a reset link has been sent'})

        PasswordResetToken.objects.filter(user=auth_user, used=False).delete()

        token = PasswordResetToken.objects.create(
            user=auth_user,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        reset_link = f'http://localhost:8000/reset-password/?token={token.token}'

        send_mail(
            subject='Cithara - Password Reset',
            message=f'Click the link to reset your password:\n\n{reset_link}\n\nThis link expires in 1 hour.',
            from_email='noreply@cithara.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'If that email exists, a reset link has been sent'})
