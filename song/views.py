from django.http import HttpResponseRedirect
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
from .generation.factory import get_song_generator
from .generation.base import GenerationRequest
from .models import SongStatus
from .generation.content_filter import ContentFilter


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

    def _get_audio_url(self, song, request):
        """Return the audio URL for a song, or None if unavailable."""
        return song.url or (
            request.build_absolute_uri(song.audio_file.url)
            if song.audio_file else None
        )

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

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Trigger song generation using the active strategy"""
        song = self.get_object()
        prompt = song.prompt

        # filter
        filter_result = ContentFilter().check_prompt(prompt)
        if not filter_result.passed:
            return Response(
                {'error': filter_result.reason},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build the request object
        gen_request = GenerationRequest(
            prompt_id=prompt.id,
            title=prompt.title,
            occasion=prompt.occasion,
            genre=prompt.genre,
            mood=prompt.mood,
            voice_type=prompt.voice_type,
            lyrics=prompt.lyrics,
        )

        # Get strategy from factory (reads GENERATOR_STRATEGY setting)
        generator = get_song_generator()
        result = generator.generate(gen_request)

        # Update the song with results
        song.meta_data = result.raw_response or {}
        if result.task_id:
            song.meta_data['task_id'] = result.task_id
        if result.audio_url:
            song.url = result.audio_url
        if result.status in ('SUCCESS',):
            song.status = SongStatus.READY
        elif result.status == 'FAILED':
            song.status = SongStatus.FAILED
        # else stays GENERATING

        song.save()
        serializer = self.get_serializer(song)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def check_status(self, request, pk=None):
        """Poll Suno for the latest generation status"""
        song = self.get_object()
        task_id = song.meta_data.get('task_id')

        if not task_id:
            return Response(
                {'error': 'No task_id found. Run /generate first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        generator = get_song_generator()
        result = generator.get_status(task_id)

        if result.audio_url:
            song.url = result.audio_url
        if result.status == 'SUCCESS':
            song.status = SongStatus.READY
        elif result.status == 'FAILED':
            song.status = SongStatus.FAILED

        song.meta_data.update(result.raw_response or {})
        song.save()

        return Response({
            'task_id': task_id,
            'suno_status': result.status,
            'audio_url': result.audio_url,
            'song_status': song.status,
        })

    @action(detail=True, methods=['get'])
    def share(self, request, pk=None):
        song = self.get_object()
        url = self._get_audio_url(song, request)
        if not url:
            return Response(
                {'error': 'No audio available for this song yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'share_url': url})

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        song = self.get_object()
        url = self._get_audio_url(song, request)
        if not url:
            return Response(
                {'error': 'No audio available for this song yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return HttpResponseRedirect(url)
