from rest_framework import serializers
from ..models import Prompt, Song
from .prompt_serializer import PromptSerializer


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
