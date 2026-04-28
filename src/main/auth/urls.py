
from . import views
from django.urls import path

from .views import CookieTokenRefreshView, MeView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenVerifyView
)


urlpatterns = [
    path('api/set-csrf-token', views.set_csrf_token, name='set_csrf_token'),
    path('api/login', views.login_view, name='login'),
    path('api/logout', views.logout_view, name='logout'),
    path('api/register', views.register, name='register'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/profile/', MeView.as_view(), name='me'),

]
