from django.urls import path

from .views import (
    DashboardExportView, 
    DashboardLoginView, 
    DashboardLogoutView, 
    DashboardView,
    PasswordChangeView,
    PasswordChangeDoneView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard_home'),
    path('login/', DashboardLoginView.as_view(), name='dashboard_login'),
    path('logout/', DashboardLogoutView.as_view(), name='dashboard_logout'),
    path('export/csv/', DashboardExportView.as_view(), {'format': 'csv'}, name='dashboard_export_csv'),
    path('export/excel/', DashboardExportView.as_view(), {'format': 'excel'}, name='dashboard_export_excel'),
    path('change-password/', PasswordChangeView.as_view(), name='password_change'),
    path('change-password/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
]
