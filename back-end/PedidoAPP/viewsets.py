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

import pandas as pd
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Order, Product, SurfaceFinish, OrderProduct
from .serializers import FileUploadSerializer

class OrderUploadViewSet(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin):
    serializer_class = FileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']

        try:
            # Ler o arquivo Excel usando pandas
            df = pd.read_excel(file, header=None)  # header=None para que pandas não interprete a primeira linha como cabeçalhos

            # Verificar se a célula C9 (índice [8, 2]) contém um valor válido
            if df.shape[0] > 8 and df.shape[1] > 2:
                request_title = df.iloc[8, 2]
                if pd.isna(request_title):
                    return Response({'error': "'request_title' is missing or empty in the Excel file"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Excel file does not have the expected number of rows or columns'}, status=status.HTTP_400_BAD_REQUEST)

            # Crie uma instância do pedido
            order = Order.objects.create(request_title=request_title)

            # Mapear os tipos de acabamento de superfície
            surface_finish_types = df.iloc[15, 11:17].tolist()  # L16 até Q16: tipos de acabamento
            surface_finish_map = {surface_finish: idx + 1 for idx, surface_finish in enumerate(surface_finish_types)}

            # Processar os códigos de produto e quantidades
            for row in range(16, min(370, len(df))):  # Começa da linha 17 (índice 16) até a linha 370 (ou até o final do DataFrame)
                product_code = df.iloc[row, 2]  # C17 até C370: índice 2 na linha atual
                factory_code = df.iloc[row, 3]  # D17 até D370: índice 3 na linha atual
                quantities = df.iloc[row, 11:17]  # L17 até Q370: índices 11 a 17 na linha atual

                if pd.isna(product_code):
                    continue  # Ignorar se o código do produto estiver faltando

                # Criar instâncias dos produtos e relacionamentos
                try:
                    product = Product.objects.get(alumifont_code=product_code)
                except Product.DoesNotExist:
                    return Response({'error': f'Product with code {product_code} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                for index, quantity in enumerate(quantities):
                    if pd.notna(quantity) and quantity > 0:
                        surface_finish_type = surface_finish_types[index]  # Mapeia os tipos de acabamento
                        try:
                            surface_finish = SurfaceFinish.objects.get(type=surface_finish_type)
                        except SurfaceFinish.DoesNotExist:
                            return Response({'error': f'Surface finish {surface_finish_type} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                        OrderProduct.objects.create(
                            order=order,
                            product=product,
                            surface_finish=surface_finish,
                            quantity=int(quantity)  # Certifique-se de que a quantidade seja um inteiro
                        )

            # Atualize os cálculos do pedido
            order.update_calculations()

            return Response({'status': 'Order created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
