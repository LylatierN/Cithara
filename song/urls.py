from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import generate_page

router = DefaultRouter()
router.register(r'prompts', views.PromptViewSet, basename='prompt')
router.register(r'songs', views.SongViewSet, basename='song')

urlpatterns = [
    path('', include(router.urls)),
]
