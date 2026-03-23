from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'song_count_display',
                    'can_add_songs_display', 'created_at')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('library',)
    readonly_fields = ('created_at', 'updated_at',
                       'song_count_display', 'can_add_songs_display')

    fieldsets = (
        ('Account', {
            'fields': ('user',)
        }),
        ('Library', {
            'fields': ('library', 'song_count_display', 'can_add_songs_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def song_count_display(self, obj):
        return obj.song_count()
    song_count_display.short_description = 'Songs in Library'

    def can_add_songs_display(self, obj):
        return obj.can_add_songs()
    can_add_songs_display.short_description = 'Can Add Songs'
