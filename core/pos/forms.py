from django import forms
from datetime import date

from .models import *


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'cols': 3,
                'placeholder': 'Ingrese una descripción'
            }),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ingrese un nombre'}),
            'code': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ingrese un código'}),
            'description': forms.Textarea(attrs={'class': 'form-control','rows': 1,'placeholder': 'Ingrese una descripción', 'rows': 3, 'cols': 3}),
            'category': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            'price': forms.TextInput(attrs={'name': 'price'}),
            'pvp': forms.TextInput(attrs={'name': 'pvp'}),
            'stock': forms.TextInput(attrs={'name': 'stock'}),
            'is_service': forms.CheckboxInput(attrs={'class': 'form-check-input', 'name': 'is_service'}),
            'with_tax': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class CompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre de razón social'}),
            'ruc': forms.TextInput(attrs={'placeholder': 'Ingrese un ruc'}),
            'address': forms.TextInput(attrs={'placeholder': 'Ingrese una dirección'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Ingrese un teléfono celular'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Ingrese un teléfono convencional'}),
            'email': forms.TextInput(attrs={'placeholder': 'Ingrese un email'}),
            'website': forms.TextInput(attrs={'placeholder': 'Ingrese una dirección web'}),
            'description': forms.TextInput(attrs={'placeholder': 'Ingrese una descripción'}),
            'iva': forms.TextInput(),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['names'].widget.attrs['autofocus'] = True

    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'names': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'dni': forms.TextInput(attrs={'placeholder': 'Ingrese un número de cedula'}),
            'gender': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
            'mobile': forms.TextInput(attrs={'placeholder': 'Ingrese un teléfono celular'}),
            'email': forms.TextInput(attrs={'placeholder': 'Ingrese un email'}),
            'birthdate': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'birthdate',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#birthdate'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Ingrese una dirección'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                data = super().save().toJSON()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
    
class ProviderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['names'].widget.attrs['autofocus'] = True

    class Meta:
        model = Provider
        fields = '__all__'
        widgets = {
            'names': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'dni': forms.TextInput(attrs={'placeholder': 'Ingrese un número de identificación'}),
            'gender': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
            'mobile': forms.TextInput(attrs={'placeholder': 'Ingrese un teléfono celular'}),
            'email': forms.TextInput(attrs={'placeholder': 'Ingrese un email'}),
            'address': forms.TextInput(attrs={
                'placeholder': 'Ingrese una dirección'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                data = super().save().toJSON()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class SaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.none()
        if not self.instance.pk:  # solo en formularios nuevos
            self.fields['expiration_date'].initial = next_month_day_10()

    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select select2'}),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined',
                'disabled': True
            }),
            'subtotal_0': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True,
            }),
            'subtotal_12': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'subtotal_12_sin_iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total_iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'dscto': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'total_dscto': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'cash': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'change': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'paymentmethod': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
            'transfermethods': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
            'service_type': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
            'typemethods': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
            'expiration_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'expiration_date',
                'data-toggle': 'datetimepicker',
                'data-target': '#expiration_date'
            }),
        }
        
def next_month_day_10():
    today = date.today()
    if today.month == 12:
        return date(today.year + 1, 1, 10)
    else:
        return date(today.year, today.month + 1, 10)

class PriceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.none()

    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select select2'}),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'subtotal_0': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'subtotal_12': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total_iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'dscto': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'total_dscto': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'cash': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'change': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'paymentmethod': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
        }

class BuyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provider'].queryset = Provider.objects.none()

    class Meta:
        model = Buy
        fields = '__all__'
        widgets = {
            'provider': forms.Select(attrs={'class': 'form-select select2'}),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'subtotal_0': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'subtotal_12': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total_iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'dscto': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'total_dscto': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'cash': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'change': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'paymentmethod': forms.Select(attrs={
                'class': 'select2',
                'style': 'width: 100%'
            }),
        }

class ProductAutoAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ProductAutoAdd
        fields = '__all__'
        widgets = {
            'trigger_product': forms.Select(
                attrs={'class': 'form-control select2', 'style': 'width: 100%;'}
            ),
            'auto_product': forms.Select(
                attrs={'class': 'form-control select2', 'style': 'width: 100%;'}
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control touchspin',
                    'autocomplete': 'off',
                    'step': '0.01',   # permite 2 decimales
                    'min': '0'
                }
            ),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
    
class ExpensesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Expenses
        fields = '__all__'
        exclude = ['user'] 
        widgets = {
            'source': forms.Select(
                attrs={'class': 'form-control select2', 'style': 'width: 100%;'}
            ),
            'created_at': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'created_at',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#created_at'
            }),
            'amount': forms.TextInput(
                attrs={
                    'class': 'form-control touchspin',
                    'autocomplete': 'off',
                    'step': '0.01',   # permite 2 decimales
                    'min': '0'
                }
            ),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control w-100',
                'placeholder': 'Ingrese una descripción'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }