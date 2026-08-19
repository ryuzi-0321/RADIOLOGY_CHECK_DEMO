from django import forms
from django.forms import formset_factory

from .models import AbnormalIssue, Equipment, InspectionAnswer, InspectionItem, InspectionRecord, InspectionTemplate


class StyledModelForm(forms.ModelForm):
    """共通の入力スタイルを付与する基底フォーム。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            else:
                widget.attrs.setdefault('class', 'form-control')


class EquipmentForm(StyledModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'category', 'display_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '例：CT室'}),
            'category': forms.TextInput(attrs={'placeholder': '例：CT'}),
            'display_order': forms.NumberInput(attrs={'min': 0}),
        }


class InspectionTemplateForm(StyledModelForm):
    WEEKDAY_CHOICES = [
        ('0', '月'), ('1', '火'), ('2', '水'), ('3', '木'),
        ('4', '金'), ('5', '土'), ('6', '日'),
    ]
    weekdays_selection = forms.MultipleChoiceField(
        label='実施曜日',
        choices=WEEKDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        help_text='この点検表を表示する曜日を選択してください。',
    )

    class Meta:
        model = InspectionTemplate
        fields = ['equipment', 'name', 'weekdays_selection', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '例：始業点検'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['weekdays_selection'].initial = [
                str(number) for number in self.instance.weekday_numbers()
            ]
        else:
            self.fields['weekdays_selection'].initial = [str(number) for number in range(7)]

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected = self.cleaned_data.get('weekdays_selection', [])
        instance.weekdays = ','.join(sorted(selected, key=int))
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class InspectionItemForm(StyledModelForm):
    class Meta:
        model = InspectionItem
        fields = ['label', 'display_order', 'is_required']
        widgets = {
            'label': forms.TextInput(attrs={'placeholder': '例：装置が正常に起動する'}),
            'display_order': forms.NumberInput(attrs={'min': 0}),
        }


class InspectionRecordForm(forms.ModelForm):
    class Meta:
        model = InspectionRecord
        fields = ['abnormal_details', 'action_taken']
        labels = {
            'abnormal_details': '全体メモ（任意）',
            'action_taken': '対応内容（任意）',
        }
        widgets = {
            'abnormal_details': forms.Textarea(attrs={'rows': 3, 'placeholder': '点検全体について補足があれば入力'}),
            'action_taken': forms.Textarea(attrs={'rows': 3, 'placeholder': '報告・再起動・メーカー連絡など'}),
        }


class InspectionAnswerForm(forms.Form):
    RESULT_CHOICES = [
        (InspectionAnswer.Result.NORMAL, '正常'),
        (InspectionAnswer.Result.ABNORMAL, '異常'),
    ]

    item_id = forms.IntegerField(widget=forms.HiddenInput)
    label = forms.CharField(disabled=True, required=False)
    required_item = forms.BooleanField(widget=forms.HiddenInput, required=False)
    result = forms.ChoiceField(
        choices=RESULT_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label='結果',
    )
    note = forms.CharField(
        required=False,
        max_length=255,
        label='異常内容・メモ',
        widget=forms.TextInput(attrs={'placeholder': '異常の内容を入力'}),
    )
    photo = forms.ImageField(
        required=False,
        label='異常写真（任意）',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'photo-input',
        }),
    )
    remove_photo = forms.BooleanField(
        required=False,
        label='現在の写真を削除',
    )
    existing_photo_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
    )

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and photo.size > 8 * 1024 * 1024:
            raise forms.ValidationError('写真は8MB以下にしてください。')
        return photo


InspectionAnswerFormSet = formset_factory(InspectionAnswerForm, extra=0)


class AbnormalIssueUpdateForm(forms.Form):
    status = forms.ChoiceField(
        label='対応状況',
        choices=AbnormalIssue.Status.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    note = forms.CharField(
        label='対応内容',
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'メーカーへ連絡、部品交換予定、復旧確認など'}),
    )
