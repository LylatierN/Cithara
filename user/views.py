from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import SongCreator, SongListener
from .serializers import (
    SongCreatorListSerializer,
    SongCreatorDetailSerializer,
    SongCreatorCreateSerializer,
    SongListenerListSerializer,
    SongListenerDetailSerializer,
    SongListenerCreateSerializer
)
from song.serializers import SongListSerializer


class SongCreatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SongCreator CRUD operations.

    list: Get all song creators
    create: Create a new song creator
    retrieve: Get a specific song creator
    update: Update a song creator
    partial_update: Partially update a song creator
    destroy: Delete a song creator
    """
    queryset = SongCreator.objects.all().select_related(
        'user').prefetch_related('library')
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email',
                     'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'user__username']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return SongCreatorListSerializer
        elif self.action == 'create':
            return SongCreatorCreateSerializer
        return SongCreatorDetailSerializer

    @action(detail=True, methods=['get'])
    def library(self, request, pk=None):
        """Get all songs in the creator's library"""
        creator = self.get_object()
        songs = creator.library.all()
        serializer = SongListSerializer(songs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_song(self, request, pk=None):
        """Add a song to the creator's library"""
        creator = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response(
                {'error': 'song_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not creator.can_add_songs():
            return Response(
                {'error': 'Library is full (max 20 songs)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from song.models import Song
            song = Song.objects.get(pk=song_id)
            creator.library.add(song)
            return Response(
                {'message': 'Song added to library'},
                status=status.HTTP_200_OK
            )
        except Song.DoesNotExist:
            return Response(
                {'error': 'Song not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_song(self, request, pk=None):
        """Remove a song from the creator's library"""
        creator = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response(
                {'error': 'song_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from song.models import Song
            song = Song.objects.get(pk=song_id)
            creator.library.remove(song)
            return Response(
                {'message': 'Song removed from library'},
                status=status.HTTP_200_OK
            )
        except Song.DoesNotExist:
            return Response(
                {'error': 'Song not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SongListenerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SongListener CRUD operations.

    list: Get all song listeners
    create: Create a new song listener
    retrieve: Get a specific song listener
    update: Update a song listener
    partial_update: Partially update a song listener
    destroy: Delete a song listener
    """
    queryset = SongListener.objects.all().select_related('user')
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email',
                     'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'user__username']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return SongListenerListSerializer
        elif self.action == 'create':
            return SongListenerCreateSerializer
        return SongListenerDetailSerializer
