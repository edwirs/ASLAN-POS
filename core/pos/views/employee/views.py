import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView

from core.pos.forms import EmployeeForm
from core.pos.models import Employee
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Empleados'


class EmployeeListView(GroupPermissionMixin, TemplateView):
    template_name = 'employee/list.html'
    permission_required = 'view_employee'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                items = []
                for i in Employee.objects.all():
                    items.append(i.toJSON())
                return HttpResponse(json.dumps(items), content_type='application/json')
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Empleados'
        context['list_url'] = reverse_lazy('employee_list')
        context['create_url'] = reverse_lazy('employee_create')
        context['module_name'] = MODULE_NAME
        return context

class EmployeeCreateView(GroupPermissionMixin, CreateView):
    template_name = 'employee/create.html'
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy('employee_list')
    permission_required = 'add_employee'

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
        context['title'] = 'Nuevo registro de un empleado'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['module_name'] = MODULE_NAME
        return context

class EmployeeUpdateView(GroupPermissionMixin, UpdateView):
    template_name = 'employee/create.html'
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy('employee_list')
    permission_required = 'change_employee'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                data = self.get_form().save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de un empleado'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['module_name'] = MODULE_NAME
        return context


class EmployeeDeleteView(GroupPermissionMixin, DeleteView):
    model = Employee
    template_name = 'delete.html'
    success_url = reverse_lazy('employee_list')
    permission_required = 'delete_employee'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de un empleado'
        context['list_url'] = self.success_url
        context['module_name'] = MODULE_NAME
        return context

