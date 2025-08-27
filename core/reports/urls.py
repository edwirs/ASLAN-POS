from django.urls import path

from core.reports.views.sale_report.views import SaleReportView
from core.reports.views.employee_report.views import EmployeeSaleReportView

urlpatterns = [
    path('sale/', SaleReportView.as_view(), name='sale_report'),
    path('employeesale/', EmployeeSaleReportView.as_view(), name='employee_sale_report'),
]
