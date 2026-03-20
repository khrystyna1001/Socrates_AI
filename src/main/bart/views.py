import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book
from .serializers import BookSerializer
from .tasks import fetch_api_results

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-id')
    serializer_class = BookSerializer

    @action(detail=False, methods=['get'])
    def trigger_sync(self, request):
        fetch_api_results.delay(
            os.getenv("GUTENBERG_API_URL"),
            headers={
                'x-rapidapi-host': os.getenv("GUTENBERG_API_HOST"),
                'x-rapidapi-key': os.getenv("GUTENBERG_API_KEY")
            }
        )
        return Response({
            "status": "Sync chain started",
            "message": "The scout is fetching the API list. New books will appear in the list shortly."
        }, status=status.HTTP_202_ACCEPTED)