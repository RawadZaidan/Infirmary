from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/bulk-receive/', views.inventory_bulk_receive, name='inventory_bulk_receive'),
    path('inventory/<int:item_id>/edit/', views.inventory_edit, name='inventory_edit'),
    path('inventory/<int:item_id>/restock/', views.inventory_restock, name='inventory_restock'),
    path('tests/', views.test_list, name='test_list'),
    path('tests/bulk-log/', views.test_bulk_log, name='test_bulk_log'),
    path('tests/add/', views.test_add, name='test_add'),
    path('tests/<int:test_id>/edit/', views.test_edit, name='test_edit'),
    path('daily-log/', views.daily_log_today, name='daily_log_today'),
    path('daily-log/<str:date_str>/', views.daily_log, name='daily_log'),
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.reports_export, name='reports_export'),
    path('reports/export-pdf/', views.reports_export_pdf, name='reports_export_pdf'),
]
