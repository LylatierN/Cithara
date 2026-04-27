from .user_views import UserViewSet
from .auth_views import LoginView, LogoutView
from .google_views import GoogleAuthRedirectView, GoogleCallbackView
from .password_views import ForgotPasswordView, ResetPasswordView
from .template_views import login_page, register_page, dashboard_page
