from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BARTQuery
from .serializers import BARTQuerySerializer
from .tasks import generate_bart_response_task


class BARTViewSet(viewsets.ModelViewSet):
    queryset = BARTQuery.objects.select_related("document").all().order_by("-id")
    serializer_class = BARTQuerySerializer

    def perform_create(self, serializer):
        instance = serializer.save(response="")
        generate_bart_response_task.delay(instance.id)

    @action(detail=True, methods=["get"])
    def result(self, request, pk=None):
        query = self.get_object()
        return Response(
            {
                "id": query.id,
                "document_id": query.document_id,
                "prompt": query.prompt,
                "response": query.response,
                "created_at": query.created_at,
                "is_ready": bool(query.response),
            },
            status=status.HTTP_200_OK,
        )
