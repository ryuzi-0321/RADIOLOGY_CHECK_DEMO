from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inspection/<int:template_id>/', views.perform_inspection, name='perform_inspection'),
    path('history/', views.history, name='history'),
    path('analytics/', views.analytics, name='analytics'),
    path('issues/', views.issues, name='issues'),
    path('issues/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('analytics/export/excel/', views.export_analytics_excel, name='export_analytics_excel'),
    path('history/<int:record_id>/', views.record_detail, name='record_detail'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('qr/equipment/<int:equipment_id>/', views.equipment_scan, name='equipment_scan'),

    path('settings/', views.settings_home, name='settings_home'),
    path('settings/equipment/add/', views.equipment_create, name='equipment_create'),
    path('settings/equipment/<int:equipment_id>/edit/', views.equipment_edit, name='equipment_edit'),
    path('settings/equipment/<int:equipment_id>/qr/', views.equipment_qr_page, name='equipment_qr_page'),
    path('settings/equipment/<int:equipment_id>/qr/image/', views.equipment_qr_image, name='equipment_qr_image'),
    path('settings/equipment/<int:equipment_id>/delete/', views.equipment_delete, name='equipment_delete'),
    path('settings/template/add/', views.template_create, name='template_create'),
    path('settings/equipment/<int:equipment_id>/template/add/', views.template_create, name='template_create_for_equipment'),
    path('settings/template/<int:template_id>/edit/', views.template_edit, name='template_edit'),
    path('settings/template/<int:template_id>/delete/', views.template_delete, name='template_delete'),
    path('settings/template/<int:template_id>/item/add/', views.item_create, name='item_create'),
    path('settings/item/<int:item_id>/edit/', views.item_edit, name='item_edit'),
    path('settings/item/<int:item_id>/delete/', views.item_delete, name='item_delete'),
]
