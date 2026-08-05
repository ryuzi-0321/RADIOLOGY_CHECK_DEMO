from django import forms
from django.forms import formset_factory

from .models import InspectionRecord


class InspectionRecordForm(forms.ModelForm):
    class Meta:
        model = InspectionRecord
        fields = ['status', 'abnormal_details', 'action_taken']
        widgets = {
            'status': forms.RadioSelect,
            'abnormal_details': forms.Textarea(attrs={'rows': 3, 'placeholder': '異常がある場合のみ入力'}),
            'action_taken': forms.Textarea(attrs={'rows': 3, 'placeholder': '報告・再起動・メーカー連絡など'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('status') == InspectionRecord.Status.ABNORMAL and not cleaned.get('abnormal_details'):
            self.add_error('abnormal_details', '「異常あり」の場合は異常内容を入力してください。')
        return cleaned


class InspectionAnswerForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput)
    label = forms.CharField(disabled=True, required=False)
    required_item = forms.BooleanField(widget=forms.HiddenInput, required=False)
    checked = forms.BooleanField(required=False, label='確認済み')
    note = forms.CharField(required=False, max_length=255, label='メモ')


InspectionAnswerFormSet = formset_factory(InspectionAnswerForm, extra=0)
