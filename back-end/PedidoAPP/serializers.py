from rest_framework import serializers
from .models import Agent, Company, SurfaceFinish, Product, Order
from rest_framework import serializers
from .models import Agent, Factory, Company, SurfaceFinish, Product, Order, OrderProduct

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'nome', 'cpf', 'endereco', 'n_convenio']


class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ['id', 'name']


class CompanySerializer(serializers.ModelSerializer):
    factories = FactorySerializer(many=True, read_only=True)  # Mostra as fábricas associadas

    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'city', 'neighborhood', 'phone', 'cnpj', 'ie', 'factories', 'agent']


class SurfaceFinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurfaceFinish
        fields = ['id', 'type']


class ProductSerializer(serializers.ModelSerializer):
    surface_finish = SurfaceFinishSerializer(read_only=True)
    enabled_companies = CompanySerializer(many=True, read_only=True)  # Lista de empresas que têm acesso ao produto

    class Meta:
        model = Product
        fields = ['id', 'alumifont_code', 'factory_code', 'image', 'length_mm', 'temper_alloy', 'weight_m_kg', 'surface_finish', 'enabled_companies']


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    surface_finish = SurfaceFinishSerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['id', 'order', 'product', 'surface_finish', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    factory = FactorySerializer(read_only=True)
    order_products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'factory', 'company', 'request_title', 'n_containers', 'total_weight', 'percentage_under250', 'order_products']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


