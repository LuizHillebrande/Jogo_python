import pandas as pd

def generate_possible_sheet_names(start_year=2017, start_month="Nov", end_year=2025, end_month="Fev"):
    """
    Gera uma lista com os possíveis nomes das planilhas entre Nov 17 e Fev 25,
    considerando que podem ter espaço ou não.
    """
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    sheet_names = []
    
    current_year = start_year
    current_month_index = months.index(start_month)
    
    while True:
        month_name = months[current_month_index]
        year_suffix = str(current_year)[-2:]
        
        # Adiciona as duas possibilidades: com e sem espaço
        sheet_names.append(f"{month_name}{year_suffix}")   # Ex: "Nov17"
        sheet_names.append(f"{month_name} {year_suffix}")  # Ex: "Nov 17"
        
        # Se chegamos ao último mês e ano desejado, incluímos e paramos o loop
        if current_year == end_year and month_name == end_month:
            break
        
        current_month_index += 1
        if current_month_index == 12:  # Passou de Dezembro, vira para Janeiro do próximo ano
            current_month_index = 0
            current_year += 1

    return sheet_names

def convert_value(x):
    """ 
    Converte valores do Excel para números.
    - Remove separador de milhar e troca vírgula por ponto.
    - Converte para float ou retorna 0.0 se vazio ou inválido.
    """
    if pd.isna(x) or (isinstance(x, str) and x.strip() == ""):
        return 0.0
    try:
        if isinstance(x, (int, float)):
            return float(x)
        x_str = x.replace('.', '').replace(',', '.')
        return float(x_str)
    except Exception:
        return 0.0

def process_excel(file, sheet_names):
    """
    Processa todas as planilhas informadas e gera um único DataFrame consolidado.
    """
    try:
        xls = pd.ExcelFile(file)
        available_sheets = xls.sheet_names
        print(f"Abas disponíveis no arquivo: {available_sheets}")
    except Exception as e:
        print(f"Erro ao abrir o arquivo Excel: {e}")
        return
    
    consolidated_data = []  # Lista para armazenar todas as planilhas processadas
    
    for sheet in sheet_names:
        matching_sheets = [available_sheet for available_sheet in available_sheets if sheet.strip() in available_sheet]
        if not matching_sheets:
            print(f"Aba não encontrada, pulando: {sheet}")
            continue
        
        sheet = matching_sheets[0]
        print(f"Processando aba: {sheet}")
        
        try:
            df = pd.read_excel(file, sheet_name=sheet, header=None)
        except Exception as e:
            print(f"Erro ao ler a aba {sheet}: {e}")
            continue
        
        df = df.iloc[:, :8]  # Mantém as 8 primeiras colunas (a coluna "Banco" será removida abaixo)
        
        current_balance = None
        group_name = None
        expect_initial = False  # flag para aguardar a linha de "SALDO ANTERIOR"
        last_date = None  # Armazena a última data encontrada para preenchimento
        
        processed_rows = []
        
        for idx, row in df.iterrows():
            if row.isnull().all() or (row.astype(str).str.strip() == "").all():
                continue
            
            first_cell = str(row[0]).strip() if not pd.isna(row[0]) else ""
            
            if first_cell.lower() == "data":
                group_name = row[2] if not pd.isna(row[2]) else "Grupo desconhecido"
                expect_initial = True
                continue
            
            if expect_initial:
                account_cell = str(row[2]).strip() if not pd.isna(row[2]) else ""
                if account_cell.upper() == "SALDO ANTERIOR":
                    current_balance = convert_value(row[6])
                else:
                    current_balance = 0.0
                expect_initial = False
                continue
            
            # Se a célula da data estiver vazia, preenche com a última data válida
            if pd.isna(row[0]) or str(row[0]).strip() == "":
                row[0] = last_date
            else:
                last_date = row[0]
            
            debit = convert_value(row[4]) or 0.0
            credit = convert_value(row[5]) or 0.0
            
            if debit == 0.0 and credit == 0.0:
                continue
            
            if debit < 0:
                debit *= -1
            
            # Elimina a coluna "Banco": não inclui row[3]
            processed_rows.append([row[0], row[1], row[2], debit, credit, group_name])
        
        if processed_rows:
            df_processed = pd.DataFrame(processed_rows, columns=["Data", "Histórico", "Conta", "Débito", "Crédito", "Grupo"])
            
            def format_date(x):
                if pd.isna(x):
                    return ""
                try:
                    return pd.to_datetime(x, errors='coerce', dayfirst=True).strftime('%d/%m/%Y')
                except Exception:
                    return ""

            df_processed["Data"] = df_processed["Data"].apply(format_date)
            consolidated_data.append(df_processed)
        else:
            print(f"Nenhuma linha válida encontrada na aba: {sheet}")
    
    if not consolidated_data:
        print("Nenhuma aba válida foi processada. Verifique o arquivo de entrada.")
        return
    
    final_df = pd.concat(consolidated_data, ignore_index=True)
    
    # NOVA FUNCIONALIDADE: Remoção de linhas com valores iguais na mesma data (anulação)
    # Se duas (ou mais) linhas possuírem os mesmos valores de "Data", "Débito" e "Crédito",
    # elas se cancelam (em pares) e serão retiradas do DataFrame final. As linhas eliminadas serão salvas.
    duplicated_rows = pd.DataFrame(columns=final_df.columns)
    indices_to_drop = []
    for group_keys, group in final_df.groupby(["Data", "Débito", "Crédito"]):
        if len(group) > 1:
            num_pairs = len(group) // 2  # número de pares que se anulam
            drop_count = num_pairs * 2
            drop_indices = group.index[:drop_count]
            indices_to_drop.extend(drop_indices)
            duplicated_rows = pd.concat([duplicated_rows, final_df.loc[drop_indices]], ignore_index=True)
    
    final_df.drop(indices_to_drop, inplace=True)
    
    # Formata números para o padrão 0.000,00
    final_df["Débito"] = final_df["Débito"].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    final_df["Crédito"] = final_df["Crédito"].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    output_file = "dados_consolidados.xlsx"
    final_df.to_excel(output_file, index=False)
    print(f"Arquivo consolidado salvo como: {output_file}")
    
    # Salva os valores eliminados, se houver, em um outro Excel
    if not duplicated_rows.empty:
        output_removed = "valores_eliminados.xlsx"
        duplicated_rows.to_excel(output_removed, index=False)
        print(f"Arquivo de valores eliminados salvo como: {output_removed}")

