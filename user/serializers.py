from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SongCreator, SongListener
from song.models import Song
from song.serializers import SongListSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class SongCreatorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for SongCreator lists"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    song_count = serializers.SerializerMethodField()
    can_add_songs = serializers.SerializerMethodField()

    class Meta:
        model = SongCreator
        fields = ['user', 'username', 'email',
                  'song_count', 'can_add_songs', 'created_at']

    def get_song_count(self, obj):
        return obj.song_count()

    def get_can_add_songs(self, obj):
        return obj.can_add_songs()


class SongCreatorDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual SongCreator"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    library = SongListSerializer(many=True, read_only=True)
    library_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Song.objects.all(),
        source='library',
        write_only=True,
        required=False
    )
    song_count = serializers.SerializerMethodField()
    can_add_songs = serializers.SerializerMethodField()

    class Meta:
        model = SongCreator
        fields = [
            'user', 'user_id', 'library', 'library_ids',
            'song_count', 'can_add_songs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_song_count(self, obj):
        return obj.song_count()

    def get_can_add_songs(self, obj):
        return obj.can_add_songs()

    def validate_library(self, value):
        """Validate that library doesn't exceed 20 songs"""
        if len(value) > 20:
            raise serializers.ValidationError("Library cannot exceed 20 songs")
        return value


class SongCreatorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SongCreator"""

    class Meta:
        model = SongCreator
        fields = ['user', 'library']

    def validate_library(self, value):
        """Validate that library doesn't exceed 20 songs"""
        if len(value) > 20:
            raise serializers.ValidationError("Library cannot exceed 20 songs")
        return value


class SongListenerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for SongListener lists"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SongListener
        fields = ['user', 'username', 'email', 'created_at']


class SongListenerDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual SongListener"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = SongListener
        fields = ['user', 'user_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SongListenerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SongListener"""

    class Meta:
        model = SongListener
        fields = ['user']
