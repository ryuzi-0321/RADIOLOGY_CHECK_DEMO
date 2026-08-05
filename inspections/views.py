from datetime import date
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .forms import InspectionAnswerFormSet, InspectionRecordForm
from .models import InspectionAnswer, InspectionRecord, InspectionTemplate


@login_required
def dashboard(request):
    today = timezone.localdate()
    templates = list(
        InspectionTemplate.objects.filter(is_active=True, equipment__is_active=True)
        .select_related('equipment')
        .prefetch_related('items')
    )
    today_records = {
        record.template_id: record
        for record in InspectionRecord.objects.filter(
            inspection_date=today,
            template__in=templates,
        ).select_related('template', 'template__equipment', 'inspected_by')
    }

    cards = [{'template': template, 'record': today_records.get(template.id)} for template in templates]
    completed_count = len(today_records)
    abnormal_count = sum(1 for record in today_records.values() if record.status == InspectionRecord.Status.ABNORMAL)

    return render(request, 'inspections/dashboard.html', {
        'today': today,
        'cards': cards,
        'completed_count': completed_count,
        'pending_count': max(len(templates) - completed_count, 0),
        'abnormal_count': abnormal_count,
    })


@login_required
@transaction.atomic
def perform_inspection(request, template_id):
    template = get_object_or_404(
        InspectionTemplate.objects.select_related('equipment').prefetch_related('items'),
        pk=template_id,
        is_active=True,
        equipment__is_active=True,
    )
    today = timezone.localdate()
    existing = InspectionRecord.objects.filter(template=template, inspection_date=today).first()

    initial_answers = []
    existing_answers = {}
    if existing:
        existing_answers = {answer.item_id: answer for answer in existing.answers.select_related('item')}

    for item in template.items.all():
        answer = existing_answers.get(item.id)
        initial_answers.append({
            'item_id': item.id,
            'label': item.label,
            'required_item': item.is_required,
            'checked': answer.checked if answer else False,
            'note': answer.note if answer else '',
        })

    if request.method == 'POST':
        record_form = InspectionRecordForm(request.POST, instance=existing)
        answer_formset = InspectionAnswerFormSet(request.POST)

        if record_form.is_valid() and answer_formset.is_valid():
            missing_required = [
                form.cleaned_data.get('label')
                for form in answer_formset
                if form.cleaned_data.get('required_item') and not form.cleaned_data.get('checked')
            ]
            if missing_required and record_form.cleaned_data.get('status') == InspectionRecord.Status.NORMAL:
                record_form.add_error('status', '必須項目に未確認があります。「異常あり」にするか、すべて確認してください。')
            else:
                record = record_form.save(commit=False)
                record.template = template
                record.inspection_date = today
                record.inspected_by = request.user
                record.save()

                valid_item_ids = {item.id for item in template.items.all()}
                for form in answer_formset:
                    item_id = form.cleaned_data['item_id']
                    if item_id not in valid_item_ids:
                        continue
                    InspectionAnswer.objects.update_or_create(
                        record=record,
                        item_id=item_id,
                        defaults={
                            'checked': form.cleaned_data.get('checked', False),
                            'note': form.cleaned_data.get('note', ''),
                        },
                    )
                messages.success(request, f'{template.equipment.name}の{template.name}を保存しました。')
                return redirect('dashboard')
    else:
        record_form = InspectionRecordForm(instance=existing)
        answer_formset = InspectionAnswerFormSet(initial=initial_answers)

    return render(request, 'inspections/perform_inspection.html', {
        'template': template,
        'today': today,
        'record_form': record_form,
        'answer_formset': answer_formset,
        'existing': existing,
    })


@login_required
def history(request):
    records = InspectionRecord.objects.select_related('template', 'template__equipment', 'inspected_by')
    keyword = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    start = request.GET.get('start', '').strip()
    end = request.GET.get('end', '').strip()

    if keyword:
        records = records.filter(
            Q(template__equipment__name__icontains=keyword)
            | Q(template__name__icontains=keyword)
            | Q(abnormal_details__icontains=keyword)
            | Q(action_taken__icontains=keyword)
            | Q(inspected_by__username__icontains=keyword)
        )
    if status in {InspectionRecord.Status.NORMAL, InspectionRecord.Status.ABNORMAL}:
        records = records.filter(status=status)
    if start:
        records = records.filter(inspection_date__gte=start)
    if end:
        records = records.filter(inspection_date__lte=end)

    return render(request, 'inspections/history.html', {
        'records': records[:300],
        'filters': {'q': keyword, 'status': status, 'start': start, 'end': end},
    })


@login_required
def record_detail(request, record_id):
    record = get_object_or_404(
        InspectionRecord.objects.select_related('template', 'template__equipment', 'inspected_by').prefetch_related('answers__item'),
        pk=record_id,
    )
    return render(request, 'inspections/record_detail.html', {'record': record})


@login_required
def export_excel(request):
    records = InspectionRecord.objects.select_related(
        'template', 'template__equipment', 'inspected_by'
    ).prefetch_related('answers__item')

    start = request.GET.get('start', '').strip()
    end = request.GET.get('end', '').strip()
    if start:
        records = records.filter(inspection_date__gte=start)
    if end:
        records = records.filter(inspection_date__lte=end)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = '点検履歴'
    headers = ['点検日', '装置・部屋', '点検表', '点検者', '結果', '異常内容', '対応内容', '登録日時']
    sheet.append(headers)

    header_fill = PatternFill('solid', fgColor='D9EAF7')
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    for record in records:
        sheet.append([
            record.inspection_date.strftime('%Y-%m-%d'),
            record.template.equipment.name,
            record.template.name,
            record.inspected_by.get_full_name() or record.inspected_by.username,
            record.get_status_display(),
            record.abnormal_details,
            record.action_taken,
            timezone.localtime(record.created_at).strftime('%Y-%m-%d %H:%M'),
        ])

    widths = [12, 20, 18, 16, 12, 35, 35, 18]
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = 'A2'
    sheet.auto_filter.ref = sheet.dimensions

    detail_sheet = workbook.create_sheet('点検項目')
    detail_headers = ['点検日', '装置・部屋', '点検表', '点検項目', '確認', 'メモ']
    detail_sheet.append(detail_headers)
    for cell in detail_sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill

    for record in records:
        for answer in record.answers.all():
            detail_sheet.append([
                record.inspection_date.strftime('%Y-%m-%d'),
                record.template.equipment.name,
                record.template.name,
                answer.item.label,
                '済' if answer.checked else '未',
                answer.note,
            ])
    for index, width in enumerate([12, 20, 18, 40, 10, 30], start=1):
        detail_sheet.column_dimensions[get_column_letter(index)].width = width
    detail_sheet.freeze_panes = 'A2'
    detail_sheet.auto_filter.ref = detail_sheet.dimensions

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    filename = f'inspection_history_{date.today().isoformat()}.xlsx'
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
