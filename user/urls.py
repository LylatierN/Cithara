from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'creators', views.SongCreatorViewSet, basename='songcreator')
router.register(r'listeners', views.SongListenerViewSet,
                basename='songlistener')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
