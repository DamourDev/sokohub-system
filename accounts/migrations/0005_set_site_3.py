from django.db import migrations

def set_site_3(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    site_id = 3  # must match your SITE_ID in settings.py

    site, created = Site.objects.get_or_create(
        id=site_id,
        defaults={
            "domain": "sokohub-sul9.onrender.com",
            "name": "SokoHub",
        },
    )
    if not created:
        site.domain = "sokohub-sul9.onrender.com"
        site.name = "SokoHub"
        site.save()

class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("accounts", "0004_alter_customuser_phone"),
    ]

    operations = [
        migrations.RunPython(set_site_3),
    ]
