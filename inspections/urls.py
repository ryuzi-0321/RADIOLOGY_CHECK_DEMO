from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inspection/<int:template_id>/', views.perform_inspection, name='perform_inspection'),
    path('history/', views.history, name='history'),
    path('history/<int:record_id>/', views.record_detail, name='record_detail'),
    path('export/excel/', views.export_excel, name='export_excel'),
]
