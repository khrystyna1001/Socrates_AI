from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0005_alter_document_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="process_state",
            field=models.CharField(
                choices=[
                    ("get_document", "Get Document"),
                    ("upload_document", "Upload Document"),
                    ("extract_pdf_text", "Extract PDF Text"),
                    ("split_pdf_into_chunks", "Split PDF Into Chunks"),
                    ("split_text_into_chunks", "Split Text Into Chunks"),
                    ("embed_chunks", "Embed Chunks"),
                    ("save_to_pgvector", "Save to PGVector"),
                    ("save_to_minio", "Save to MinIO"),
                ],
                default="get_document",
                max_length=32,
            ),
        ),
    ]
