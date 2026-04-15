from rest_framework import serializers
from .models import Document, DocumentText, DocumentTextChunk, DocumentChunkEmbedding

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ("owner", "minio_bucket", "process_state", "created_at", "updated_at")


class DocumentTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentText
        fields = "__all__"


class DocumentTextChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTextChunk
        fields = "__all__"


class DocumentChunkEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunkEmbedding
        fields = "__all__"
