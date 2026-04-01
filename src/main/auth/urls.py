
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('api/set-csrf-token', views.set_csrf_token, name='set_csrf_token'),
    path('api/login', auth_views.LoginView.as_view(template_name="/frontend/src/auth/Login.vue"), name='login'),
    path('api/logout', auth_views.LogoutView.as_view(), name='logout'),
    path('api/user', views.user, name='user'),
    path('api/register', views.register, name='register'),
]
