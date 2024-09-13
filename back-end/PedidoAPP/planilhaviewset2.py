def process_excel_and_create_entries(file_path):
    # Carregar o arquivo Excel
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active  # Usar a primeira planilha

    # Obter os nomes das fábricas a partir das células específicas
    factory_names = {
        'H1': sheet['H1'].value,  # Fábrica H1
        'L1': sheet['L1'].value,  # Fábrica L1
        'P1': sheet['P1'].value,  # Fábrica P1
        'T1': sheet['T1'].value,  # Fábrica T1
        'AA1': sheet['AA1'].value  # Fábrica AA1
    }
    
    print(f"Fábricas encontradas: {factory_names}")

    # Obter os nomes das companhias a partir das células específicas (linhas de empresas)
    company_columns = {
        'H3': {'name': sheet['H3'].value, 'sim_col': 'H'},  # Coluna para SIM verificação
        'I3': {'name': sheet['I3'].value, 'sim_col': 'I'},
        'L3': {'name': sheet['L3'].value, 'sim_col': 'L'},
        'M3': {'name': sheet['M3'].value, 'sim_col': 'M'},
        'P3': {'name': sheet['P3'].value, 'sim_col': 'P'},
        'T3': {'name': sheet['T3'].value, 'sim_col': 'T'},  # Empresas separadas por '/'
        'U3': {'name': sheet['U3'].value, 'sim_col': 'U'},
        'V3': {'name': sheet['V3'].value, 'sim_col': 'V'},
        'X3': {'name': sheet['X3'].value, 'sim_col': 'X'},
        'AA3': {'name': sheet['AA3'].value, 'sim_col': 'AA'},
        'AB3': {'name': sheet['AB3'].value, 'sim_col': 'AB'}
    }

    print(f"Companhias encontradas: {company_columns}")

    # Criar ou obter as fábricas
    factories = {}
    for cell, factory_name in factory_names.items():
        if factory_name:
            factory, _ = Factory.objects.get_or_create(name=factory_name)
            factories[cell] = factory
            print(f"Fábrica processada: {factory_name}")

    # Criar ou obter as empresas (Company)
    companies = {}
    for cell, company_info in company_columns.items():
        company_name = company_info['name']
        if company_name:
            # Algumas colunas têm múltiplas empresas separadas por "/"
            company_names = [name.strip() for name in company_name.split('/')]
            for name in company_names:
                company, _ = Company.objects.get_or_create(name=name)
                companies[name] = company
                print(f"Empresa processada: {name}")

    # Definir as colunas das fábricas e pesos corretamente
    factory_columns = {
        'H1': {'factory_code_col': 'J', 'weight_col': 'K', 'start_row': 4},  # Fábrica H1
        'L1': {'factory_code_col': 'N', 'weight_col': 'O', 'start_row': 4},  # Fábrica L1
        'P1': {'factory_code_col': 'Q', 'weight_col': 'R', 'start_row': 4},  # Fábrica P1
        'T1': {'factory_code_col': 'Y', 'weight_col': 'Z', 'start_row': 6},  # Fábrica T1
        'AA1': {'factory_code_col': 'AC', 'weight_col': 'AD', 'start_row': 4}  # Fábrica AA1
    }

    # Processar as linhas da planilha a partir da linha 4 para criar produtos e associá-los
    for row in sheet.iter_rows(min_row=4, max_row=sheet.max_row):  # Processa todas as linhas relevantes
        ncm = row[1].value  # Coluna B (NCM)
        alumifont_code = row[3].value  # Coluna D (alumifont_code)
        image = row[4].value  # Coluna E (imagem)
        length_mm = row[5].value  # Coluna F (length_mm)

        # Verificar se o alumifont_code é válido e não nulo
        if not alumifont_code:
            print(f"Erro: Alumifont Code está ausente na linha {row[0].row}.")
            continue  # Ignorar a linha se não houver código

        print(f"Processando produto: {alumifont_code}")

        # Criar ou obter o produto
        product, created = Product.objects.get_or_create(
            alumifont_code=alumifont_code,
            defaults={
                'ncm': ncm,
                'image': image,
                'length_mm': length_mm if length_mm else 6000,  # Valor padrão 6000
                'temper_alloy': '6063T5',
                'surface_finish': None  # Adicionar padrão se necessário
            }
        )

        # Relacionar o produto com as fábricas
        for factory_cell, columns in factory_columns.items():
            current_row = row[0].row
            if current_row < columns['start_row']:
                continue  # Ignorar se a linha atual for menor que a linha inicial da fábrica

            factory_code_col = columns['factory_code_col'] + str(current_row)
            weight_col = columns['weight_col'] + str(current_row)

            factory_code = sheet[factory_code_col].value
            weight_m_kg = sheet[weight_col].value

            # Verificar se o código da fábrica e o peso estão preenchidos
            if factory_code and weight_m_kg:
                try:
                    factory = factories.get(factory_cell)
                    if factory:
                        # Substituir vírgula por ponto para lidar com números decimais
                        weight_m_kg = str(weight_m_kg).replace(',', '.')

                        # Criar ou atualizar a entrada FactoryProduct
                        FactoryProduct.objects.update_or_create(
                            factory=factory,
                            product=product,
                            defaults={
                                'factory_code': factory_code.strip(),  # Remover espaços em branco
                                'weight_m_kg': float(weight_m_kg)  # Converter para float após substituir vírgula
                            }
                        )
                        print(f"Produto {alumifont_code} associado à fábrica {factory_cell} com código {factory_code} e peso {weight_m_kg}.")
                except Exception as e:
                    print(f"Erro ao processar a fábrica {factory_cell} para o produto {alumifont_code}: {e}")
            else:
                print(f"Produto {alumifont_code}: Fábrica {factory_cell} não oferece este produto.")

        # Verificar empresas habilitadas ("SIM") para este produto e criar relação
        for company_col, company_info in company_columns.items():
            enabled_value = sheet[company_info['sim_col'] + str(row[0].row)].value
            if enabled_value and enabled_value.strip().upper() == "SIM":
                company_name = company_info['name']
                company = companies.get(company_name)
                if company:
                    product.companies.add(company)  # Assuming many-to-many relationship (add company to product)
                    print(f"Produto {alumifont_code} habilitado para a companhia: {company_name}")

        # Salvar o produto após a atualização
        product.save()