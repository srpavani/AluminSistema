from django.contrib import admin

from django.contrib import admin
from .models import Agent, Company, SurfaceFinish, Product, Order

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
    list_display = ('type', 'amount')
    search_fields = ('type',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('alumifont_code', 'factory_code', 'length_mm', 'temper_alloy', 'weight_m_kg', 'surface_finish')
    search_fields = ('alumifont_code', 'factory_code', 'temper_alloy')
    list_filter = ('surface_finish',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('request_title', 'n_containers', 'total_weight', 'percentage_under250')
    search_fields = ('request_title',)

