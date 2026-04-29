from rest_framework import serializers
from ..models import Song


class SongListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for song lists"""
    prompt_title = serializers.CharField(source='prompt.title', read_only=True)

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'status', 'prompt_title',
            'created_at', 'url'
        ]
