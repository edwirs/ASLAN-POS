import json
import calendar
from datetime import date
from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

from core.pos.forms import PayrollForm
from core.pos.models import Payroll, Employee, EmployeeTransaction
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Nómina'


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def get_period_range(period, period_type):
    parts = period.split('-')
    year = int(parts[0])
    month = int(parts[1])

    if period_type == 'Q1':
        start = date(year, month, 1)
        end = date(year, month, 15)

    elif period_type == 'Q2':
        start = date(year, month, 16)
        end = date(year, month, calendar.monthrange(year, month)[1])

    else:  # mensual
        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])

    return start, end


def get_employee_deductions(employee, start_date, end_date):
    return (
        EmployeeTransaction.objects
        .filter(
            employee=employee,
            is_paid=False,
            created_at__date__range=[start_date, end_date]
        )
        .aggregate(
            total=Coalesce(Sum('amount'), Decimal('0.00'))
        )['total']
    )


# =========================================================
# LISTADO DE NÓMINAS
# =========================================================

class PayrollListView(GroupPermissionMixin, TemplateView):
    template_name = 'payroll/list.html'
    permission_required = 'view_payroll'

    def post(self, request, *args, **kwargs):
        try:
            action = request.POST['action']

            if action == 'search':

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

                data = []
                for i in queryset:
                    data.append({
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

                return JsonResponse(data, safe=False)

            return JsonResponse({'error': 'Acción no válida'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Nóminas'
        context['list_url'] = reverse_lazy('payroll_list')
        context['create_url'] = reverse_lazy('payroll_create')
        context['module_name'] = MODULE_NAME
        return context


# =========================================================
# CREAR NÓMINA
# =========================================================

class PayrollCreateView(GroupPermissionMixin, CreateView):
    template_name = 'payroll/create.html'
    model = Payroll
    form_class = PayrollForm
    success_url = reverse_lazy('payroll_list')
    permission_required = 'add_payroll'

    def post(self, request, *args, **kwargs):

        action = request.POST.get('action')

        try:

            # =====================================================
            # LISTAR EMPLEADOS ACTIVOS
            # =====================================================
            if action == 'search_employees':

                employees = Employee.objects.filter(is_active=True)

                data = [
                    {
                        'id': emp.id,
                        'names': emp.names,
                        'salary': float(emp.salary),
                        'base_salary': float(emp.base_salary),
                        'social_security': emp.social_security
                    }
                    for emp in employees
                ]

                return JsonResponse(data, safe=False)
            elif action == 'get_deductions':
                employee_id = request.POST.get('employee_id')
                period = request.POST.get('period')

                total = EmployeeTransaction.objects.filter(
                    employee_id=employee_id,
                    created_at__date__month=period.split('-')[1],
                    created_at__date__year=period.split('-')[0],
                    is_paid=False
                ).aggregate(total=Sum('amount'))['total'] or 0

                return JsonResponse({'deductions': float(total)})

            # =====================================================
            # GUARDAR NÓMINA
            # =====================================================
            elif action == 'save_payroll':

                payrolls = json.loads(request.POST.get('payrolls', '[]'))

                for p in payrolls:

                    employee = Employee.objects.get(pk=p['employee_id'])
                    period = p['period']
                    period_type = p['period_type']

                    start_date, end_date = get_period_range(period, period_type)

                    # 🔹 calcular deducciones automáticas
                    auto_deductions = get_employee_deductions(
                        employee,
                        start_date,
                        end_date
                    )

                    user_deductions = Decimal(p.get('deductions') or 0)

                    deductions = user_deductions if user_deductions > 0 else auto_deductions

                    payroll = Payroll.objects.create(
                        employee=employee,
                        period=period,
                        period_type=period_type,
                        days_worked=int(p['days_worked']),
                        overtime_hours_value=Decimal(p['overtime_hours_value'] or 0),
                        other_earnings=Decimal(p['other_earnings'] or 0),
                        deductions=deductions
                    )

                    # 🔹 marcar préstamos como pagados
                    EmployeeTransaction.objects.filter(
                        employee=employee,
                        is_paid=False,
                        created_at__date__range=[start_date, end_date]
                    ).update(is_paid=True)

                return JsonResponse({'success': True})

            return JsonResponse({'error': 'Acción no reconocida'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nueva liquidación de nómina'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['module_name'] = MODULE_NAME
        return context


# =========================================================
# DETALLE DE NÓMINA
# =========================================================

class PayrollDetailView(GroupPermissionMixin, TemplateView):
    template_name = 'payroll/detail.html'
    permission_required = 'view_payroll'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        period = self.kwargs['period']
        period_type = self.kwargs['period_type']

        payrolls = Payroll.objects.filter(
            period__startswith=period,
            period_type=period_type
        ).select_related('employee')

        context['title'] = "Detalle de Nómina"
        context['period'] = period
        context['period_type'] = period_type
        context['payrolls'] = payrolls

        return context