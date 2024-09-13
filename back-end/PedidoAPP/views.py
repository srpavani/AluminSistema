from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.forms import modelformset_factory
from .forms import OrderForm, ProductOrderForm
from .models import Order, OrderProduct, Factory, Product, Company, SurfaceFinish

# View para criar um pedido
def create_order(request):
    company = None
    factory = None
    product_form = None

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            company = order_form.cleaned_data['company']
            factory = order_form.cleaned_data['factory']

            # Instanciar o ProductOrderForm para capturar os produtos enviados
            product_form = ProductOrderForm(request.POST, company=company, factory=factory)

            if product_form.is_valid():
                # Criar o pedido
                order = Order.objects.create(factory=factory, company=company)

                # Obter todos os acabamentos de superfície disponíveis
                surface_finishes = SurfaceFinish.objects.all()

                # Iterar sobre os produtos e capturar as quantidades enviadas
                for product in Product.objects.filter(enabled_companies=company, factory_products__factory=factory):
                    for finish in surface_finishes:
                        field_name = f'product_{product.id}_finish_{finish.id}'
                        quantity = product_form.cleaned_data.get(field_name)

                        # Somente criar OrderProduct se a quantidade for maior que 0
                        if quantity and quantity > 0:
                            OrderProduct.objects.create(
                                order=order,
                                product=product.factory_products.get(factory=factory),
                                surface_finish=finish,
                                quantity=quantity
                            )

                # Redirecionar para uma página de sucesso
                return redirect('order_success')

    else:
        # Instanciar os formulários na requisição GET
        order_form = OrderForm()
        product_form = ProductOrderForm(company=company, factory=factory)

    # Renderizar o template com o formulário de pedidos e produtos
    context = {
        'order_form': order_form,
        'product_form': product_form,
    }

    return render(request, 'create_order.html', context)

# AJAX para carregar as fábricas da empresa selecionada
def load_factories(request):
    company_id = request.GET.get('company_id')
    company = Company.objects.get(id=company_id)
    factories = company.factories.all()
    return render(request, 'factory_dropdown_list_options.html', {'factories': factories})

# AJAX para carregar os produtos habilitados


def load_products(request):
    company_id = request.GET.get('company')
    factory_id = request.GET.get('factory')

    print(f"Recebido Company ID: {company_id}, Factory ID: {factory_id}")  # Log para ver se os IDs foram recebidos

    if company_id and factory_id:
        try:
            company = Company.objects.get(id=company_id)
            factory = Factory.objects.get(id=factory_id)

            products = Product.objects.filter(enabled_companies=company, factory_products__factory=factory)
            surface_finishes = SurfaceFinish.objects.all()

            print(f"Produtos encontrados: {products.count()}")  # Log para contar quantos produtos foram encontrados

            return render(request, 'product_table.html', {
                'products': products,
                'surface_finishes': surface_finishes,
            })
        except Company.DoesNotExist:
            print("Empresa não encontrada")
            return JsonResponse({'error': 'Empresa não encontrada'}, status=404)
        except Factory.DoesNotExist:
            print("Fábrica não encontrada")
            return JsonResponse({'error': 'Fábrica não encontrada'}, status=404)

    print("Empresa ou fábrica não fornecida")
    return JsonResponse({'error': 'Empresa ou fábrica não fornecida'}, status=400)



def order_success(request):
    return render(request, 'order_success.html')

    
    
