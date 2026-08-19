from django.conf import settings
from django.db import models
from django.utils import timezone
from pathlib import Path
import uuid


def inspection_photo_upload_path(instance, filename):
    """元ファイル名を保存せず、推測しにくいUUID名で画像を保存する。"""
    suffix = Path(filename).suffix.lower() or '.jpg'
    return f'inspection_photos/{timezone.localdate():%Y/%m}/{uuid.uuid4().hex}{suffix}'


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
    weekdays = models.CharField(
        '実施曜日',
        max_length=20,
        default='0,1,2,3,4,5,6',
        help_text='0=月曜日、6=日曜日',
    )

    WEEKDAY_LABELS = ('月', '火', '水', '木', '金', '土', '日')

    def weekday_numbers(self):
        values = []
        for value in self.weekdays.split(','):
            value = value.strip()
            if value.isdigit() and 0 <= int(value) <= 6:
                values.append(int(value))
        return sorted(set(values))

    def runs_on(self, target_date):
        return target_date.weekday() in self.weekday_numbers()

    @property
    def weekday_display(self):
        numbers = self.weekday_numbers()
        if numbers == list(range(7)):
            return '毎日'
        if numbers == list(range(5)):
            return '平日'
        return '・'.join(self.WEEKDAY_LABELS[number] for number in numbers) or '未設定'

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
    class Result(models.TextChoices):
        NORMAL = 'normal', '正常'
        ABNORMAL = 'abnormal', '異常'

    record = models.ForeignKey(InspectionRecord, on_delete=models.CASCADE, related_name='answers', verbose_name='点検記録')
    item = models.ForeignKey(InspectionItem, on_delete=models.PROTECT, related_name='answers', verbose_name='点検項目')
    checked = models.BooleanField('確認済み', default=False)
    result = models.CharField('項目結果', max_length=20, choices=Result.choices, blank=True, default='')
    note = models.CharField('異常時コメント', max_length=255, blank=True)
    photo = models.ImageField('異常写真', upload_to=inspection_photo_upload_path, blank=True)

    class Meta:
        ordering = ['item__display_order', 'item_id']
        constraints = [
            models.UniqueConstraint(fields=['record', 'item'], name='unique_record_item_answer')
        ]
        verbose_name = '点検回答'
        verbose_name_plural = '点検回答'

    def __str__(self):
        return f'{self.record} / {self.item}'


class AbnormalIssue(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', '未対応'
        IN_PROGRESS = 'in_progress', '対応中'
        RESOLVED = 'resolved', '対応済み'

    answer = models.OneToOneField(InspectionAnswer, on_delete=models.CASCADE, related_name='issue', verbose_name='異常項目')
    status = models.CharField('対応状況', max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField('発生登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    resolved_at = models.DateTimeField('対応完了日時', null=True, blank=True)

    class Meta:
        ordering = ['status', '-answer__record__inspection_date', '-created_at']
        verbose_name = '異常対応'
        verbose_name_plural = '異常対応'

    @property
    def equipment(self):
        return self.answer.record.template.equipment

    def __str__(self):
        return f'{self.answer.record.inspection_date} {self.equipment.name} / {self.answer.item.label}'


class AbnormalIssueUpdate(models.Model):
    issue = models.ForeignKey(AbnormalIssue, on_delete=models.CASCADE, related_name='updates', verbose_name='異常対応')
    status = models.CharField('変更後の状況', max_length=20, choices=AbnormalIssue.Status.choices)
    note = models.TextField('対応内容')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='abnormal_issue_updates', verbose_name='対応者')
    created_at = models.DateTimeField('対応日時', auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']
        verbose_name = '異常対応履歴'
        verbose_name_plural = '異常対応履歴'

    def __str__(self):
        return f'{self.issue} - {self.get_status_display()}'
