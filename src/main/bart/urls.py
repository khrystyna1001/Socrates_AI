# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BARTViewSet

router = DefaultRouter()

router.register(r'docs', BARTViewSet, basename='BART')

urlpatterns = [
    path('', include(router.urls)),
]