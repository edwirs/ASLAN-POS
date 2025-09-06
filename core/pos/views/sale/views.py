import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, FormView, TemplateView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt

from core.pos.forms import *
from core.pos.utilities import printer
from core.reports.forms import ReportForm
from core.security.mixins import GroupPermissionMixin
from core.pos.choices import PAYMENTMETHODS, TRANSFERMETHODS

MODULE_NAME = 'Ventas'

class SaleListView(GroupPermissionMixin, FormView):
    template_name = 'sale/admin/list.html'
    form_class = ReportForm
    permission_required = 'view_sale'

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'search':
                data = []
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                queryset = Sale.objects.filter()
                if len(start_date) and len(end_date):
                    queryset = queryset.filter(date_joined__range=[start_date, end_date])
                for i in queryset.order_by('-id'):
                    data.append(i.toJSON())
            elif action == 'search_detail_products':
                data = []
                for i in SaleDetail.objects.filter(sale_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ventas'
        context['list_url'] = reverse_lazy('sale_admin_list')
        context['create_url'] = reverse_lazy('sale_admin_create')
        context['module_name'] = MODULE_NAME
        context['sale_form'] = SaleForm()
        return context
    
def get_sale(request, pk):
    try:
        sale = Sale.objects.get(pk=pk)
        data = sale.toJSON()
        return JsonResponse(data, safe=False)
    except Sale.DoesNotExist:
        return JsonResponse({'error': 'La venta no existe'}, status=404)
    
def update_sale(request, pk):
    try:
        sale = Sale.objects.get(pk=pk)
        sale.paymentmethod = request.POST.get('paymentmethod')
        if sale.paymentmethod == 'transfer':
            sale.transfermethods = (request.POST['transfermethods'])
        else:
            sale.transfermethods = None
        sale.total = request.POST.get('total')
        sale.cash = request.POST.get('cash')
        sale.change = request.POST.get('change')
        sale.propina = request.POST.get('propina')
        sale.save()
        return JsonResponse({"success": True})
    except Sale.DoesNotExist:
        return JsonResponse({"error": "Venta no encontrada"})
    except Exception as e:
        return JsonResponse({"error": str(e)})


class SaleCreateView(GroupPermissionMixin, CreateView):
    model = Sale
    template_name = 'sale/admin/create.html'
    form_class = SaleForm
    success_url = reverse_lazy('sale_admin_list')
    permission_required = 'add_sale'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'add':
                with transaction.atomic():
                    company = Company.objects.first()
                    iva = float(company.iva) / 100
                    sale = Sale()
                    sale.company = company
                    sale.employee_id = request.user.id
                    sale.client_id = int(request.POST['client'])
                    sale.iva = iva
                    sale.dscto = float(request.POST['dscto']) / 100
                    sale.cash = float(request.POST['cash'])
                    sale.change = float(request.POST['change'])
                    sale.paymentmethod = (request.POST['paymentmethod'])
                    if sale.paymentmethod == 'transfer':
                        sale.transfermethods = (request.POST['transfermethods'])
                    else:
                        sale.transfermethods = None
                    sale.typemethods = (request.POST['typemethods'])
                    if sale.typemethods == 'credit':
                        sale.expiration_date = (request.POST['expiration_date'])
                    else:
                        sale.expiration_date = None
                    sale.service_type = (request.POST['service_type'])
                    sale.propina = float(request.POST['propina'])
                    sale.save()
                    for i in json.loads(request.POST['products']):
                        product = Product.objects.get(pk=i['id'])
                        detail = SaleDetail()
                        detail.sale_id = sale.id
                        detail.product_id = product.id
                        detail.cant = int(i['cant'])
                        detail.price = float(i['pvp'])
                        detail.dscto = float(i['dscto']) / 100
                        detail.save()
                        sale.calculate_detail()
                        detail.product.stock -= detail.cant
                        detail.product.save()

                        # Manejo de productos automáticos
                        auto_products = ProductAutoAdd.objects.filter(trigger_product=product)
                        for auto in auto_products:
                            auto_product = auto.auto_product

                            # Descontar del inventario general del producto automático
                            auto_product.stock -= auto.quantity * int(i['cant'])
                            auto_product.save()

                    sale.calculate_invoice()
                    data = {'print_url': str(reverse_lazy('sale_admin_print_invoice', kwargs={'pk': sale.id}))}
            elif action == 'search_products':
                ids = json.loads(request.POST['ids'])
                data = []
                term = request.POST['term']
                queryset = Product.objects.filter(Q(stock__gt=0) | Q(is_service=True)).exclude(id__in=ids).order_by('code')
                if len(term):
                    # Coincidencia exacta en code
                    exact_matches = queryset.filter(code__iexact=term)

                    # Unimos y limitamos a 10
                    queryset = (exact_matches).order_by('code')[:20]
                for i in queryset:
                    item = i.toJSON()
                    item['pvp'] = float(i.pvp)
                    item['value'] = i.get_full_name()
                    item['dscto'] = '0.00'
                    item['total_dscto'] = '0.00'
                    data.append(item)
            elif action == 'search_client':
                data = []
                term = request.POST['term']
                for i in Client.objects.filter(Q(names__icontains=term) | Q(dni__icontains=term)).order_by('names')[0:10]:
                    data.append(i.toJSON())
            elif action == 'create_client':
                form = ClientForm(self.request.POST)
                data = form.save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_final_consumer(self):
        queryset = Client.objects.filter(dni='2222222222')
        if queryset.exists():
            return json.dumps(queryset[0].toJSON())
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['frmClient'] = ClientForm()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de una Venta'
        context['action'] = 'add'
        context['company'] = Company.objects.first()
        context['final_consumer'] = self.get_final_consumer()
        context['module_name'] = MODULE_NAME
        return context

class SaleDeliveredUpdateView(View):
    def post(self, request, *args, **kwargs):
        data = {}
        if not request.user.has_perm('app_label.delivered_sale'):
            return JsonResponse({'error': 'No tienes permiso para hacer esto'}, status=403)
        try:
            sale_id = kwargs.get('pk')
            sale = Sale.objects.get(pk=sale_id)
            sale.delivered = not sale.delivered  # Cambia el valor
            sale.save()
            data['success'] = True
            data['delivered'] = sale.delivered
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

class SaleDeleteView(GroupPermissionMixin, DeleteView):
    model = Sale
    template_name = 'delete.html'
    success_url = reverse_lazy('sale_admin_list')
    permission_required = 'delete_sale'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Venta'
        context['list_url'] = self.success_url
        context['module_name'] = MODULE_NAME
        return context


@method_decorator(xframe_options_exempt, name='dispatch')
class SalePrintInvoiceView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            sale = Sale.objects.get(id=self.kwargs['pk'])
            context = {
                'sale': sale,
                'height': 450 + sale.saledetail_set.all().count() * 10
            }
            return render(request, 'sale/format/ticket.html', context)
        except Sale.DoesNotExist:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
