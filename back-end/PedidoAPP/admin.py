from django.contrib import admin
from .models import (
    Agent, Factory, Company, SurfaceFinish, Product, 
    FactoryProduct, Order, OrderProduct
)

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'endereco', 'n_convenio')
    search_fields = ('nome', 'cpf')
    list_filter = ('nome',)

@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'cnpj', 'phone', 'agent')
    search_fields = ('name', 'cnpj', 'agent__nome')
    list_filter = ('name', 'city')
    filter_horizontal = ('factories',)  # Para selecionar fábricas que a empresa pode acessar

@admin.register(SurfaceFinish)
class SurfaceFinishAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('alumifont_code', 'ncm', 'length_mm', 'temper_alloy')
    search_fields = ('alumifont_code', 'ncm')
    list_filter = ('surface_finish', 'enabled_companies')
    filter_horizontal = ('enabled_companies',)  # Para selecionar quais empresas têm acesso a um produto

@admin.register(FactoryProduct)
class FactoryProductAdmin(admin.ModelAdmin):
    list_display = ('factory', 'product', 'factory_code', 'weight_m_kg')
    search_fields = ('factory__name', 'product__alumifont_code', 'factory_code')
    list_filter = ('factory', 'product')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('factory', 'company', 'request_title', 'total_weight', 'n_containers')
    search_fields = ('request_title', 'company__name', 'factory__name')
    list_filter = ('factory', 'company')
 # Supondo que você tenha um campo de data de criação

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'surface_finish', 'quantity')
    search_fields = ('order__request_title', 'product__product__alumifont_code', 'surface_finish__type')
    list_filter = ('order', 'surface_finish')