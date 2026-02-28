import json
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from core.pos.forms import *
from core.pos.forms import OrderBarraForm
from core.pos.models import Table, Order, OrderDetail, InventoryGroup, Product, Company, Client, Sale, SaleDetail
from core.security.mixins import GroupPermissionMixin

MODULE_NAME = 'Ordenes'

class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = 'order/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tables = Table.objects.filter(is_active=True)
        data = []

        for table in tables:
            order = Order.objects.filter(
                table=table,
                status__in=['open', 'sent', 'ready']
            ).order_by('-id').first()

            data.append({
                'id': table.id,
                'name': table.name,
                'has_order': bool(order),
                'total': order.total if order else 0,
                'order_id': order.id if order else None,
                'employee': order.employee.get_short_name() if order else None
            })

        context['tables'] = data
        context['sale_form'] = SaleForm()
        context['module_name'] = MODULE_NAME
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')

            if action == 'create_sale':
                with transaction.atomic():
                    order_id = request.POST.get('order_id')
                    order = Order.objects.get(id=order_id)

                    # 🛡️ VALIDACIÓN DE ESTADO
                    if order.status != 'ready':
                        data['error'] = f'No se puede facturar: El pedido está en estado "{order.get_status_display()}". Debe estar "Listo" para proceder.'
                        return JsonResponse(data)
                        
                    company = Company.objects.first()

                    # 1. Crear la Venta (Sale)
                    sale = Sale()
                    sale.company = company
                    # Buscamos cliente de la orden o el consumidor final
                    sale.client = order.client if order.client else Client.objects.get(dni='222222222222')
                    sale.employee = request.user
                    sale.paymentmethod = request.POST.get('paymentmethod')
                    sale.transfermethods = request.POST.get('transfermethods')
                    sale.cash = float(request.POST.get('cash', 0))
                    sale.propina = float(request.POST.get('propina', 0))
                    sale.change = float(request.POST.get('change', 0))
                    sale.total = float(order.total)
                    sale.save()

                    # 2. Crear Detalles de Venta desde la Orden
                    for det in order.orderdetail_set.all():
                        product = det.product
                        sd = SaleDetail()
                        sd.sale = sale
                        sd.product = det.product
                        sd.cant = det.cant
                        sd.price = det.price
                        # Lógica de IVA según el producto
                        sd.iva = 0.19 if det.product.with_tax else 0 
                        sd.total = float(det.cant * det.price)
                        sd.save()
                        product.stock -= det.cant
                        product.save()

                        # Manejo de productos automáticos
                        auto_products = ProductAutoAdd.objects.filter(trigger_product=product)
                        for auto in auto_products:
                            auto_product = auto.auto_product

                            # Descontar del inventario general del producto automático
                            auto_product.stock -= auto.quantity * int(det.cant)
                            auto_product.save()

                    # 3. Recalcular totales de la venta
                    sale.calculate_invoice()

                    # 4. Cerrar la Orden
                    order.status = 'closed'
                    order.save()

                    data['redirect'] = reverse('order_list')
            else:
                data['error'] = 'Acción no válida'

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

class OrderBarraView(LoginRequiredMixin, TemplateView):
    template_name = 'order/create.html'

    def get_final_consumer(self):
        queryset = Client.objects.filter(dni='222222222222')
        if queryset.exists():
            return json.dumps(queryset[0].toJSON())
        return {}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table_id = self.kwargs['table_id']
        table = Table.objects.get(id=table_id)
        details = []

        order = Order.objects.filter(table=table, status='open').first()
        if not order:
            order = Order.objects.create(
                table=table,
                employee=self.request.user,
                status='open'
            )

        if order:
            for d in order.orderdetail_set.select_related('product'):
                details.append({
                    'id': d.product.id,
                    'name': d.product.name,
                    'cant': d.cant,
                    'pvp': float(d.price),
                    'total': float(d.cant * d.price),
                })

        context['order'] = order
        context['table'] = table
        context['order_details'] = json.dumps(details)

        user = self.request.user
        user_groups = InventoryGroup.objects.filter(userinventorygroup__user=user)
        product_stocks = Product.objects.filter(
            is_active=True
        ).select_related('category').order_by('id')
        
        product_data = []
        for p in product_stocks:
            product_data.append({
                'product': p,
                'total_stock': float(p.stock),
            })

        context['products_grouped'] = product_data

        context['client'] = order.client if order and order.client else None
        context['title'] = f'Mesa # {table.id} / Cliente: {order.client}'
        context['action'] = 'add'
        context['company'] = Company.objects.first()
        context['categories'] = Category.objects.all().order_by('name')
        context['final_consumer'] = self.get_final_consumer()
        context['frmBar'] = OrderBarraForm(instance=order)
        context['module_name'] = MODULE_NAME
        return context

class OrderCreateView(GroupPermissionMixin, CreateView):
    # Se mantiene para la acción de actualización de productos desde la vista de toma de pedido
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'update_order':
                with transaction.atomic():
                    order_id = request.POST.get('order_id')
                    products = json.loads(request.POST.get('products'))
                    order = Order.objects.get(id=order_id)

                    order.orderdetail_set.all().delete()
                    total = 0
                    for item in products:
                        subtotal = item['cant'] * item['pvp']
                        total += subtotal
                        OrderDetail.objects.create(
                            order=order,
                            product_id=item['id'],
                            cant=item['cant'],
                            price=item['pvp']
                        )
                    order.total = total
                    order.save()
                    data['redirect'] = reverse('order_list')
            else:
                data['error'] = 'Acción no válida'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)