from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']
