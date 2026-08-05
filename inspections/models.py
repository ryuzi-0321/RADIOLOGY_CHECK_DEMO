from django.conf import settings
from django.db import models
from django.utils import timezone


class Equipment(models.Model):
    name = models.CharField('装置・部屋名', max_length=100, unique=True)
    category = models.CharField('分類', max_length=100, blank=True)
    display_order = models.PositiveIntegerField('表示順', default=0)
    is_active = models.BooleanField('使用中', default=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = '装置'
        verbose_name_plural = '装置'

    def __str__(self):
        return self.name


class InspectionTemplate(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='templates', verbose_name='装置')
    name = models.CharField('点検表名', max_length=100, default='始業点検')
    is_active = models.BooleanField('使用中', default=True)

    class Meta:
        ordering = ['equipment__display_order', 'equipment__name', 'name']
        constraints = [
            models.UniqueConstraint(fields=['equipment', 'name'], name='unique_equipment_template_name')
        ]
        verbose_name = '点検表'
        verbose_name_plural = '点検表'

    def __str__(self):
        return f'{self.equipment.name} - {self.name}'


class InspectionItem(models.Model):
    template = models.ForeignKey(InspectionTemplate, on_delete=models.CASCADE, related_name='items', verbose_name='点検表')
    label = models.CharField('点検項目', max_length=255)
    display_order = models.PositiveIntegerField('表示順', default=0)
    is_required = models.BooleanField('必須', default=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = '点検項目'
        verbose_name_plural = '点検項目'

    def __str__(self):
        return self.label


class InspectionRecord(models.Model):
    class Status(models.TextChoices):
        NORMAL = 'normal', '正常'
        ABNORMAL = 'abnormal', '異常あり'

    template = models.ForeignKey(InspectionTemplate, on_delete=models.PROTECT, related_name='records', verbose_name='点検表')
    inspection_date = models.DateField('点検日', default=timezone.localdate)
    inspected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='inspection_records', verbose_name='点検者')
    status = models.CharField('結果', max_length=20, choices=Status.choices, default=Status.NORMAL)
    abnormal_details = models.TextField('異常内容', blank=True)
    action_taken = models.TextField('対応内容', blank=True)
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['-inspection_date', '-created_at']
        constraints = [
            models.UniqueConstraint(fields=['template', 'inspection_date'], name='one_record_per_template_per_day')
        ]
        verbose_name = '点検記録'
        verbose_name_plural = '点検記録'

    def __str__(self):
        return f'{self.inspection_date} {self.template}'


class InspectionAnswer(models.Model):
    record = models.ForeignKey(InspectionRecord, on_delete=models.CASCADE, related_name='answers', verbose_name='点検記録')
    item = models.ForeignKey(InspectionItem, on_delete=models.PROTECT, related_name='answers', verbose_name='点検項目')
    checked = models.BooleanField('確認済み', default=False)
    note = models.CharField('項目メモ', max_length=255, blank=True)

    class Meta:
        ordering = ['item__display_order', 'item_id']
        constraints = [
            models.UniqueConstraint(fields=['record', 'item'], name='unique_record_item_answer')
        ]
        verbose_name = '点検回答'
        verbose_name_plural = '点検回答'

    def __str__(self):
        return f'{self.record} / {self.item}'
