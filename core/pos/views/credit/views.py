import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.views.generic import FormView
from django.views import View

from core.pos.models import Sale, SaleCreditPayment
from core.pos.forms import *
from core.reports.forms import ReportForm

MODULE_NAME = 'Créditos Ventas'


class SaleCreditReportView(LoginRequiredMixin, FormView):
    template_name = 'credit/report.html'
    form_class = ReportForm

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        data = {}
        try:
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')

                queryset = Sale.objects.filter(typemethods='credit')
                if start_date and end_date:
                    queryset = queryset.filter(date_joined__range=[start_date, end_date])

                for s in queryset:
                    total_paid = s.salecreditpayment_set.aggregate(total=Sum('total'))['total'] or 0
                    pending = float(s.total) - float(total_paid)

                    data.append({
                        "id": s.id,
                        "date_joined": s.date_joined.strftime('%Y-%m-%d'),
                        "expiration_date": s.expiration_date.strftime('%Y-%m-%d') if s.expiration_date else '',
                        "client": {
                            "dni": s.client.dni,
                            "names": s.client.names,
                        },
                        "total": float(s.total),
                        "paid": float(total_paid),
                        "pending": float(pending),
                    })
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créditos de Ventas'
        context['module_name'] = MODULE_NAME
        context['sale_form'] = SaleForm()
        return context


def get_sale_credit(request, pk):
    try:
        sale = Sale.objects.get(pk=pk)
        total_payments = SaleCreditPayment.objects.filter(sale=sale).aggregate(total=Sum('total'))['total'] or 0
        pending = float(sale.total) - float(total_payments)
        data = {
            'id': sale.id,
            'date_joined': sale.date_joined.strftime('%Y-%m-%d'),
            'client': {
                'dni': sale.client.dni,
                'names': sale.client.names,
            },
            'paymentmethod': {
                'id': sale.paymentmethod,
                'name': sale.get_paymentmethod_display() if sale.paymentmethod else ''
            },
            'transfermethods': {
                'id': sale.transfermethods,
                'name': sale.get_transfermethods_display() if sale.transfermethods else ''
            },
            'pending': float(pending),
            'total': float(sale.total),
            'paid': float(total_payments),
            'error': ''
        }
        return JsonResponse(data, safe=False)
    except Sale.DoesNotExist:
        return JsonResponse({'error': 'La venta no existe'}, status=404)

def get_sale_payments(request, pk):
    try:
        payments = SaleCreditPayment.objects.filter(sale_id=pk).order_by('-date_payment')
        data = [
            {
                'id': p.id,
                'date_payment': p.date_payment.strftime('%Y-%m-%d'),
                'total': float(p.total),
                'paymentmethod': str(p.paymentmethod) if p.paymentmethod else '',
                'transfermethods': str(p.transfermethods) if p.transfermethods else '',
            }
            for p in payments
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

class SaleCreditAddPaymentView(View):
    def post(self, request, *args, **kwargs):
        try:
            sale_id = request.POST.get("sale_id")
            total = request.POST.get("total")
            paymentmethod = request.POST.get("paymentmethod")
            transfermethods = request.POST.get("transfermethods")

            sale = Sale.objects.get(pk=sale_id)

            # Guardar el abono
            payment = SaleCreditPayment.objects.create(
                sale=sale,
                total=total,
                paymentmethod=paymentmethod,
                transfermethods=transfermethods if transfermethods else None
            )

            return JsonResponse({"success": True, "payment": payment.toJSON()})
        except Exception as e:
            return JsonResponse({"error": str(e)})
