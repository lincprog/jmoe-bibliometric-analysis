import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import os

# CONFIGURAÇÕES
API_KEY = 'CHAVE_API_SCRAPERAPI'
SCRAPER_URL = 'http://api.scraperapi.com'
ARQUIVO_ENTRADA = 'artigos_jmoe_final.csv'
ARQUIVO_SAIDA = 'artigos_atualizados.csv'

# 1. Carregar os dados
df_original = pd.read_csv(ARQUIVO_ENTRADA)

# Se o arquivo de saída já existir, vamos carregar para continuar de onde parou
if os.path.exists(ARQUIVO_SAIDA):
    df = pd.read_csv(ARQUIVO_SAIDA)
    print(f"Retomando progresso do arquivo de saída. {len(df)} linhas carregadas.")
else:
    df = df_original.copy()
    df['Citações'] = None # Inicializa se for a primeira vez
    print("Iniciando novo processamento.")

def get_citacoes_scholar(titulo):
    # Se o título for inválido (NaN ou não for string), ignora
    if not isinstance(titulo, str) or titulo.strip() == "":
        return 0
    
    payload = {
        'api_key': API_KEY,
        'url': f'https://scholar.google.com/scholar?q={titulo}',
        'country_code': 'us'
    }
    try:
        response = requests.get(SCRAPER_URL, params=payload, timeout=60)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            result = soup.find("div", {"class": "gs_ri"})
            if result:
                link_citacao = result.find("a", string=re.compile(r"Citado por|Cited by|\d+ citations"))
                if link_citacao:
                    num = re.findall(r'\d+', link_citacao.get_text())
                    return int(num[0]) if num else 0
            return 0
        return None
    except Exception:
        return None

# 2. Loop de Processamento
print("Iniciando busca...")

for index, row in df.iterrows():
    # SÓ PROCESSA SE A COLUNA 'Citações' ESTIVER VAZIA (NaN ou None)
    if pd.isna(row['Citações']):
        titulo = row['titulo']
        
        # TRATAMENTO PARA O ERRO DO FLOAT (NaN)
        # Se o título for inválido, coloca 0 citações e pula
        if not isinstance(titulo, str):
            print(f"[{index+1}] Pulando: Título inválido/vazio encontrado.")
            df.at[index, 'Citações'] = 0
            continue

        print(f"[{index+1}/{len(df)}] Buscando: {titulo[:60]}...")
        
        resultado = get_citacoes_scholar(titulo)
        
        if resultado is not None:
            df.at[index, 'Citações'] = resultado
            # Salva o arquivo a cada sucesso (Checkpoint)
            df.to_csv(ARQUIVO_SAIDA, index=False)
            print(f"   -> Citações: {resultado}")
        
        time.sleep(1) 
    else:
        # Opcional: print informativo de que já existe dado ali
        pass

print(f"\n PROCESSO FINALIZADO! Arquivo salvo em: {ARQUIVO_SAIDA}")
