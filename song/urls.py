from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'prompts', views.PromptViewSet, basename='prompt')
router.register(r'songs', views.SongViewSet, basename='song')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
