from django.db import migrations, models


def rename_site_brand(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(business_name="Royal Munchkin Cattery").update(
        business_name="American Munchkin House"
    )
    SiteSettings.objects.filter(
        tagline="Home-raised Munchkin kittens with royal manners"
    ).update(tagline="Home-raised Munchkin kittens, raised with care")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_contactmessage_submission_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="business_name",
            field=models.CharField(default="American Munchkin House", max_length=120),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="tagline",
            field=models.CharField(
                default="Home-raised Munchkin kittens, raised with care",
                max_length=200,
            ),
        ),
        migrations.RunPython(rename_site_brand, migrations.RunPython.noop),
    ]
