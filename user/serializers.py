from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers

from song.models import Song
from song.serializers import SongListSerializer
from .models import User


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    song_count = serializers.SerializerMethodField()
    can_add_songs = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user', 'username', 'email',
                  'song_count', 'can_add_songs', 'created_at']

    def get_song_count(self, obj):
        return obj.song_count()

    def get_can_add_songs(self, obj):
        return obj.can_add_songs()


class UserDetailSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=AuthUser.objects.all(),
        source='user',
        write_only=True,
    )
    library = SongListSerializer(many=True, read_only=True)
    library_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Song.objects.all(),
        source='library',
        write_only=True,
        required=False,
    )
    song_count = serializers.SerializerMethodField()
    can_add_songs = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user', 'user_id', 'library', 'library_ids',
            'song_count', 'can_add_songs',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_song_count(self, obj):
        return obj.song_count()

    def get_can_add_songs(self, obj):
        return obj.can_add_songs()

    def validate_library(self, value):
        if len(value) > 20:
            raise serializers.ValidationError('Library cannot exceed 20 songs')
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(write_only=True, required=True)
    first_name = serializers.CharField(
        write_only=True, required=False, default='')
    last_name = serializers.CharField(
        write_only=True, required=False, default='')
    library = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Song.objects.all(), required=False
    )

    def validate_email(self, value):
        if AuthUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'An account with that email already exists.'
            )
        return value

    class Meta:
        model = User
        fields = ['user', 'username', 'password', 'email',
                  'first_name', 'last_name', 'library']
        read_only_fields = ['user']

    def validate_username(self, value):
        if AuthUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'A user with that username already exists.')
        return value

    def validate_library(self, value):
        if len(value) > 20:
            raise serializers.ValidationError(
                'Library cannot exceed 20 songs.')
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        library = validated_data.pop('library', [])

        auth_user = AuthUser.objects.create_user(
            username=username,
            password=password,  # create_user calls set_password internally
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        profile = User.objects.create(user=auth_user)
        if library:
            profile.library.set(library)
        return profile
