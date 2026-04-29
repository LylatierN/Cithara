from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers

from song.models import Song
from song.serializers import SongListSerializer
from ..models import User
from .auth_user_serializer import AuthUserSerializer


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
