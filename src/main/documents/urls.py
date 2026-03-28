# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()

router.register(r'docs', DocumentViewSet, basename='Docs')

urlpatterns = [
    path('', include(router.urls)),
]