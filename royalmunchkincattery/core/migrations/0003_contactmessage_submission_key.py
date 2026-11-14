import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_update_public_contact_details"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactmessage",
            name="submission_key",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
