# backend/records/migrations/0003_enable_pgcrypto.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("records", "0002_clinicalentry_content_enc_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
            reverse_sql=migrations.RunSQL.noop,
        )
    ]