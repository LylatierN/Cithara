from rest_framework import serializers
from ..models import User


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
