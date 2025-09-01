from django.urls import path

from core.pos.views.category.views import *
from core.pos.views.client.views import *
from core.pos.views.company.views import *
from core.pos.views.product.views import *
from core.pos.views.sale.views import *
from core.pos.views.price.views import *
from core.pos.views.buy.views import *
from core.pos.views.provider.views import *
from core.pos.views.productAutoAdd.views import *
from core.pos.views.expenses.views import *
from core.pos.views.sale import views

urlpatterns = [
    # category
    path('category/', CategoryListView.as_view(), name='category_list'),
    path('category/add/', CategoryCreateView.as_view(), name='category_create'),
    path('category/update/<int:pk>/', CategoryUpdateView.as_view(), name='category_update'),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category_delete'),
    # product
    path('product/', ProductListView.as_view(), name='product_list'),
    path('product/add/', ProductCreateView.as_view(), name='product_create'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    # company
    path('company/update/', CompanyUpdateView.as_view(), name='company_update'),
    # client
    path('client/', ClientListView.as_view(), name='client_list'),
    path('client/add/', ClientCreateView.as_view(), name='client_create'),
    path('client/update/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('client/delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
    # provider
    path('provider/', ProviderListView.as_view(), name='provider_list'),
    path('provider/add/', ProviderCreateView.as_view(), name='provider_create'),
    path('provider/update/<int:pk>/', ProviderUpdateView.as_view(), name='provider_update'),
    path('provider/delete/<int:pk>/', ProviderDeleteView.as_view(), name='provider_delete'),
    # sale
    path('sale/admin/', SaleListView.as_view(), name='sale_admin_list'),
    path('sale/admin/add/', SaleCreateView.as_view(), name='sale_admin_create'),
    path('sale/admin/delete/<int:pk>/', SaleDeleteView.as_view(), name='sale_admin_delete'),
    path('sale/admin/delivered/<int:pk>/', SaleDeliveredUpdateView.as_view(), name='sale_admin_delivered'),
    path('sale/admin/print/invoice/<int:pk>/', SalePrintInvoiceView.as_view(), name='sale_admin_print_invoice'),
    path('sale/admin/get_sale/<int:pk>/', views.get_sale, name='get_sale'),
    path('sale/admin/update_sale/<int:pk>/', views.update_sale, name='update_sale'),
    # price
    path('price/admin/', PriceListView.as_view(), name='price_admin_list'),
    path('price/admin/add/', PriceCreateView.as_view(), name='price_admin_create'),
    path('price/admin/delete/<int:pk>/', PriceDeleteView.as_view(), name='price_admin_delete'),
    path('price/admin/print/invoice/<int:pk>/', PricePrintInvoiceView.as_view(), name='price_admin_print_invoice'),
     # buy
    path('buy/admin/', BuyListView.as_view(), name='buy_admin_list'),
    path('buy/admin/add/', BuyCreateView.as_view(), name='buy_admin_create'),
    path('buy/admin/delete/<int:pk>/', BuyDeleteView.as_view(), name='buy_admin_delete'),
    path('buy/admin/print/invoice/<int:pk>/', BuyPrintInvoiceView.as_view(), name='buy_admin_print_invoice'),
     # productAutoAdd
    path("productAutoAdd/", ProductAutoAddListView.as_view(), name='productautoadd_list'),
    path("productAutoAdd/add/", ProductAutoAddCreateView.as_view(), name='productautoadd_create'),
    path("productAutoAdd/update/<int:pk>/", ProductAutoAddUpdateView.as_view(), name='productautoadd_update'),
    path("productAutoAdd/delete/<int:pk>/", ProductAutoAddDeleteView.as_view(), name='productautoadd_delete'),
     # expenses
    path("expenses/", ExpensesListView.as_view(), name='expenses_list'),
    path("expenses/add/", ExpensesCreateView.as_view(), name='expenses_create'),
    path("expenses/update/<int:pk>/", ExpensesUpdateView.as_view(), name='expenses_update'),
    path("expenses/delete/<int:pk>/", ExpensesDeleteView.as_view(), name='expenses_delete'),
]
