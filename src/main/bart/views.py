from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import BARTQuery
from .serializers import BARTQuerySerializer
from .tasks import embed_user_prompt, read_user_prompt, invoke_bart_response


class BARTViewSet(viewsets.ModelViewSet):
    queryset = BARTQuery.objects.select_related("document").all().order_by("-id")
    serializer_class = BARTQuerySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(llm_response="")

        try:
            q_vec = embed_user_prompt(instance)
            context = read_user_prompt(instance, q_vec)
            invoke_bart_response(instance, context)
        except Exception as exc:
            return Response(
                {
                    "detail": "LLM service unavailable. Ensure Ollama is running and the model is pulled.",
                    "error": str(exc),
                    "query_id": instance.id,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        instance.refresh_from_db()

        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["get"])
    def result(self, request, pk=None):
        query = self.get_object()
        return Response(
            {
                "id": query.id,
                "document_id": query.document_id,
                "prompt": query.prompt,
                "llm_response": query.llm_response,
                "created_at": query.created_at,
                "is_ready": bool(query.llm_response),
            },
            status=status.HTTP_200_OK,
        )
