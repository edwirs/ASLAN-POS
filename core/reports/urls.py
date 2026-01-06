from django.urls import path

from core.reports.views.sale_report.views import SaleReportView
from core.reports.views.employee_report.views import EmployeeSaleReportView
from core.reports.views.sale_by_product_report.views import SaleByProductReportView

urlpatterns = [
    path('sale/', SaleReportView.as_view(), name='sale_report'),
    path('employeesale/', EmployeeSaleReportView.as_view(), name='employee_sale_report'),
    path('saleByProduct/', SaleByProductReportView.as_view(), name='sale_by_product_report'),
]
