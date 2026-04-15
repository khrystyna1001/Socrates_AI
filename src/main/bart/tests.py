from django.test import TestCase
from .model import BARTQuery, EmbeddingModel, LLMModel, TextSplitter
from faker import Faker
from faker_file.providers.pdf_file import PdfFileProvider
from faker_file.providers.pdf_file.generators.pdfkit_generator import (
    PdfkitPdfGenerator,
)

# Create your tests here.

fake = Faker()
fake.add_provider(PdfFileProvider)

class BARTQueryTestCase(TestCase):
    def setUp(self):
        BARTQuery.objects.create(
            document=fake.pdf_file(pdf_generator_cls=PdfkitPdfGenerator), 
            query="What is MRP?"
        )
        EmbeddingModel.objects.create()
        LLMModel.objects.create()
        TextSplitter.objects.create()

    def test_queries_can_speak(self):
        query = BARTQuery.objects.get(query="What is MRP?")
        self.assertEqual(llm_response, "")