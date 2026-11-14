import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0002_reservation_message_channel"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="submission_key",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
