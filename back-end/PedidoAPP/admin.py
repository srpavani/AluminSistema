from django.contrib import admin

from django.contrib import admin
from .models import Agent, Company, SurfaceFinish, Product, Order, OrderProduct



class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1  # Número de campos extras exibidos no admin

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('request_title', 'n_containers', 'total_weight', 'percentage_under250')
    inlines = [OrderProductInline]



@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'surface_finish', 'quantity')
    search_fields = ('order__request_title', 'product__alumifont_code', 'surface_finish__type')
    list_filter = ('order', 'product', 'surface_finish')
    
    
    
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1  # Número de campos extras exibidos no admin 


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'endereco', 'n_convenio')
    search_fields = ('nome', 'cpf')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'cnpj', 'ie', 'agent')
    search_fields = ('name', 'cnpj', 'ie')
    list_filter = ('agent',)

@admin.register(SurfaceFinish)
class SurfaceFinishAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('alumifont_code', 'factory_code', 'length_mm', 'temper_alloy', 'weight_m_kg', 'surface_finish')
    search_fields = ('alumifont_code', 'factory_code', 'temper_alloy')
    list_filter = ('surface_finish',)



