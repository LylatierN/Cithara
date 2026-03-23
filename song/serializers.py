from rest_framework import serializers
from .models import Prompt, Song


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


class SongListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for song lists"""
    prompt_title = serializers.CharField(source='prompt.title', read_only=True)

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'status', 'prompt_title',
            'created_at', 'url'
        ]


class SongDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual song"""
    prompt = PromptSerializer(read_only=True)
    prompt_id = serializers.PrimaryKeyRelatedField(
        queryset=Prompt.objects.all(),
        source='prompt',
        write_only=True
    )

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'description', 'meta_data',
            'audio_file', 'url', 'status',
            'prompt', 'prompt_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SongCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating songs"""

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'description', 'prompt',
            'status', 'url', 'meta_data'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create song with default generating status"""
        if 'status' not in validated_data:
            validated_data['status'] = 'GENERATING'
        return super().create(validated_data)
