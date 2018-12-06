from django.db import migrations, models
import lanthanum.fields

from mock_app.schema_fields import music_catalog_field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RecordShop',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'name',
                    models.CharField(max_length=50, unique=True)
                ),
                (
                    'catalog',
                    lanthanum.fields.DynamicField(
                        blank=True,
                        null=True,
                        schema_field=music_catalog_field
                    )
                ),
            ],
        ),
    ]
