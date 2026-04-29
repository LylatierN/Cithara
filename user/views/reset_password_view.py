from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from ..models import PasswordResetToken


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token_value = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token_value or not new_password:
            return Response({'error': 'Token and new_password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = PasswordResetToken.objects.get(token=token_value)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        if not token.is_valid():
            return Response({'error': 'Token has expired or already been used'}, status=status.HTTP_400_BAD_REQUEST)

        token.user.set_password(new_password)
        token.user.save()
        token.used = True
        token.save()

        return Response({'message': 'Password reset successfully'})
