import pandas as pd
import numpy as np

def run_demand_forecast():
    # 1. Carregar os dados (Camada Bronze)
    products = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/products.csv')
    variants = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/product_variants.csv')
    orders = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/orders.csv')
    order_items = pd.read_csv('/home/gustavo/Documentos/workspace/indicium-lighthouse/desafio-lighthouse-lh-nautical/data/01_bronze/order_items.csv')

    # 2. Filtrar o produto específico e mapear suas variantes
    prod_id = products.loc[products['name'] == 'Bússola de Bordo 702', 'id'].iloc[0]
    var_ids = variants.loc[variants['product_id'] == prod_id, 'id'].tolist()

    # 3. Unificar o Dataset (apenas itens da bússola com seus respectivos pedidos)
    df_items = order_items[order_items['product_variant_id'].isin(var_ids)]
    df = df_items.merge(orders, left_on='order_id', right_on='id', suffixes=('_item', '_order'))

    # 4. Preparar série temporal (Agregação Mensal)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['month'] = df['created_at'].dt.to_period('M')
    
    # Soma de quantidades vendidas por mês
    monthly_sales = df.groupby('month')['quantity'].sum().reset_index()

    # Garantir que a linha do tempo seja contínua (preencher meses sem venda com 0)
    min_month = df['month'].min()
    max_month = pd.Period('2026-03', freq='M')
    all_months = pd.period_range(start=min_month, end=max_month, freq='M')
    
    monthly_sales = monthly_sales.set_index('month').reindex(all_months, fill_value=0).reset_index()
    monthly_sales.columns = ['month', 'quantity']
    monthly_sales = monthly_sales.sort_values('month').reset_index(drop=True)

    # 5. Criar a Média Móvel (Baseline)
    # Janela de 3 meses, usando shift(1) para olhar apenas para o passado
    monthly_sales['pred_3m_ma'] = monthly_sales['quantity'].rolling(window=3).mean().shift(1)

    # 6. Separar o Período de Teste (Primeiro Trimestre de 2026)
    test_period = ['2026-01', '2026-02', '2026-03']
    test_df = monthly_sales[monthly_sales['month'].astype(str).isin(test_period)]

    # 7. Calcular o MAE (Mean Absolute Error) e a Soma das Previsões
    mae = np.mean(np.abs(test_df['quantity'] - test_df['pred_3m_ma']))
    soma_previsao = np.round(test_df['pred_3m_ma'].sum())

    print("--- Resultados do Período de Teste (Q1 2026) ---")
    print(test_df[['month', 'quantity', 'pred_3m_ma']].to_string(index=False))
    print(f"\nMAE (Erro Absoluto Médio): {mae:.2f} unidades")
    print(f"Soma Total da Previsão (Arredondada): {int(soma_previsao)} unidades")

if __name__ == '__main__':
    run_demand_forecast()
