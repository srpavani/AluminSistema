import pandas as pd
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Agent, Company, SurfaceFinish, Product, Order, OrderProduct
from .serializers import AgentSerializer, CompanySerializer, SurfaceFinishSerializer, ProductSerializer, OrderSerializer, FileUploadSerializer

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

class OrderUploadViewSet(viewsets.ViewSet):
    serializer_class = FileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']

        try:
            # Ler o arquivo enviado
            df = pd.read_excel(file)

            # Processar os dados da planilha
            for _, row in df.iterrows():
                # Crie uma instância do pedido
                order = Order.objects.create(request_title=row['request_title'])

                # Crie instâncias dos produtos e relacionamentos
                for _, order_product in row['products'].items():
                    try:
                        product = Product.objects.get(alumifont_code=order_product['product_code'])
                        surface_finish = SurfaceFinish.objects.get(type=order_product['surface_finish'])
                    except Product.DoesNotExist:
                        return Response({'error': f'Product with code {order_product["product_code"]} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                    except SurfaceFinish.DoesNotExist:
                        return Response({'error': f'Surface finish {order_product["surface_finish"]} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                    OrderProduct.objects.create(
                        order=order,
                        product=product,
                        surface_finish=surface_finish,
                        quantity=order_product['quantity']
                    )

                # Atualize os cálculos do pedido
                order.update_calculations()

            return Response({'status': 'Order(s) created successfully'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
