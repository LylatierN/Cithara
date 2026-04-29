from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/',           views.LoginView.as_view(),
         name='api_login'),
    path('auth/logout/',          views.LogoutView.as_view(),           name='logout'),
    path('auth/refresh/',         TokenRefreshView.as_view(),
         name='token_refresh'),
    path('auth/google/',          views.GoogleAuthRedirectView.as_view(),
         name='google_auth'),
    path('auth/google/callback/', views.GoogleCallbackView.as_view(),
         name='google_callback'),
    path('auth/forgot-password/', views.ForgotPasswordView.as_view(),
         name='api_forgot_password'),
    path('auth/reset-password/',  views.ResetPasswordView.as_view(),
         name='api_reset_password'),
]
