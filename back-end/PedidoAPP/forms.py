from django import forms
from .models import Order, OrderProduct, Factory, Company, Product, SurfaceFinish


class UploadOrderForm(forms.Form):
    file = forms.FileField()

from django import forms
from .models import Company, Factory, Product, SurfaceFinish

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['company', 'factory']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['factory'].queryset = Factory.objects.none()  # Inicialmente vazio

        if 'company' in self.data:
            try:
                company_id = int(self.data.get('company'))
                self.fields['factory'].queryset = Factory.objects.filter(company__id=company_id)
            except (ValueError, TypeError):
                pass  # Ignore se houver erro de validação
        elif self.instance.pk:
            self.fields['factory'].queryset = self.instance.company.factories.all()  # Se o formulário estiver sendo editado


class ProductOrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        factory = kwargs.pop('factory', None)
        super(ProductOrderForm, self).__init__(*args, **kwargs)

        if company and factory:
            products = Product.objects.filter(enabled_companies=company, factory_products__factory=factory)
            surface_finishes = SurfaceFinish.objects.all()

            for product in products:
                for finish in surface_finishes:
                    field_name = f'product_{product.id}_finish_{finish.id}'
                    self.fields[field_name] = forms.IntegerField(min_value=0, required=False, label=f"{product.alumifont_code} - {finish.type}")