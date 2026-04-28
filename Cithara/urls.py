"""
URL configuration for Cithara project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from user.views import login_page, register_page, dashboard_page
from song.views import generate_page, dashboard_page

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Page routes
    path('login/',     login_page,     name='login'),
    path('register/',  register_page,  name='register'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('generate/',  generate_page,  name='generate'),

    # API routes
    path('api/', include('song.urls')),
    path('api/', include('user.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
