from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Company, Factory, Product, Order, OrderProduct, SurfaceFinish
from math import ceil
from django.db.models import F



def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Inicialize uma lista para armazenar os produtos do pedido
    order_products = []
    total_weight_order = 0

    # Iterar sobre os produtos do pedido e calcular o peso total
    for item in order.order_products.all():
        custom_length = item.custom_length_mm or item.product.product.length_mm
        total_weight_product = item.quantity * item.product.weight_m_kg * custom_length
        total_weight_order += total_weight_product

        # Adicione cada produto e seus detalhes à lista
        order_products.append({
            'alumifont_code': item.product.product.alumifont_code,
            'quantity': item.quantity,
            'surface_finish': item.surface_finish.type,
            'length_mm': custom_length,
            'weight_m_kg': item.product.weight_m_kg,
            'total_weight_product': total_weight_product,
            'product_image': item.product.product.image.url if item.product.product.image else None
        })

    # Calcular o número de containers
    container_capacity_kg = 28000
    n_containers = ceil(total_weight_order / container_capacity_kg)

    # Passar os dados para o template
    context = {
        'order': order,
        'order_products': order_products,
        'total_weight_order': total_weight_order,
        'n_containers': n_containers,
    }

    return render(request, 'PedidoAPP/order_detail.html', context)


def create_orderonly(request):
    if request.method == 'POST':
        company_id = request.POST.get('company')
        factory_id = request.POST.get('factory')

        company = Company.objects.get(id=company_id)
        factory = Factory.objects.get(id=factory_id)

        # Criar pedido vazio por enquanto
        order = Order.objects.create(factory=factory, company=company)

        return redirect('order_detail', order_id=order.id)

    # Para GET, carregar as empresas
    companies = Company.objects.all()
    return render(request, 'PedidoAPP/create_order.html', {'companies': companies})

# AJAX para carregar fábricas associadas à empresa
def load_factoriesonly(request):
    company_id = request.GET.get('company_id')
    if company_id:
        try:
            company = Company.objects.get(id=company_id)
            factories = company.factories.all()  # Certifique-se de que `factories` está relacionado corretamente no modelo Company
            return render(request, 'PedidoAPP/factory_dropdown_list.html', {'factories': factories})
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Empresa não encontrada.'}, status=404)
    return JsonResponse({'error': 'Nenhuma empresa fornecida.'}, status=400)


# AJAX para buscar produtos habilitados da fábrica e da empresa
def load_productsonly(request):
    company_id = request.GET.get('company_id')
    factory_id = request.GET.get('factory_id')
    search_query = request.GET.get('search_query', '')  # Para pesquisa por Alumifonte Code

    # Se houver uma query de pesquisa, filtrar por alumifont_code
    if search_query:
        products = Product.objects.filter(enabled_companies__id=company_id, factory_products__factory__id=factory_id, alumifont_code__icontains=search_query)
    else:
        products = Product.objects.filter(enabled_companies__id=company_id, factory_products__factory__id=factory_id)

    surface_finishes = SurfaceFinish.objects.all()

    return render(request, 'PedidoAPP/product_dropdown_list.html', {
        'products': products,
        'surface_finishes': surface_finishes
    })

# AJAX para adicionar o produto ao pedido
def add_to_orderonly(request):
    product_id = request.GET.get('product_id')
    factory_id = request.GET.get('factory_id')
    finish_id = request.GET.get('finish_id')
    quantity = request.GET.get('quantity')

    product = Product.objects.get(id=product_id)
    factory = Factory.objects.get(id=factory_id)
    finish = SurfaceFinish.objects.get(id=finish_id)

    # Obter o pedido atual
    order = Order.objects.last()  # Pega o último pedido (isso pode mudar de acordo com a lógica de pedido)

    # Verificar se já existe um OrderProduct para o mesmo produto, fábrica e acabamento
    try:
        order_product = OrderProduct.objects.get(
            order=order,
            product=product.factory_products.get(factory=factory),
            surface_finish=finish
        )
        # Se já existir, simplesmente atualize a quantidade
        order_product.quantity = F('quantity') + int(quantity)
        order_product.save()
    except OrderProduct.DoesNotExist:
        # Caso não exista, crie um novo
        order_product = OrderProduct.objects.create(
            order=order,
            product=product.factory_products.get(factory=factory),
            surface_finish=finish,
            quantity=int(quantity)
        )

    # Calcular o peso total do produto e o pedido
    total_weight_product = float(order_product.quantity) * float(order_product.product.weight_m_kg) * float(order_product.custom_length_mm or product.length_mm)
    total_weight_order = sum(
    float(item.quantity) * float(item.product.weight_m_kg) * float(item.custom_length_mm or item.product.product.length_mm) for item in order.order_products.all()
    )

    # Número de containers, supondo que a capacidade de cada container seja 28.000 kg
    container_capacity_kg = 28000
    n_containers = ceil(total_weight_order / container_capacity_kg)

    return JsonResponse({
        'alumifont_code': product.alumifont_code,
        'quantity': quantity,
        'length_mm': product.length_mm,
        'weight_m_kg': order_product.product.weight_m_kg,
        'total_weight_product': total_weight_product,
        'total_weight_order': total_weight_order,
        'n_containers': n_containers
    })
