from django.db import migrations, models
import inspections.models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0003_inspectionanswer_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspectionanswer',
            name='photo',
            field=models.ImageField(blank=True, upload_to=inspections.models.inspection_photo_upload_path, verbose_name='異常写真'),
        ),
    ]
