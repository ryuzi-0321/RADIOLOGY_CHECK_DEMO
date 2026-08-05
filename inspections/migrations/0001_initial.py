from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='装置・部屋名')),
                ('category', models.CharField(blank=True, max_length=100, verbose_name='分類')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='表示順')),
                ('is_active', models.BooleanField(default=True, verbose_name='使用中')),
            ],
            options={'verbose_name': '装置', 'verbose_name_plural': '装置', 'ordering': ['display_order', 'name']},
        ),
        migrations.CreateModel(
            name='InspectionTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='始業点検', max_length=100, verbose_name='点検表名')),
                ('is_active', models.BooleanField(default=True, verbose_name='使用中')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='templates', to='inspections.equipment', verbose_name='装置')),
            ],
            options={'verbose_name': '点検表', 'verbose_name_plural': '点検表', 'ordering': ['equipment__display_order', 'equipment__name', 'name']},
        ),
        migrations.CreateModel(
            name='InspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, verbose_name='点検項目')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='表示順')),
                ('is_required', models.BooleanField(default=True, verbose_name='必須')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inspections.inspectiontemplate', verbose_name='点検表')),
            ],
            options={'verbose_name': '点検項目', 'verbose_name_plural': '点検項目', 'ordering': ['display_order', 'id']},
        ),
        migrations.CreateModel(
            name='InspectionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_date', models.DateField(default=django.utils.timezone.localdate, verbose_name='点検日')),
                ('status', models.CharField(choices=[('normal', '正常'), ('abnormal', '異常あり')], default='normal', max_length=20, verbose_name='結果')),
                ('abnormal_details', models.TextField(blank=True, verbose_name='異常内容')),
                ('action_taken', models.TextField(blank=True, verbose_name='対応内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('inspected_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inspection_records', to=settings.AUTH_USER_MODEL, verbose_name='点検者')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='inspections.inspectiontemplate', verbose_name='点検表')),
            ],
            options={'verbose_name': '点検記録', 'verbose_name_plural': '点検記録', 'ordering': ['-inspection_date', '-created_at']},
        ),
        migrations.CreateModel(
            name='InspectionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked', models.BooleanField(default=False, verbose_name='確認済み')),
                ('note', models.CharField(blank=True, max_length=255, verbose_name='項目メモ')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='inspections.inspectionitem', verbose_name='点検項目')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='inspections.inspectionrecord', verbose_name='点検記録')),
            ],
            options={'verbose_name': '点検回答', 'verbose_name_plural': '点検回答', 'ordering': ['item__display_order', 'item_id']},
        ),
        migrations.AddConstraint(model_name='inspectiontemplate', constraint=models.UniqueConstraint(fields=('equipment', 'name'), name='unique_equipment_template_name')),
        migrations.AddConstraint(model_name='inspectionrecord', constraint=models.UniqueConstraint(fields=('template', 'inspection_date'), name='one_record_per_template_per_day')),
        migrations.AddConstraint(model_name='inspectionanswer', constraint=models.UniqueConstraint(fields=('record', 'item'), name='unique_record_item_answer')),
    ]
