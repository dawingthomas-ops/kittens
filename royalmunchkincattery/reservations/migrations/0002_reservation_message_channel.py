from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="message_channel",
            field=models.CharField(
                choices=[("email", "Email"), ("sms", "Google Voice text")],
                default="email",
                max_length=10,
                verbose_name="Send reservation details via",
            ),
        ),
    ]
