from django.db import migrations, models


def populate_result(apps, schema_editor):
    InspectionAnswer = apps.get_model('inspections', 'InspectionAnswer')
    for answer in InspectionAnswer.objects.all().iterator():
        if answer.checked:
            answer.result = 'normal'
        elif answer.note:
            answer.result = 'abnormal'
        else:
            answer.result = ''
        answer.save(update_fields=['result'])


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0002_inspectiontemplate_weekdays'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspectionanswer',
            name='result',
            field=models.CharField(blank=True, choices=[('normal', '正常'), ('abnormal', '異常')], default='', max_length=20, verbose_name='項目結果'),
        ),
        migrations.AlterField(
            model_name='inspectionanswer',
            name='note',
            field=models.CharField(blank=True, max_length=255, verbose_name='異常時コメント'),
        ),
        migrations.RunPython(populate_result, migrations.RunPython.noop),
    ]
