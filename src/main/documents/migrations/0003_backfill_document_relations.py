import django.db.models.deletion
from django.db import migrations, models


def backfill_document_relations(apps, schema_editor):
    Document = apps.get_model("documents", "Document")
    DocumentPages = apps.get_model("documents", "DocumentPages")
    DocumentText = apps.get_model("documents", "DocumentText")
    DocumentTextChunk = apps.get_model("documents", "DocumentTextChunk")
    DocumentChunk = apps.get_model("documents", "DocumentChunk")

    DocumentPages.objects.filter(document__isnull=True).delete()
    DocumentTextChunk.objects.filter(document__isnull=True).delete()
    DocumentChunk.objects.filter(document__isnull=True).delete()

    document_texts_with_no_document = list(
        DocumentText.objects.filter(document__isnull=True).values_list("pk", flat=True)
    )
    if document_texts_with_no_document:
        DocumentTextChunk.objects.filter(document_id__in=document_texts_with_no_document).delete()
        DocumentText.objects.filter(pk__in=document_texts_with_no_document).delete()

    for document in Document.objects.all().iterator():
        DocumentPages.objects.get_or_create(document=document)
        document_text, _ = DocumentText.objects.get_or_create(document=document, defaults={"text": ""})
        DocumentTextChunk.objects.get_or_create(document=document_text)
        DocumentChunk.objects.get_or_create(
            document=document,
            chunk_index=0,
            defaults={"embedding": None},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_remove_documentchunk_content_documentpages_document_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_document_relations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="documentpages",
            name="document",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="documents.document",
            ),
        ),
        migrations.AlterField(
            model_name="documenttext",
            name="document",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="documents.document",
            ),
        ),
        migrations.AlterField(
            model_name="documenttextchunk",
            name="document",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="text_chunks",
                to="documents.documenttext",
            ),
        ),
        migrations.AlterField(
            model_name="documentchunk",
            name="document",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="chunks",
                to="documents.document",
            ),
        ),
    ]
