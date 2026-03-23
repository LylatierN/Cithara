from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from song.serializers import SongListSerializer
from .models import User
from .serializers import UserCreateSerializer, UserDetailSerializer, UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.

    list:           GET    /api/users/
    create:         POST   /api/users/
    retrieve:       GET    /api/users/{id}/
    update:         PUT    /api/users/{id}/
    partial_update: PATCH  /api/users/{id}/
    destroy:        DELETE /api/users/{id}/
    library:        GET    /api/users/{id}/library/
    add_song:       POST   /api/users/{id}/add_song/
    remove_song:    POST   /api/users/{id}/remove_song/
    """

    queryset = (
        User.objects.all()
        .select_related('user')
        .prefetch_related('library')
        .order_by('user__username')
    )
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email',
                     'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'user__username']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return UserDetailSerializer

    @action(detail=True, methods=['get'])
    def library(self, request, pk=None):
        user_obj = self.get_object()
        serializer = SongListSerializer(user_obj.library.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_song(self, request, pk=None):
        user_obj = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'song_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not user_obj.can_add_songs():
            return Response({'error': 'Library is full (max 20 songs)'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from song.models import Song
            song = Song.objects.get(pk=song_id)
            user_obj.library.add(song)
            return Response({'message': 'Song added to library'}, status=status.HTTP_200_OK)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_song(self, request, pk=None):
        user_obj = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'song_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from song.models import Song
            song = Song.objects.get(pk=song_id)
            user_obj.library.remove(song)
            return Response({'message': 'Song removed from library'}, status=status.HTTP_200_OK)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)
