import os
from datetime import datetime

from django.db import models
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
from django.forms import model_to_dict

from config import settings
from core.pos.choices import GENDER
from core.pos.choices import PAYMENTMETHODS
from core.pos.choices import TRANSFERMETHODS
from core.pos.choices import EXPENSES
from core.pos.choices import SERVICE_TYPE
from core.pos.choices import TYPETMETHODS
from core.user.models import User


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoría')
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio de Compra')
    pvp = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio de Venta')
    image = models.ImageField(upload_to='product/%Y/%m/%d', null=True, blank=True, verbose_name='Imagen')
    is_service = models.BooleanField(default=False, verbose_name='¿Sin Inventario?')
    with_tax = models.BooleanField(default=True, verbose_name='¿Se cobra impuesto?')
    stock = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Stock')
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.code} - {self.name} ({self.category.name})'

    def get_short_name(self):
        return f'{self.name} ({self.category.name})'

    def get_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}img/default/empty.png'

    def toJSON(self):
        item = model_to_dict(self)
        item['full_name'] = self.get_full_name()
        item['short_name'] = self.get_short_name()
        item['category'] = self.category.toJSON()
        item['price'] = float(self.price)
        item['pvp'] = float(self.pvp)
        item['stock'] = float(self.stock) 
        item['image'] = self.get_image()
        return item

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class Company(models.Model):
    name = models.CharField(max_length=50, verbose_name='Razón social')
    ruc = models.CharField(max_length=13, verbose_name='Número de RUC')
    address = models.CharField(max_length=200, verbose_name='Dirección')
    mobile = models.CharField(max_length=10, verbose_name='Teléfono celular')
    phone = models.CharField(max_length=10, verbose_name='Teléfono convencional')
    email = models.CharField(max_length=50, verbose_name='Email')
    website = models.CharField(max_length=250, verbose_name='Dirección de página web')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    iva = models.DecimalField(default=0.00, decimal_places=2, max_digits=9, verbose_name='IVA')
    image = models.ImageField(null=True, blank=True, upload_to='company/%Y/%m/%d', verbose_name='Logotipo de la empresa')
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.name

    def get_iva(self):
        return float(self.iva)

    def get_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}img/default/empty.png'

    def toJSON(self):
        item = model_to_dict(self)
        item['image'] = self.get_image()
        item['iva'] = float(self.iva)
        return item

    class Meta:
        verbose_name = 'Compañia'
        verbose_name_plural = 'Compañias'
        default_permissions = ()
        permissions = (
            ('view_company', 'Can view Empresa'),
        )


class Client(models.Model):
    names = models.CharField(max_length=150, verbose_name='Nombre')
    dni = models.CharField(max_length=13, unique=True, verbose_name='Número de cedula')
    gender = models.CharField(max_length=50, choices=GENDER, default=GENDER[0][0], verbose_name='Genero')
    mobile = models.CharField(max_length=10, null=True, blank=True, verbose_name='Teléfono')
    email = models.CharField(max_length=50, null=True, blank=True, verbose_name='Email')
    birthdate = models.DateField(default=datetime.now, verbose_name='Fecha de nacimiento')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.names} ({self.dni})'

    def birthdate_format(self):
        return self.birthdate.strftime('%Y-%m-%d')

    def toJSON(self):
        item = model_to_dict(self)
        item['text'] = self.get_full_name()
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        item['birthdate'] = self.birthdate.strftime('%Y-%m-%d')
        return item

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

class Provider(models.Model):
    names = models.CharField(max_length=150, verbose_name='Nombre')
    dni = models.CharField(max_length=13, unique=True, verbose_name='Número de identificacion')
    gender = models.CharField(max_length=50, choices=GENDER, default=GENDER[0][0], verbose_name='Genero')
    mobile = models.CharField(max_length=10, null=True, blank=True, verbose_name='Teléfono')
    email = models.CharField(max_length=50, null=True, blank=True, verbose_name='Email')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.names} ({self.dni})'

    def toJSON(self):
        item = model_to_dict(self)
        item['text'] = self.get_full_name()
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        return item

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

