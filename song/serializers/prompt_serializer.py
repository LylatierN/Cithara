from rest_framework import serializers
from ..models import Prompt


class PromptSerializer(serializers.ModelSerializer):
    """Serializer for Prompt model"""
    songs_count = serializers.SerializerMethodField()

    class Meta:
        model = Prompt
        fields = [
            'id', 'title', 'description', 'occasion',
            'genre', 'mood', 'voice_type', 'lyrics',
            'created_at', 'updated_at', 'songs_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_songs_count(self, obj):
        """Return count of songs generated from this prompt"""
        return obj.songs.count()
