from django.db import models
from documents.models import Document


class BARTQuery(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="queries",
    )
    prompt = models.TextField(max_length=2000)
    response = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Query {self.id} for document {self.document_id}"

    def set_response(self, text: str):
        self.response = text
        self.save(update_fields=["response"])
