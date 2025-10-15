import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView
from django.db.models import Sum, Count

from core.pos.forms import PayrollForm
from core.pos.models import Payroll
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Nómina'


class PayrollListView(GroupPermissionMixin, TemplateView):
    template_name = 'payroll/list.html'
    permission_required = 'view_payroll'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                items = []
                # 🔹 Agrupar por periodo (mes + tipo de quincena)
                queryset = (
                    Payroll.objects
                    .values('period', 'period_type')
                    .annotate(
                        total_employees=Count('employee', distinct=True),
                        total_earned=Sum('total_earned'),
                        total_payable=Sum('total_payable'),
                    )
                    .order_by('-period', '-period_type')
                )

                for i in queryset:
                    items.append({
                        'period': i['period'].strftime('%Y-%m'),
                        'period_type': i['period_type'],
                        'period_type_display': (
                            'First Half' if i['period_type'] == 'Q1'
                            else 'Second Half' if i['period_type'] == 'Q2'
                            else 'Monthly'
                        ),
                        'total_employees': i['total_employees'],
                        'total_earned': float(i['total_earned'] or 0),
                        'total_payable': float(i['total_payable'] or 0),
                    })

                return HttpResponse(json.dumps(items), content_type='application/json')
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Nóminas'
        context['list_url'] = reverse_lazy('payroll_list')
        context['create_url'] = reverse_lazy('payroll_create')
        context['module_name'] = MODULE_NAME
        return context
    
class PayrollCreateView(GroupPermissionMixin, CreateView):
    template_name = 'payroll/create.html'
    model = Payroll
    form_class = PayrollForm
    success_url = reverse_lazy('payroll_list')
    permission_required = 'add_payroll'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                data = self.get_form().save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nueva liquidación de nómina'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['module_name'] = MODULE_NAME
        return context


