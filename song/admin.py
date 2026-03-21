from django.contrib import admin
from .models import Genre, Mood, SongStatus, Prompt, Song


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'mood', 'occasion', 'created_at')
    list_filter = ('genre', 'mood', 'created_at')
    search_fields = ('title', 'description', 'occasion', 'lyrics')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'occasion')
        }),
        ('Music Settings', {
            'fields': ('genre', 'mood', 'voice_type')
        }),
        ('Content', {
            'fields': ('lyrics',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'prompt', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['prompt']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'prompt')
        }),
        ('Song Details', {
            'fields': ('status', 'audio_file', 'url', 'meta_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
