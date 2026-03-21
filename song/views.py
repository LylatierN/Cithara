from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Prompt, Song
from .serializers import (
    PromptSerializer,
    SongListSerializer,
    SongDetailSerializer,
    SongCreateSerializer
)


class PromptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Prompt CRUD operations.

    list: Get all prompts
    create: Create a new prompt
    retrieve: Get a specific prompt
    update: Update a prompt
    partial_update: Partially update a prompt
    destroy: Delete a prompt
    """
    queryset = Prompt.objects.all().order_by('-created_at')
    serializer_class = PromptSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'mood']
    search_fields = ['title', 'description', 'occasion', 'lyrics']
    ordering_fields = ['created_at', 'title']

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        """Get all songs generated from this prompt"""
        prompt = self.get_object()
        songs = prompt.songs.all()
        serializer = SongListSerializer(songs, many=True)
        return Response(serializer.data)


class SongViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Song CRUD operations.

    list: Get all songs
    create: Create a new song
    retrieve: Get a specific song
    update: Update a song
    partial_update: Partially update a song
    destroy: Delete a song
    """
    queryset = Song.objects.all().select_related('prompt').order_by('-created_at')
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'prompt']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return SongListSerializer
        elif self.action == 'create':
            return SongCreateSerializer
        return SongDetailSerializer

    @action(detail=True, methods=['post'])
    def mark_ready(self, request, pk=None):
        """Mark a song as ready"""
        song = self.get_object()
        song.status = 'READY'
        song.save()
        serializer = self.get_serializer(song)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Mark a song as failed"""
        song = self.get_object()
        song.status = 'FAILED'
        song.save()
        serializer = self.get_serializer(song)
        return Response(serializer.data)