import pandas as pd
from fuzzywuzzy import process

def gerar_nomes_sheets(start_month="Jan", start_year=2017, end_year=2025):
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    sheet_names = []
    
    current_year = start_year
    current_month_index = months.index(start_month)
    
    while current_year <= end_year:
        month_name = months[current_month_index]
        year_suffix = str(current_year)[-2:]
        sheet_names.append((f"{month_name}{year_suffix}", f"{month_name} {year_suffix}"))
        current_month_index += 1
        if current_month_index == 12:
            current_month_index = 0
            current_year += 1
    
    return sheet_names

def encontrar_melhor_correspondencia(nome_busca, lista_nomes, limite=80):
    melhor_correspondencia, score = process.extractOne(nome_busca, lista_nomes)
    return melhor_correspondencia if score >= limite else None

def preencher_datas_faltantes(dados_consolidados, arquivo_referencia, start_month="Jan", start_year=2017, end_year=2025):
    df_consolidado = pd.ExcelFile(dados_consolidados)
    sheet_name = df_consolidado.sheet_names[0]  
    df_consolidado = pd.read_excel(dados_consolidados, sheet_name=sheet_name)

    registros_sem_data = df_consolidado[pd.isna(df_consolidado['Data'])].copy()
    print(f"🔍 Encontrados {len(registros_sem_data)} registros sem data.")

    xls_ref = pd.ExcelFile(arquivo_referencia)
    abas_esperadas = gerar_nomes_sheets(start_month, start_year, end_year)
    abas_reais = xls_ref.sheet_names  

    for index, row in registros_sem_data.iterrows():
        conta = row['Conta']
        melhor_data = None

        print(f"\n🔎 Buscando data para 'Conta': {conta}")

        for nome1, nome2 in abas_esperadas:
            nome_correspondente = encontrar_melhor_correspondencia(nome1, abas_reais, limite=85) or encontrar_melhor_correspondencia(nome2, abas_reais, limite=85)
            if not nome_correspondente:
                continue

            print(f"📂 Melhor aba encontrada (fuzzy): {nome_correspondente}")
            df_ref = pd.read_excel(xls_ref, sheet_name=nome_correspondente)

            if 'Data' in df_ref.columns and 'Caixa Escritório' in df_ref.columns:
                contas_disponiveis = df_ref['Caixa Escritório'].astype(str).tolist()
                melhor_conta = encontrar_melhor_correspondencia(str(conta), contas_disponiveis, limite=85)
                
                if melhor_conta:
                    filtro = df_ref[df_ref['Caixa Escritório'].astype(str) == melhor_conta]
                    filtro = filtro.dropna(subset=['Data']).sort_index(ascending=False)
                    
                    if not filtro.empty:
                        data_str = filtro.iloc[0]['Data']

                        # Verifica se a célula contém um valor válido para data
                        if isinstance(data_str, str) and data_str.lower() == "data":
                            print("⚠️ Erro: Célula contém o nome da coluna ao invés de uma data. Ignorando...")
                            melhor_data = None
                        else:
                            try:
                                melhor_data = pd.to_datetime(data_str, errors='coerce').date()
                                
                                # Evita anos incorretos como 025 ou 082024
                                if melhor_data and (melhor_data.year < 2000 or melhor_data.year > 2050):
                                    print(f"⚠️ Data inválida encontrada: {data_str} (ano inconsistente: {melhor_data.year}). Ignorando...")
                                    melhor_data = None
                                else:
                                    print(f"✅ Data encontrada para '{conta}': {melhor_data}")

                            except Exception as e:
                                print(f"⚠️ Erro ao converter data '{data_str}': {e}")
                                melhor_data = None

        if melhor_data:
            df_consolidado.at[index, 'Data'] = melhor_data
        else:
            print(f"⚠️ Nenhuma data encontrada para 'Conta': {conta}")

    with pd.ExcelWriter(dados_consolidados, engine='xlsxwriter', datetime_format='dd/mm/yyyy') as writer:
        df_consolidado.to_excel(writer, sheet_name=sheet_name, index=False) 
    print("\n✅ Atualização concluída!")

# Chamada da função
dados_consolidados = "dados_consolidados.xlsx"
arquivo_referencia = "jlp carga de dados 20250305 (1).xlsx"

preencher_datas_faltantes(dados_consolidados, arquivo_referencia, start_month="Fev", start_year=2017, end_year=2025)


''''
if __name__ == "__main__":
    file_name = "jlp carga de dados 20250305 (1).xlsx"
    sheet_names = generate_possible_sheet_names()
    process_excel(file_name, sheet_names)
'''