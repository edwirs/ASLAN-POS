import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from core.pos.utilities import printer
from core.pos.forms import EmployeeTransactionForm
from core.pos.models import Employee, EmployeeTransaction
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Transacciones Empleados'


class EmployeeTransactionListView(GroupPermissionMixin, TemplateView):
    template_name = 'employee_transaction/list.html'
    permission_required = 'view_employee_transaction'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                items = []
                for i in EmployeeTransaction.objects.all():
                    items.append(i.toJSON())
                return HttpResponse(json.dumps(items), content_type='application/json')
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Transacciones Empleados'
        context['list_url'] = reverse_lazy('employee_transaction_list')
        context['create_url'] = reverse_lazy('employee_transaction_create')
        context['module_name'] = MODULE_NAME
        return context

class EmployeeTransactionCreateView(GroupPermissionMixin, CreateView):
    template_name = 'employee_transaction/create.html'
    model = EmployeeTransaction
    form_class = EmployeeTransactionForm
    success_url = reverse_lazy('employee_transaction_list')
    permission_required = 'add_employee_transaction'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                form = self.get_form()

                if form.is_valid():
                    obj = form.save()
                    #data = {'success': True}
                    data = {'print_url': str(reverse_lazy('employee_transaction_print', kwargs={'pk': obj.id}))}
                else:
                    data = {'error': form.errors}
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nuevo registro de una transacción'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['module_name'] = MODULE_NAME
        return context

class EmployeeTransactionUpdateView(GroupPermissionMixin, UpdateView):
    template_name = 'employee_transaction/create.html'
    model = EmployeeTransaction
    form_class = EmployeeTransactionForm
    success_url = reverse_lazy('employee_transaction_list')
    permission_required = 'change_employee_transaction'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                form = self.get_form()

                if form.is_valid():
                    obj = form.save()
                    data = {'success': True}
                else:
                    data = {'error': form.errors}
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de una transacción'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['module_name'] = MODULE_NAME
        return context


class EmployeeTransactionDeleteView(GroupPermissionMixin, DeleteView):
    model = EmployeeTransaction
    template_name = 'delete.html'
    success_url = reverse_lazy('employee_transaction_list')
    permission_required = 'delete_employee_transaction'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una transacción'
        context['list_url'] = self.success_url
        context['module_name'] = MODULE_NAME
        return context

@method_decorator(xframe_options_exempt, name='dispatch')
class EmployeeTransactionPrintView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            transaction = EmployeeTransaction.objects.get(pk=self.kwargs['pk'])

            context = {
                'transaction': transaction,
                'height': 500
            }
            return render(request, 'employee_transaction/ticket.html', context)
        except EmployeeTransaction.DoesNotExist:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
