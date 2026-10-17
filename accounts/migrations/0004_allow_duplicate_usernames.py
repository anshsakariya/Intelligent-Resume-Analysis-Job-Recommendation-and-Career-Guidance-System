from django.db import migrations

# Retain this migration node without the old SQLite-only table rebuild. Django's
# auth_user.username remains unique, and the legacy SQL cannot run on PostgreSQL.
class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_profile_avatar'),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
