from django.contrib import admin

from .models import Equipment, InspectionAnswer, InspectionItem, InspectionRecord, InspectionTemplate


class InspectionItemInline(admin.TabularInline):
    model = InspectionItem
    extra = 1
    ordering = ['display_order']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    search_fields = ['name', 'category']


@admin.register(InspectionTemplate)
class InspectionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment', 'is_active']
    list_filter = ['is_active', 'equipment']
    inlines = [InspectionItemInline]


class InspectionAnswerInline(admin.TabularInline):
    model = InspectionAnswer
    extra = 0
    readonly_fields = ['item', 'checked', 'note']
    can_delete = False


@admin.register(InspectionRecord)
class InspectionRecordAdmin(admin.ModelAdmin):
    list_display = ['inspection_date', 'template', 'inspected_by', 'status', 'created_at']
    list_filter = ['status', 'inspection_date', 'template__equipment']
    search_fields = ['template__equipment__name', 'abnormal_details', 'action_taken', 'inspected_by__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [InspectionAnswerInline]
