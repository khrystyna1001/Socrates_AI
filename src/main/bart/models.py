from django.db import models
from pgvector.django import VectorField

# Create your models here.
class Book(models.Model):
    content = models.TextField()
    page_number = models.IntegerField()
    embedding = VectorField(dimensions=384, null=True, blank=True)

    def __str__(self):
        return f"Book {self.source_id} - Page {self.page_number}"