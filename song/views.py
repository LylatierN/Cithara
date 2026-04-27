from django.http import HttpResponseRedirect
from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Prompt, Song, SongShareLink, SongStatus
from .serializers import (
    PromptSerializer,
    SongListSerializer,
    SongDetailSerializer,
    SongCreateSerializer,
)
from .services import (
    check_concurrent_limit,
    check_library_limit,
    check_content,
    run_generation,
    check_generation_timeout,
    poll_and_maybe_retry,
)


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


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all().select_related('prompt').order_by('-created_at')
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'prompt']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return SongListSerializer
        elif self.action == 'create':
            return SongCreateSerializer
        return SongDetailSerializer

    def _get_audio_url(self, song, request):
        return song.url or (
            request.build_absolute_uri(song.audio_file.url)
            if song.audio_file else None
        )

    @action(detail=True, methods=['post'])
    def mark_ready(self, request, pk=None):
        song = self.get_object()
        song.status = 'READY'
        song.save()
        return Response(self.get_serializer(song).data)

    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        song = self.get_object()
        song.status = 'FAILED'
        song.save()
        return Response(self.get_serializer(song).data)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        song = self.get_object()

        if error := check_concurrent_limit():
            return Response({'error': error}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if error := check_library_limit(request.user):
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        if error := check_content(song.prompt):
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        result = run_generation(song)
        serializer = self.get_serializer(song)

        if song.status == SongStatus.FAILED:
            return Response(
                {**serializer.data, 'error': 'Song generation failed. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def check_status(self, request, pk=None):
        song = self.get_object()
        task_id = song.meta_data.get('task_id')

        if not task_id:
            return Response(
                {'error': 'No task_id found. Run /generate first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if check_generation_timeout(song):
            return Response({
                'task_id': task_id,
                'suno_status': 'FAILED',
                'audio_url': None,
                'song_status': song.status,
                'error': 'Generation timed out after 10 minutes.',
            }, status=status.HTTP_408_REQUEST_TIMEOUT)

        result, was_retried = poll_and_maybe_retry(song)

        if song.status == SongStatus.FAILED:
            return Response({
                'task_id': task_id,
                'suno_status': 'FAILED',
                'audio_url': None,
                'song_status': song.status,
                'error': 'Song generation failed after retry.',
            }, status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            'task_id': song.meta_data.get('task_id'),
            'suno_status': result.status,
            'audio_url': result.audio_url,
            'song_status': song.status,
            **(({'retried': True}) if was_retried else {}),
        })

    @action(detail=True, methods=['get'])
    def share(self, request, pk=None):
        song = self.get_object()
        audio_url = self._get_audio_url(song, request)
        if not audio_url:
            return Response(
                {'error': 'No audio available for this song yet.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        share_link, _ = SongShareLink.objects.get_or_create(song=song)
        player_url = request.build_absolute_uri(
            f'/api/songs/play/{share_link.token}/')
        return Response({'share_url': player_url})

    @action(
        detail=False,
        methods=['get'],
        url_path=r'play/(?P<token>[0-9a-f-]+)',
        permission_classes=[AllowAny],
    )
    def play(self, request, token=None):
        try:
            share_link = SongShareLink.objects.select_related(
                'song').get(token=token)
        except SongShareLink.DoesNotExist:
            return Response(
                {'error': 'Share link not found or has been revoked.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not share_link.is_valid():
            return Response(
                {'error': 'This share link has expired.'},
                status=status.HTTP_410_GONE,
            )
        audio_url = self._get_audio_url(share_link.song, request)
        if not audio_url:
            return Response(
                {'error': 'No audio available for this song yet.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'title': share_link.song.title, 'audio_url': audio_url})

    @action(
        detail=False,
        methods=['get'],
        url_path=r'download/(?P<token>[0-9a-f-]+)',
        permission_classes=[AllowAny],
    )
    def download(self, request, token=None):
        try:
            share_link = SongShareLink.objects.select_related(
                'song').get(token=token)
        except SongShareLink.DoesNotExist:
            return Response(
                {'error': 'Share link not found or has been revoked.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not share_link.is_valid():
            return Response(
                {'error': 'This share link has expired.'},
                status=status.HTTP_410_GONE,
            )
        audio_url = self._get_audio_url(share_link.song, request)
        if not audio_url:
            return Response(
                {'error': 'No audio available for this song yet.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return HttpResponseRedirect(audio_url)
