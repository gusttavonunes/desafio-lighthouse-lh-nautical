import os
import csv
from datetime import datetime

# Configurações de diretórios seguindo a arquitetura
INPUT_DIR = '/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze'
OUTPUT_FILE = '/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/src/config/schema.sql'

def infer_data_type(value: str) -> str:
    """Tenta inferir o tipo de dado de uma string."""
    value = value.strip()
    if not value:
        return None
        
    # Tenta Inteiro
    try:
        int(value)
        return 'INTEGER'
    except ValueError:
        pass
        
    # Tenta Decimal/Numeric
    try:
        float(value)
        return 'NUMERIC'
    except ValueError:
        pass
        
    # Tenta Timestamp (padrão ISO)
    try:
        datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return 'TIMESTAMP'
    except ValueError:
        pass

    # Tenta Date
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return 'DATE'
    except ValueError:
        pass
        
    return 'VARCHAR'

def resolve_column_type(types_found: set) -> str:
    """Define o tipo final da coluna baseado nos tipos encontrados nas linhas amostradas."""
    types_found.discard(None) # Remove nulos da avaliação
    
    if not types_found:
        return 'VARCHAR' # Se a coluna for inteira vazia
    if 'VARCHAR' in types_found:
        return 'VARCHAR' # Se tiver qualquer texto, prevalece VARCHAR
    if 'NUMERIC' in types_found:
        return 'NUMERIC' # Se tiver float e int, prevalece NUMERIC
    if 'TIMESTAMP' in types_found:
        return 'TIMESTAMP'
    if 'DATE' in types_found:
        return 'DATE'
    if 'INTEGER' in types_found:
        return 'INTEGER'
        
    return 'VARCHAR'

def generate_sql_for_csv(file_path: str, table_name: str, sample_size: int = 1000) -> str:
    """Lê um CSV e gera a string de CREATE TABLE."""
    col_types = {}
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        try:
            headers = next(reader)
        except StopIteration:
            return "" # Arquivo vazio
            
        # Inicializa o set de tipos para cada coluna
        for h in headers:
            col_types[h] = set()
            
        # Lê as primeiras linhas para inferência
        for i, row in enumerate(reader):
            if i >= sample_size:
                break
            for h, v in zip(headers, row):
                inferred = infer_data_type(v)
                if inferred:
                    col_types[h].add(inferred)
                    
    # Monta a query
    sql_lines = [f"CREATE TABLE {table_name} ("]
    col_defs = []
    
    for h in headers:
        final_type = resolve_column_type(col_types[h])
        col_defs.append(f"    {h} {final_type}")
        
    sql_lines.append(",\n".join(col_defs))
    sql_lines.append(");\n\n")
    
    return "\n".join(sql_lines)

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Diretório de entrada não encontrado: {INPUT_DIR}")
        return
        
    # Garante que a pasta de saída existe
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, mode='w', encoding='utf-8') as out_f:
        # Varre todos os arquivos da pasta Bronze
        for filename in os.listdir(INPUT_DIR):
            if filename.endswith('.csv'):
                file_path = os.path.join(INPUT_DIR, filename)
                table_name = filename.replace('.csv', '').lower()
                
                print(f"Processando tabela: {table_name}...")
                create_statement = generate_sql_for_csv(file_path, table_name)
                out_f.write(create_statement)
                
    print(f"Schema gerado com sucesso em: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()