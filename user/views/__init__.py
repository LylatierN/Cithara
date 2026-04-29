from .user_views import UserViewSet
from .auth_views import LoginView, LogoutView
from .google_auth_redirect_view import GoogleAuthRedirectView
from .google_callback_view import GoogleCallbackView
from .forgot_password_view import ForgotPasswordView
from .reset_password_view import ResetPasswordView
from .template_views import login_page, register_page, dashboard_page, forgot_password_page, reset_password_page
