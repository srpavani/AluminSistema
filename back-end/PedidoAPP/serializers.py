from rest_framework import serializers
from .models import Agent, Company, SurfaceFinish, Product, Order

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class SurfaceFinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurfaceFinish
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    surface_finish = SurfaceFinishSerializer()  

    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)  

    class Meta:
        model = Order
        fields = '__all__'


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


