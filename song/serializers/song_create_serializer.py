from rest_framework import serializers
from ..models import Song


class SongCreateSerializer(serializers.ModelSerializer):
    meta_data = serializers.JSONField(default=dict, required=False)

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'description', 'prompt',
            'status', 'url', 'meta_data'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data.setdefault('status', 'GENERATING')
        validated_data.setdefault('meta_data', {})
        return super().create(validated_data)
