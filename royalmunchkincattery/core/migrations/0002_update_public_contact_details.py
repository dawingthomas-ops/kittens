from django.db import migrations, models


def update_public_contact_details(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(contact_email="hello@royalmunchkincattery.com").update(
        contact_email="dawingthomas@gmail.com"
    )
    SiteSettings.objects.filter(contact_phone="").update(contact_phone="+1 (720) 819-6325")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="contact_email",
            field=models.EmailField(default="dawingthomas@gmail.com", max_length=254),
        ),
        migrations.RunPython(update_public_contact_details, migrations.RunPython.noop),
    ]
