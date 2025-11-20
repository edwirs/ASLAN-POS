import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView
from django.db.models import Sum, Count
from django.http import JsonResponse
from decimal import Decimal

from core.pos.forms import PayrollForm
from core.pos.models import Payroll, Employee
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
                            'Primera quincena' if i['period_type'] == 'Q1'
                            else 'Segunda quincena' if i['period_type'] == 'Q2'
                            else 'Mensual'
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
        action = request.POST.get('action', None)
        try:
            if action == 'search_employees':
                employees = Employee.objects.filter(is_active=True)
                data = []
                for emp in employees:
                    data.append({
                        'id': emp.id,
                        'names': emp.names,
                        'salary': float(emp.salary),
                        'base_salary': float(emp.base_salary),
                        'social_security': emp.social_security
                    })
                return JsonResponse(data, safe=False)

            elif action == 'save_payroll':
                payrolls = json.loads(request.POST.get('payrolls', '[]'))
                for p in payrolls:
                    employee = Employee.objects.get(pk=p['employee_id'])
                    Payroll.objects.create(
                        employee=employee,
                        period=p['period'],
                        period_type=p['period_type'],
                        days_worked=int(p['days_worked']),
                        overtime_hours_value=Decimal(p['overtime_hours_value'] or 0),
                        other_earnings=Decimal(p['other_earnings'] or 0),
                        deductions=Decimal(p['deductions'] or 0)
                    )
                return JsonResponse({'success': True})

            else:
                return JsonResponse({'error': 'Acción no reconocida'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nueva liquidación de nómina'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['module_name'] = MODULE_NAME
        return context

class PayrollDetailView(GroupPermissionMixin, TemplateView):
    template_name = 'payroll/detail.html'
    permission_required = 'view_payroll'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        period = self.kwargs['period']        # formato YYYY-MM
        period_type = self.kwargs['period_type']

        # Filtrar nómina del periodo
        payrolls = Payroll.objects.filter(
            period__startswith=period,
            period_type=period_type
        ).select_related('employee')

        context['title'] = "Detalle de Nómina"
        context['period'] = period
        context['period_type'] = period_type
        context['payrolls'] = payrolls

        return context
