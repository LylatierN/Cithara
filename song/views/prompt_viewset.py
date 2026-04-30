from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Prompt
from ..serializers import PromptSerializer, SongListSerializer


class PromptViewSet(viewsets.ModelViewSet):
    queryset = Prompt.objects.all().order_by('-created_at')
    serializer_class = PromptSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'mood']
    search_fields = ['title', 'description', 'occasion', 'lyrics']
    ordering_fields = ['created_at', 'title']

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        prompt = self.get_object()
        serializer = SongListSerializer(prompt.songs.all(), many=True)
        return Response(serializer.data)
