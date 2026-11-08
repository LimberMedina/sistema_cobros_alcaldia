from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfil",
            name="incluir_fotos_informe",
            field=models.BooleanField(default=False),
        ),
    ]
