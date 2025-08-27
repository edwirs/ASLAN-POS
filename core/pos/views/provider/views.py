import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView

from core.pos.forms import ProviderForm
from core.pos.models import Provider
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Proveedores'


class ProviderListView(GroupPermissionMixin, TemplateView):
    template_name = 'provider/list.html'
    permission_required = 'view_provider'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                for i in Provider.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Proveedores'
        context['list_url'] = reverse_lazy('provider_list')
        context['create_url'] = reverse_lazy('provider_create')
        context['module_name'] = MODULE_NAME
        return context


class ProviderCreateView(GroupPermissionMixin, CreateView):
    template_name = 'provider/create.html'
    model = Provider
    form_class = ProviderForm
    success_url = reverse_lazy('provider_list')
    permission_required = 'add_provider'

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
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Proveedor'
        context['action'] = 'add'
        context['module_name'] = MODULE_NAME
        return context


class ProviderUpdateView(GroupPermissionMixin, UpdateView):
    template_name = 'provider/create.html'
    model = Provider
    form_class = ProviderForm
    success_url = reverse_lazy('provider_list')
    permission_required = 'change_provider'

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
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Proveedor'
        context['action'] = 'edit'
        context['module_name'] = MODULE_NAME
        return context


class ProviderDeleteView(GroupPermissionMixin, DeleteView):
    model = Provider
    template_name = 'delete.html'
    success_url = reverse_lazy('provider_list')
    permission_required = 'delete_provider'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de un Proveedor'
        context['list_url'] = self.success_url
        context['module_name'] = MODULE_NAME
        return context
