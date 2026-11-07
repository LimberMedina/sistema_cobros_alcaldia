from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("actividades", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="actividad",
            name="imagen",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="actividades/",
            ),
        ),
    ]
