from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspectiontemplate',
            name='weekdays',
            field=models.CharField(
                default='0,1,2,3,4,5,6',
                help_text='0=月曜日、6=日曜日',
                max_length=20,
                verbose_name='実施曜日',
            ),
        ),
    ]