class Sale(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name='Compañia')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name='Cliente')
    employee = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Empleado')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de registro')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    subtotal_12 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 12%')
    subtotal_12_sin_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor Bruto')
    subtotal_0 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 0%')
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Descuento')
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor del descuento')
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Iva')
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor de iva')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total a pagar')
    cash = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=0.00, verbose_name='Efectivo recibido')
    change = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=0.00, verbose_name='Cambio')
    paymentmethod = models.CharField(max_length=50, choices=PAYMENTMETHODS, default=PAYMENTMETHODS[0][0], verbose_name='Método de pago')
    transfermethods = models.CharField(max_length=50, choices=TRANSFERMETHODS, default=TRANSFERMETHODS[0][0], verbose_name='Tipo transferencia', null=True)
    typemethods = models.CharField(max_length=50, choices=TYPETMETHODS, default=TYPETMETHODS[0][0], verbose_name='Tipo pago', null=True)
    expiration_date = models.DateField(null = True, blank=True , verbose_name='Fecha de vencimiento')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE, default=SERVICE_TYPE[0][0], verbose_name='Tipo Servicio', null=True)
    delivered = models.BooleanField(default=False, verbose_name='Entregado')
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.client.get_full_name()

    def get_subtotal_without_taxes(self):
        return float(self.saledetail_set.filter().aggregate(result=Coalesce(Sum('subtotal'), 0.00, output_field=FloatField())).get('result'))

    def get_full_subtotal(self):
        return float(self.subtotal_0) + float(self.subtotal_12)

    def calculate_invoice(self):
        self.subtotal_0 = float(self.saledetail_set.filter(product__with_tax=False).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result'))
        self.subtotal_12 = float(self.saledetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result'))
        self.total_iva = float(self.saledetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total_iva'), 0.00, output_field=FloatField())).get('result'))
        self.subtotal_12_sin_iva = self.subtotal_12 - self.total_iva
        self.total_dscto = float(self.get_full_subtotal()) * float(self.dscto)
        self.total = float(self.get_full_subtotal()) - float(self.total_dscto)
        self.save()

    def calculate_detail(self):
        for detail in self.saledetail_set.filter():
            detail.price = float(detail.price)
            detail.iva = float(self.iva)
            detail.price_with_vat = detail.price + (detail.price * detail.iva)
            detail.subtotal = detail.price * detail.cant
            detail.total_dscto = detail.subtotal * float(detail.dscto)
            detail.total_iva = (detail.subtotal - detail.total_dscto) * detail.iva
            detail.total = detail.subtotal - detail.total_dscto
            detail.save()

    def total_paid(self):
        result = self.salecreditpayment_set.aggregate(s=Sum('total'))['s']
        return result if result else 0

    def pending(self):
        return self.total - self.total_paid()

    def toJSON(self):
        item = model_to_dict(self, exclude=['company', 'creation_date'])
        item['client'] = self.client.toJSON()
        item['employee'] = self.employee.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['subtotal_12'] = float(self.subtotal_12)
        item['subtotal_12_sin_iva'] = float(self.subtotal_12_sin_iva)
        item['subtotal_0'] = float(self.subtotal_0)
        item['subtotal'] = float(self.get_subtotal_without_taxes())
        item['dscto'] = float(self.dscto)
        item['total_dscto'] = float(self.total_dscto)
        item['iva'] = float(self.iva)
        item['total_iva'] = float(self.total_iva)
        item['total'] = float(self.total)
        item['cash'] = float(self.cash)
        item['change'] = float(self.change)
        item['paymentmethod'] = {'id': self.paymentmethod, 'name': self.get_paymentmethod_display()}
        item['transfermethods'] = {'id': self.transfermethods, 'name': self.get_transfermethods_display()}
        item['typemethods'] = {'id': self.typemethods, 'name': self.get_typemethods_display()}
        item['expiration_date'] = (self.expiration_date.strftime('%Y-%m-%d') if self.expiration_date else None)
        item['service_type'] = {'id': self.service_type, 'name': self.get_service_type_display()}
        item['delivered'] = self.delivered
        item['total_paid'] = float(self.total_paid())
        item['pending'] = float(self.pending())
        return item

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        default_permissions = ()
        permissions = (
            ('view_sale', 'Can view Venta'),
            ('add_sale', 'Can add Venta'),
            ('delete_sale', 'Can delete Venta'),
            ('view_sale_client', 'Can view_sale_client Venta'),
            ('delivered_sale', 'Can delivered Venta'),
        )


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price_with_vat = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.product.name

    def get_iva_percent(self):
        return int(self.iva * 100)

    def toJSON(self):
        item = model_to_dict(self, exclude=['sale'])
        item['product'] = self.product.toJSON()
        item['price'] = float(self.price)
        item['price_with_vat'] = float(self.price_with_vat)
        item['subtotal'] = float(self.subtotal)
        item['iva'] = float(self.subtotal)
        item['total_iva'] = float(self.subtotal)
        item['dscto'] = float(self.dscto)
        item['total_dscto'] = float(self.total_dscto)
        item['total'] = float(self.total)
        return item

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalle de Ventas'
        default_permissions = ()

class Price(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name='Compañia')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name='Cliente')
    employee = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Empleado')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de registro')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    subtotal_12 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 12%')
    subtotal_0 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 0%')
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Descuento')
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor del descuento')
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Iva')
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor de iva')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total a pagar')
    cash = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Efectivo recibido')
    change = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Cambio')
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.client.get_full_name()

    def get_subtotal_without_taxes(self):
        return float(self.pricedetail_set.filter().aggregate(result=Coalesce(Sum('subtotal'), 0.00, output_field=FloatField())).get('result'))

    def get_full_subtotal(self):
        return float(self.subtotal_0) + float(self.subtotal_12)

    def calculate_invoice(self):
        self.subtotal_0 = float(self.pricedetail_set.filter(product__with_tax=False).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result'))
        self.subtotal_12 = float(self.pricedetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result'))
        self.total_iva = float(self.pricedetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total_iva'), 0.00, output_field=FloatField())).get('result'))
        self.total_dscto = float(self.get_full_subtotal()) * float(self.dscto)
        self.total = float(self.get_full_subtotal()) + float(self.total_iva) - float(self.total_dscto)
        self.save()

    def calculate_detail(self):
        for detail in self.pricedetail_set.filter():
            detail.price = float(detail.price)
            detail.iva = float(self.iva)
            detail.price_with_vat = detail.price + (detail.price * detail.iva)
            detail.subtotal = detail.price * detail.cant
            detail.total_dscto = detail.subtotal * float(detail.dscto)
            detail.total_iva = (detail.subtotal - detail.total_dscto) * detail.iva
            detail.total = detail.subtotal - detail.total_dscto
            detail.save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['company', 'creation_date'])
        item['client'] = self.client.toJSON()
        item['employee'] = self.employee.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['subtotal_12'] = float(self.subtotal_12)
        item['subtotal_0'] = float(self.subtotal_0)
        item['subtotal'] = float(self.get_subtotal_without_taxes())
        item['dscto'] = float(self.dscto)
        item['total_dscto'] = float(self.total_dscto)
        item['iva'] = float(self.iva)
        item['total_iva'] = float(self.total_iva)
        item['total'] = float(self.total)
        item['cash'] = float(self.cash)
        item['change'] = float(self.change)
        return item

    class Meta:
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        default_permissions = ()
        permissions = (
            ('view_price', 'Can view Cotizacion'),
            ('add_price', 'Can add Cotizacion'),
            ('delete_price', 'Can delete Cotizacion'),
            ('view_price_client', 'Can view_price_client Cotizacion'),
        )


class PriceDetail(models.Model):
    price_id = models.ForeignKey(Price, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price_with_vat = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.product.name

    def get_iva_percent(self):
        return int(self.iva * 100)

    def toJSON(self):
        item = model_to_dict(self, exclude=['price'])
        item['product'] = self.product.toJSON()
        item['price'] = float(self.price)
        item['price_with_vat'] = float(self.price_with_vat)
        item['subtotal'] = float(self.subtotal)
        item['iva'] = float(self.subtotal)
        item['total_iva'] = float(self.subtotal)
        item['dscto'] = float(self.dscto)
        item['total_dscto'] = float(self.total_dscto)
        item['total'] = float(self.total)
        return item

    class Meta:
        verbose_name = 'Detalle de Cotización'
        verbose_name_plural = 'Detalle de Cotización'
        default_permissions = ()


class Buy(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name='Compañia')
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, verbose_name='Proveedor')
    employee = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Empleado')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de registro')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    subtotal_12 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 12%')
    subtotal_0 = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Subtotal 0%')
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Descuento')
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor del descuento')
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Iva')
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor de iva')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total a pagar')
    cash = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Efectivo pagado')
    change = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Cambio')
    paymentmethod = models.CharField(max_length=50, choices=PAYMENTMETHODS, default=PAYMENTMETHODS[0][0], verbose_name='Método de pago')
    transfermethods = models.CharField(max_length=50, choices=TRANSFERMETHODS, default=TRANSFERMETHODS[0][0], verbose_name='Tipo transferencia', null=True)
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.provider.get_full_name()

    def get_subtotal_without_taxes(self):
        return float(self.buydetail_set.filter().aggregate(result=Coalesce(Sum('subtotal'), 0.00, output_field=FloatField())).get('result'))

    def get_full_subtotal(self):
        return float(self.subtotal_0) + float(self.subtotal_12)

    def calculate_invoice(self):
        self.subtotal_0 = float(self.buydetail_set.filter(product__with_tax=False).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result'))
        self.subtotal_12 = float(self.buydetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total'), 0.00, output_field=FloatField())).get('result'))
        self.total_iva = float(self.buydetail_set.filter(product__with_tax=True).aggregate(result=Coalesce(Sum('total_iva'), 0.00, output_field=FloatField())).get('result'))
        self.total_dscto = float(self.get_full_subtotal()) * float(self.dscto)
        self.total = float(self.get_full_subtotal()) - float(self.total_dscto)
        self.save()

    def calculate_detail(self):
        for detail in self.buydetail_set.filter():
            detail.price = float(detail.price)
            detail.iva = float(self.iva)
            detail.price_with_vat = detail.price + (detail.price * detail.iva)
            detail.subtotal = detail.price * detail.cant
            detail.total_dscto = detail.subtotal * float(detail.dscto)
            detail.total_iva = (detail.subtotal - detail.total_dscto) * detail.iva
            detail.total = detail.subtotal - detail.total_dscto
            detail.save()

    def toJSON(self):
        item = model_to_dict(self, exclude=['company', 'creation_date'])
        item['provider'] = self.provider.toJSON()
        item['employee'] = self.employee.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['subtotal_12'] = float(self.subtotal_12)
        item['subtotal_0'] = float(self.subtotal_0)
        item['subtotal'] = float(self.get_subtotal_without_taxes())
        item['dscto'] = float(self.dscto)
        item['total_dscto'] = float(self.total_dscto)
        item['iva'] = float(self.iva)
        item['total_iva'] = float(self.total_iva)
        item['total'] = float(self.total)
        item['cash'] = float(self.cash)
        item['change'] = float(self.change)
        item['paymentmethod'] = {'id': self.paymentmethod, 'name': self.get_paymentmethod_display()}
        item['transfermethods'] = {'id': self.transfermethods, 'name': self.get_transfermethods_display()}
        return item

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        default_permissions = ()
        permissions = (
            ('view_buy', 'Can view Compra'),
            ('add_buy', 'Can add Compra'),
            ('delete_buy', 'Can delete Compra'),
            ('view_buy_provider', 'Can view_buy_provider Compra'),
        )


class BuyDetail(models.Model):
    buy_id = models.ForeignKey(Buy, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price_with_vat = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True, verbose_name='Estado')

    def __str__(self):
        return self.product.name

    def get_iva_percent(self):
        return int(self.iva * 100)

    def toJSON(self):
        item = model_to_dict(self, exclude=['buy'])
        item['product'] = self.product.toJSON()
        item['price'] = float(self.price)
        item['price_with_vat'] = float(self.price_with_vat)
        item['subtotal'] = float(self.subtotal)
        item['iva'] = float(self.subtotal)
        item['total_iva'] = float(self.subtotal)
        item['dscto'] = float(self.dscto)
        item['total_dscto'] = float(self.total_dscto)
        item['total'] = float(self.total)
        return item

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalle de Compra'
        default_permissions = ()

class Expenses(models.Model):
    source = models.CharField(max_length=50, choices=EXPENSES, default=EXPENSES[0][0], verbose_name='Fuente', null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Responsable')
    reason = models.CharField(max_length=200, verbose_name='Motivo')
    description = models.TextField(null=True, blank=True, verbose_name='Descripción')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    created_at = models.DateField(default=datetime.now, verbose_name='Fecha de creación')

    def __str__(self):
        return self.source

    def toJSON(self):
        item = model_to_dict(self)
        item['user'] = self.user.names or self.user.username
        item['created_at'] = self.created_at.strftime('%Y-%m-%d')
        item['amount'] = float(self.amount)
        item['source'] = {'id': self.source, 'name': self.get_source_display()}
        return item

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        default_permissions = ()
        permissions = (
            ('view_bill', 'Can view Gasto'),
            ('add_expenses', 'Can Add Gasto'),
            ('change_expenses', 'Can Update Gasto'),
            ('delete_expenses', 'Can Delete Gasto'),
        )

class ProductAutoAdd(models.Model):
    trigger_product = models.ForeignKey(Product, related_name='auto_triggers', on_delete=models.CASCADE, verbose_name='Producto base')
    auto_product = models.ForeignKey(Product, related_name='auto_adds', on_delete=models.CASCADE, verbose_name='Producto descuento')
    quantity = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Cantidad')    

    def __str__(self):
        return f'{self.trigger_product} -> {self.auto_product} (x{self.quantity})'
    
class SaleCreditPayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    paymentmethod = models.CharField(max_length=50, choices=PAYMENTMETHODS, default=PAYMENTMETHODS[0][0], verbose_name='Método de pago')
    transfermethods = models.CharField(max_length=50, choices=TRANSFERMETHODS, default=TRANSFERMETHODS[0][0], verbose_name='Tipo transferencia', null=True)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Valor pago')
    date_payment = models.DateField(default=datetime.now, verbose_name='Fecha de pago')

    def __str__(self):
        return f"{self.sale.client.get_full_name()}"
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['sale'])
        item['paymentmethod'] = {'id': self.paymentmethod, 'name': self.get_paymentmethod_display()}
        item['transfermethods'] = {'id': self.transfermethods, 'name': self.get_transfermethods_display()}
        item['total'] = float(self.total)
        item['date_payment'] = self.date_payment.strftime('%Y-%m-%d')
        return item

    class Meta:
        verbose_name = 'Pago Crédito'
        verbose_name_plural = 'Pagos Créditos'
        default_permissions = ()