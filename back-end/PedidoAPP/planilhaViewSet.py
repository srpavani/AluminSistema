from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import os
import openpyxl
from .models import Company, Factory, Product
from .serializers import FileUploadSerializer

def process_excel_and_create_entries(file_path):
    # Carregar o arquivo Excel
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active  # Assumindo que o primeiro sheet será utilizado

    # Obter os nomes das fábricas e empresas a partir das células específicas
    factory_names = [
        sheet['H1'].value, 
        sheet['L1'].value, 
        sheet['P1'].value, 
        sheet['T1'].value, 
        sheet['AA1'].value
    ]

    # Obter os nomes das empresas
    company_columns = {
        'H3': sheet['H3'].value, 
        'I3': sheet['I3'].value, 
        'L3': sheet['L3'].value, 
        'M3': sheet['M3'].value, 
        'P3': sheet['P3'].value, 
        'T3': sheet['T3'].value,  # 4 empresas separadas por '/'
        'U3': sheet['U3'].value, 
        'V3': 'Quality', 
        'X3': 'Lumian', 
        'AA3': 'Pernambuco', 
        'AB3': 'Bahua'
    }

    # Processar as empresas da coluna T3 (4 empresas separadas por '/')
    companies_t3 = company_columns['T3'].split('/')
    company_columns['T3'] = companies_t3

    # Criar ou obter as fábricas
    factories = {}
    for factory_name in factory_names:
        if factory_name:
            factory, _ = Factory.objects.get_or_create(name=factory_name)
            factories[factory_name] = factory

    # Criar ou obter as empresas
    companies = {}
    for column, company_name in company_columns.items():
        if isinstance(company_name, list):  # Empresas da coluna T3
            for name in company_name:
                name = name.strip()  # Remover espaços em branco
                company, _ = Company.objects.get_or_create(name=name)
                companies[name] = company
        else:
            company, _ = Company.objects.get_or_create(name=company_name)
            companies[company_name] = company

    # Definir as colunas das fábricas e pesos
    factory_columns = {
        'H1': {'factory_code_col': 'J', 'weight_col': 'K'},
        'L1': {'factory_code_col': 'N', 'weight_col': 'O'},
        'P1': {'factory_code_col': 'Q', 'weight_col': 'R'},
        'T1': {'factory_code_col': 'Y', 'weight_col': 'Z'},  # Ajuste da linha inicial
        'AA1': {'factory_code_col': 'AC', 'weight_col': 'AD'}
    }

    # Processar as linhas da planilha a partir da linha 4 para criar produtos e associá-los
    for row in sheet.iter_rows(min_row=4, max_row=467):  # Vamos até a linha 467 conforme você indicou
        ncm = row[2].value  # Coluna C (NCM)
        alumifont_code = row[3].value  # Coluna D (alumifont_code)
        image = row[4].value  # Coluna E (imagem)
        length_mm = row[5].value  # Supondo que 'length_mm' esteja na coluna F

        # Verificar se o alumifont_code é válido e não nulo
        if not alumifont_code:
            raise ValueError(f"Alumifont Code está ausente na linha {row[0].row}. Esse campo não pode ser nulo.")

        # Criar ou obter o produto
        product, created = Product.objects.get_or_create(
            alumifont_code=alumifont_code,
            defaults={
                'ncm': ncm,
                'image': image,
                'length_mm': length_mm if length_mm else 6000,  # Preencha com 6000 se for nulo
                'temper_alloy': '6063T5',
                'surface_finish': None  # Defina se você tiver um acabamento de superfície padrão
            }
        )

        # Relacionar o produto com as fábricas
        for factory_name, columns in factory_columns.items():
            factory_code_col = columns['factory_code_col'] + str(row[0].row)
            weight_col = columns['weight_col'] + str(row[0].row)

            factory_code = sheet[factory_code_col].value
            weight_m_kg = sheet[weight_col].value

            if factory_code and weight_m_kg:  # Se a fábrica oferece o produto
                factory = factories.get(factory_name)
                if factory:
                    # Criar ou atualizar a entrada FactoryProduct
                    FactoryProduct.objects.update_or_create(
                        factory=factory,
                        product=product,
                        defaults={
                            'factory_code': factory_code,
                            'weight_m_kg': weight_m_kg
                        }
                    )

        # Verificar se a empresa está habilitada para o produto
        for col_idx, (column, company_name) in enumerate(company_columns.items()):
            is_enabled = row[7 + col_idx].value  # Verificar se está habilitado para a empresa
            if is_enabled == 'SIM':
                if isinstance(company_name, list):  # Para colunas com múltiplas empresas
                    for name in company_name:
                        company = companies.get(name.strip())
                        if company:
                            product.enabled_companies.add(company)
                else:
                    company = companies.get(company_name)
                    if company:
                        product.enabled_companies.add(company)

        # Salvar o produto após a atualização
        product.save()


class ExcelUploadViewSet(viewsets.ViewSet):
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        """
        POST /order-planilhas/ : Upload e processamento de planilha Excel
        """
        file_obj = request.FILES.get('file', None)
        if not file_obj:
            return Response({"detail": "Nenhum arquivo foi enviado."}, status=status.HTTP_400_BAD_REQUEST)

        # Definir o caminho completo para o arquivo de upload
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)  # Criar o diretório, se não existir
        
        file_path = os.path.join(upload_dir, file_obj.name)

        # Salvar o arquivo no diretório de upload
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        # Verificar se o arquivo foi salvo corretamente
        if not os.path.exists(file_path):
            return Response({"detail": f"O arquivo não foi encontrado após o upload: {file_path}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Processar o arquivo Excel
        try:
            process_excel_and_create_entries(file_path)
        except Exception as e:
            return Response({"detail": f"Erro ao processar o arquivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Arquivo processado com sucesso."}, status=status.HTTP_201_CREATED)
