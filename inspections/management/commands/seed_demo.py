from django.core.management.base import BaseCommand

from inspections.models import Equipment, InspectionItem, InspectionTemplate


DEMO_DATA = {
    'CT室': [
        '装置が正常に起動する',
        'エラー表示がない',
        '寝台が正常に動作する',
        'レーザーが正常に点灯する',
        '操作室モニターが正常に表示される',
        '造影剤注入器が正常に起動する',
        '室内の清掃状態を確認する',
    ],
    'MRI室': [
        '装置・コンソールが正常に起動する',
        'エラー表示がない',
        '寝台が正常に動作する',
        'コイルに破損がない',
        '酸素濃度計に異常がない',
        '吸着事故防止の環境確認を行う',
        '室内の清掃状態を確認する',
    ],
    '一般撮影室': [
        '装置が正常に起動する',
        'エラー表示がない',
        '管球・撮影台が正常に動作する',
        '画像確認モニターが正常に表示される',
        '受像器に破損がない',
        '防護具が所定の位置にある',
        '室内の清掃状態を確認する',
    ],
    '透視室': [
        '装置が正常に起動する',
        'エラー表示がない',
        '寝台・管球が正常に動作する',
        '透視画像が正常に表示される',
        'インターホンが使用できる',
        '防護具が所定の位置にある',
        '室内の清掃状態を確認する',
    ],
}


class Command(BaseCommand):
    help = 'サンプル装置と始業点検項目を登録します。'

    def handle(self, *args, **options):
        for order, (equipment_name, items) in enumerate(DEMO_DATA.items(), start=1):
            equipment, _ = Equipment.objects.update_or_create(
                name=equipment_name,
                defaults={'category': '放射線科', 'display_order': order, 'is_active': True},
            )
            template, _ = InspectionTemplate.objects.get_or_create(
                equipment=equipment,
                name='始業点検',
                defaults={'is_active': True},
            )
            for item_order, label in enumerate(items, start=1):
                InspectionItem.objects.get_or_create(
                    template=template,
                    label=label,
                    defaults={'display_order': item_order, 'is_required': True},
                )
        self.stdout.write(self.style.SUCCESS('サンプルデータを登録しました。'))
