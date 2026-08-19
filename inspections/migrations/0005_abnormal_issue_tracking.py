from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_existing_issues(apps, schema_editor):
    Answer = apps.get_model('inspections', 'InspectionAnswer')
    Issue = apps.get_model('inspections', 'AbnormalIssue')
    for answer in Answer.objects.filter(result='abnormal'):
        Issue.objects.get_or_create(answer_id=answer.id, defaults={'status': 'open'})


class Migration(migrations.Migration):
    dependencies = [
        ('inspections', '0004_inspectionanswer_photo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='AbnormalIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', '未対応'), ('in_progress', '対応中'), ('resolved', '対応済み')], default='open', max_length=20, verbose_name='対応状況')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='発生登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('resolved_at', models.DateTimeField(blank=True, null=True, verbose_name='対応完了日時')),
                ('answer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='issue', to='inspections.inspectionanswer', verbose_name='異常項目')),
            ],
            options={'verbose_name': '異常対応', 'verbose_name_plural': '異常対応'},
        ),
        migrations.CreateModel(
            name='AbnormalIssueUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', '未対応'), ('in_progress', '対応中'), ('resolved', '対応済み')], max_length=20, verbose_name='変更後の状況')),
                ('note', models.TextField(verbose_name='対応内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='対応日時')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='inspections.abnormalissue', verbose_name='異常対応')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='abnormal_issue_updates', to=settings.AUTH_USER_MODEL, verbose_name='対応者')),
            ],
            options={'verbose_name': '異常対応履歴', 'verbose_name_plural': '異常対応履歴', 'ordering': ['created_at', 'id']},
        ),
        migrations.RunPython(create_existing_issues, migrations.RunPython.noop),
    ]
