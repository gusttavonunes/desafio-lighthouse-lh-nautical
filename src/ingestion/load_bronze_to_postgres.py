import os
import pandas as pd
from sqlalchemy import create_engine

# Configurações de diretório seguindo a arquitetura do projeto
INPUT_DIR = '/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze'

# String de conexão com o PostgreSQL (Altere para as credenciais reais do servidor)
DB_CONNECTION_STRING = 'postgresql://postgres:password@localhost:5432/lh_nautical_db'

def load_data_to_postgres():
    """
    Lê os arquivos CSV da camada Bronze e os insere no PostgreSQL.
    Nenhum tratamento de dados é realizado nesta etapa, respeitando a origem.
    """
    # Cria a engine de comunicação com o banco de dados
    engine = create_engine(DB_CONNECTION_STRING)
    
    if not os.path.exists(INPUT_DIR):
        print(f"Erro: O diretório {INPUT_DIR} não foi encontrado.")
        return

    # Lista todos os arquivos CSV do diretório
    csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
    
    for file in csv_files:
        table_name = file.replace('.csv', '').lower()
        file_path = os.path.join(INPUT_DIR, file)
        
        print(f"Iniciando a leitura do arquivo: {file} ...")
        
        # Leitura bruta do CSV (sem remoção de nulos ou tratamentos especiais)
        df = pd.read_csv(file_path)
        
        print(f"Carregando {len(df)} linhas na tabela '{table_name}' no PostgreSQL...")
        
        # Carregamento no banco. 
        # if_exists='append' garante que vamos inserir na tabela criada pelo schema.sql
        # index=False evita carregar o índice numérico do DataFrame como uma coluna
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        
        print(f"Sucesso: Tabela '{table_name}' carregada!\n")

if __name__ == '__main__':
    load_data_to_postgres()
