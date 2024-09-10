from rest_framework import viewsets
from .models import Agent, Company, SurfaceFinish, Product, Order
from .serializers import AgentSerializer, CompanySerializer, SurfaceFinishSerializer, ProductSerializer, OrderSerializer

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class SurfaceFinishViewSet(viewsets.ModelViewSet):
    queryset = SurfaceFinish.objects.all()
    serializer_class = SurfaceFinishSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
