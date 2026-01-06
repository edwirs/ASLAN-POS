from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import FormView
from django.db.models import Sum

from core.pos.models import SaleDetail
from core.reports.forms import ReportForm

MODULE_NAME = 'R.Productos'


class SaleByProductReportView(LoginRequiredMixin, FormView):
    template_name = 'sale_by_product_report/report.html'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        try:
            action = request.POST.get('action')
            if action != 'search_report':
                return JsonResponse({'error': 'Acción no válida'})

            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            queryset = SaleDetail.objects.filter(
                is_active=True,
                product__is_active=True
            ).select_related(
                'product', 'sale'
            )

            if start_date and end_date:
                queryset = queryset.filter(
                    sale__date_joined__range=[start_date, end_date]
                )

            data = queryset.values(
                'product__name'
            ).annotate(
                qty=Sum('cant')
            ).order_by('-qty')

            categories = [item['product__name'] for item in data]
            quantities = [item['qty'] for item in data]

            return JsonResponse({
                'categories': categories,
                'data': quantities
            })

        except Exception as e:
            return JsonResponse({'error': str(e)})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cantidad vendida por producto'
        context['module_name'] = MODULE_NAME
        return context
