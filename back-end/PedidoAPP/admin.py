from django.contrib import admin
from .models import Agent, Factory, Company, SurfaceFinish, Product, FactoryProduct, Order, OrderProduct

# Inline para adicionar múltiplos OrderProducts diretamente no Order
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1  # Número de linhas extras para adicionar no início
    autocomplete_fields = ['product', 'surface_finish']  # Facilitar busca de produtos e acabamentos
    fields = ['product', 'surface_finish', 'quantity']  # Definir os campos visíveis
    raw_id_fields = ['product']  # Usa um widget de busca para produtos se houver muitos produtos

# Configuração para o modelo de Order no Django Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['request_title', 'company', 'factory', 'total_weight', 'n_containers', 'percentage_under250']
    inlines = [OrderProductInline]  # Incluir os produtos como uma parte do pedido
    search_fields = ['company__name', 'factory__name']  # Facilitar busca por nome de empresa ou fábrica
    readonly_fields = ['total_weight', 'n_containers', 'percentage_under250']  # Campos de cálculo automáticos

# Configuração adicional para os outros modelos
@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'city', 'neighborhood', 'phone', 'cnpj']
    search_fields = ['name', 'cnpj']  # Busca facilitada por nome ou CNPJ

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['alumifont_code', 'ncm', 'length_mm', 'temper_alloy']
    search_fields = ['alumifont_code', 'ncm']

@admin.register(SurfaceFinish)
class SurfaceFinishAdmin(admin.ModelAdmin):
    list_display = ['type']
    search_fields = ['type']  # Adicionar o campo search_fields para usar auto-complete

# Cadastro de FactoryProduct separado
@admin.register(FactoryProduct)
class FactoryProductAdmin(admin.ModelAdmin):
    list_display = ['factory', 'product', 'factory_code', 'weight_m_kg']
    search_fields = ['factory__name', 'product__alumifont_code']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf']
    search_fields = ['nome', 'cpf']
