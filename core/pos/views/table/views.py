import json
import time

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView

from core.pos.forms import TableForm
from core.pos.models import Table
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Mesas'


class TableListView(GroupPermissionMixin, TemplateView):
    template_name = 'table/list.html'
    permission_required = 'view_table'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                for i in Table.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Mesas'
        context['list_url'] = reverse_lazy('table_list')
        context['create_url'] = reverse_lazy('table_create')
        context['module_name'] = MODULE_NAME
        
        return context


class TableCreateView(GroupPermissionMixin, CreateView):
    template_name = 'table/create.html'
    model = Table
    form_class = TableForm
    success_url = reverse_lazy('table_list')
    permission_required = 'add_table'

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
        context['title'] = 'Nuevo registro de una Mesa'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['module_name'] = MODULE_NAME
        return context


class TableUpdateView(GroupPermissionMixin, UpdateView):
    template_name = 'table/create.html'
    model = Table
    form_class = TableForm
    success_url = reverse_lazy('table_list')
    permission_required = 'change_table'

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
        context['title'] = 'Edición de una Mesa'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['module_name'] = MODULE_NAME
        return context


class TableDeleteView(GroupPermissionMixin, DeleteView):
    model = Table
    template_name = 'delete.html'
    success_url = reverse_lazy('table_list')
    permission_required = 'delete_table'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Mesa'
        context['list_url'] = self.success_url
        context['module_name'] = MODULE_NAME
        return context
