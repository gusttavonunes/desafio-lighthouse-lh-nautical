import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def run_recommendation_engine():
    # 1. Carregamento dos Dados
    products = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/products.csv')
    variants = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/product_variants.csv')
    orders = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/orders.csv')
    items = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/order_items.csv')

    # 2. Mapeamento de Chaves: Conectando Customer -> Order -> Item -> Variant -> Product
    df_items_variants = items.merge(variants, left_on='product_variant_id', right_on='id')
    df_with_products = df_items_variants.merge(products, left_on='product_id', right_on='id', suffixes=('', '_product'))
    df_final = df_with_products.merge(orders, left_on='order_id', right_on='id', suffixes=('', '_order'))

    # 3. Construção da Matriz Usuário-Item (Interação)
    # Removemos duplicatas para garantir que mesmo se o cliente comprou 10 vezes, conte apenas como "presença"
    interactions = df_final[['customer_id', 'product_id']].drop_duplicates()
    interactions['purchased'] = 1  

    # Pivot: Linhas=Clientes, Colunas=Produtos, Valores=1 (completando o resto com 0)
    user_item_matrix = interactions.pivot(
        index='customer_id', 
        columns='product_id', 
        values='purchased'
    ).fillna(0)

    # 4. Cálculo da Similaridade de Cosseno (Produto x Produto)
    # Transpomos a matriz para que as linhas sejam os produtos e as colunas os clientes
    item_user_matrix = user_item_matrix.T
    similarity_matrix = cosine_similarity(item_user_matrix)

    # Convertendo para DataFrame para facilitar o acesso por ID
    sim_df = pd.DataFrame(
        similarity_matrix, 
        index=item_user_matrix.index, 
        columns=item_user_matrix.index
    )

    # 5. Geração do Ranking para o "Motor de Popa 1949"
    target_name = "Motor de Popa 1949"
    target_id = products.loc[products['name'] == target_name, 'id'].iloc[0]

    # Ordena as similaridades
    target_sims = sim_df[target_id].sort_values(ascending=False)
    
    # Desconsidera o próprio motor (sempre terá similaridade 1.0)
    target_sims = target_sims.drop(target_id)

    # Coleta os Top 5
    top_5_ids = target_sims.head(5).index
    top_5_names = products.set_index('id').loc[top_5_ids]['name']

    print(f"--- Top 5 Produtos Similares ao '{target_name}' ---")
    for i, (prod_id, sim) in enumerate(target_sims.head(5).items(), 1):
        name = top_5_names.loc[prod_id]
        print(f"{i}. {name} (Score de Similaridade: {sim:.4f})")

if __name__ == '__main__':
    run_recommendation_engine()
