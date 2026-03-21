from django.contrib import admin
from .models import SongCreator, SongListener


@admin.register(SongCreator)
class SongCreatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'song_count', 'created_at')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('library',)
    readonly_fields = ('created_at', 'updated_at',
                       'song_count', 'can_add_songs')

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Library', {
            'fields': ('library', 'song_count', 'can_add_songs')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def song_count(self, obj):
        """Display song count in list"""
        return obj.song_count()
    song_count.short_description = 'Songs in Library'


@admin.register(SongListener)
class SongListenerAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
