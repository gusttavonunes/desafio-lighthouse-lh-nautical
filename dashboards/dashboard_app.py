import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------------------------------------------------
# 1. Configurações da Página e Conexão com Banco de Dados
# -----------------------------------------------------------------------------
st.set_page_config(page_title="LH Nautical - Inteligência de Dados", layout="wide")
st.title("⚓ LH Nautical - Dashboard Executivo")
st.markdown("Visão consolidada da operação, conectada diretamente ao PostgreSQL (Camada Gold).")

# Instancia a engine de conexão (mantendo a URI configurada)
DB_URI = 'postgresql://postgres:password@localhost:5432/lh_nautical_db'
engine = create_engine(DB_URI)

# -----------------------------------------------------------------------------
# 2. Funções de Extração de Dados (Com Cache para Performance)
# -----------------------------------------------------------------------------

@st.cache_data
def load_vendas_dias_semana():
    """Consulta SQL para a Média Diária (Questão 5) cruzada com Calendário."""
    query = """
        WITH limites_data AS (
            SELECT MIN(DATE(created_at)) AS data_inicio, MAX(DATE(created_at)) AS data_fim FROM orders WHERE channel = 'pos'
        ),
        calendario AS (
            SELECT 
                data_calendario::DATE AS data_calendario,
                EXTRACT(DOW FROM data_calendario) AS num_dia_semana,
                CASE EXTRACT(DOW FROM data_calendario)
                    WHEN 0 THEN 'Domingo' WHEN 1 THEN 'Segunda-feira' WHEN 2 THEN 'Terça-feira'
                    WHEN 3 THEN 'Quarta-feira' WHEN 4 THEN 'Quinta-feira' WHEN 5 THEN 'Sexta-feira' WHEN 6 THEN 'Sábado'
                END AS nome_dia_semana
            FROM limites_data, GENERATE_SERIES(data_inicio, data_fim, '1 day'::interval) AS data_calendario
        ),
        vendas_diarias AS (
            SELECT DATE(created_at) AS data_venda, SUM(total) AS total_vendido
            FROM orders WHERE channel = 'pos' GROUP BY DATE(created_at)
        ),
        cruzamento AS (
            SELECT c.num_dia_semana, c.nome_dia_semana, COALESCE(v.total_vendido, 0) AS valor_venda_diaria
            FROM calendario c LEFT JOIN vendas_diarias v ON c.data_calendario = v.data_venda
        )
        SELECT 
            nome_dia_semana AS "Dia da Semana",
            ROUND(AVG(valor_venda_diaria)::NUMERIC, 2) AS "Média Diária Ajustada (R$)",
            SUM(CASE WHEN valor_venda_diaria = 0 THEN 1 ELSE 0 END) AS "Dias Zerados",
            num_dia_semana
        FROM cruzamento
        GROUP BY num_dia_semana, nome_dia_semana
        ORDER BY num_dia_semana;
    """
    return pd.read_sql(query, con=engine)

@st.cache_data
def load_previsao_demanda():
    """Traz o histórico da bússola via SQL e processa a média móvel no Python (Questão 6)."""
    # Adicionado ::TIMESTAMP para forçar a conversão e evitar o erro de tipagem do PostgreSQL
    query = """
        SELECT 
            DATE_TRUNC('month', o.created_at::TIMESTAMP) AS mes,
            SUM(oi.quantity) AS quantity
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN product_variants pv ON oi.product_variant_id = pv.id
        JOIN products p ON pv.product_id = p.id
        WHERE p.name = 'Bússola de Bordo 702'
        GROUP BY DATE_TRUNC('month', o.created_at::TIMESTAMP)
        ORDER BY mes;
    """
    df = pd.read_sql(query, con=engine)
    
    # Processamento da Média Móvel (Baseline)
    df['mes'] = pd.to_datetime(df['mes']).dt.to_period('M')
    
    # Preenchimento de meses vazios
    min_month = df['mes'].min()
    max_month = pd.Period('2026-03', freq='M')
    all_months = pd.period_range(start=min_month, end=max_month, freq='M')
    
    df = df.set_index('mes').reindex(all_months, fill_value=0).reset_index()
    df.columns = ['Mês', 'Realizado']
    df = df.sort_values('Mês').reset_index(drop=True)
    
    # Calcula baseline e filtra apenas Q1/2026
    df['Previsão (Baseline)'] = df['Realizado'].rolling(window=3).mean().shift(1)
    df['Mês'] = df['Mês'].astype(str)
    
    return df[df['Mês'].isin(['2026-01', '2026-02', '2026-03'])]

@st.cache_data
def load_recomendacoes():
    """Constrói a matriz de similaridade via processamento vetorial (Questão 7)."""
    query = """
        SELECT DISTINCT o.customer_id, p.id AS product_id, p.name
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN product_variants pv ON oi.product_variant_id = pv.id
        JOIN products p ON pv.product_id = p.id;
    """
    data = pd.read_sql(query, con=engine)
    data['purchased'] = 1
    
    # Pivot e Similaridade
    matrix = data.pivot(index='customer_id', columns='product_id', values='purchased').fillna(0)
    item_matrix = matrix.T
    similarity_matrix = cosine_similarity(item_matrix)
    
    sim_df = pd.DataFrame(similarity_matrix, index=item_matrix.index, columns=item_matrix.index)
    
    # Busca para o Motor 1949
    target_name = "Motor de Popa 1949"
    target_id = data.loc[data['name'] == target_name, 'product_id'].iloc[0]
    
    target_sims = sim_df[target_id].sort_values(ascending=False).drop(target_id)
    top_5_ids = target_sims.head(5).index
    
    # Mapeia nomes
    names_map = data[['product_id', 'name']].drop_duplicates().set_index('product_id')
    top_5_names = names_map.loc[top_5_ids]['name']
    
    return pd.DataFrame({
        'Produto': top_5_names,
        'Score de Similaridade': target_sims.head(5).values
    })

# -----------------------------------------------------------------------------
# 3. Construção do Layout e Gráficos
# -----------------------------------------------------------------------------

# Carrega os dados reais do banco
try:
    dados_dias_semana = load_vendas_dias_semana()
    dados_previsao = load_previsao_demanda()
    dados_similares = load_recomendacoes()
    db_status = "🟢 Conectado ao PostgreSQL"
except Exception as e:
    st.error(f"Erro ao conectar no banco de dados. Verifique o serviço PostgreSQL. Erro: {e}")
    st.stop()

st.caption(db_status)

tab1, tab2, tab3 = st.tabs(["🛒 Lojas Físicas & Vendas", "📈 Previsão de Demanda (IA)", "🤖 Recomendações"])

with tab1:
    st.subheader("Média de Vendas por Dia da Semana (Ajustada com Calendário)")
    st.markdown("Correção estatística inserindo R$ 0,00 para dias em que a loja abriu, mas não vendeu (Evitando Viés de Sobrevivência).")
    
    # Ordena pelo numero do dia da semana de forma oculta no grafico
    fig_dias = px.bar(dados_dias_semana, x='Dia da Semana', y='Média Diária Ajustada (R$)', 
                      color='Dias Zerados', text_auto='.2s', 
                      color_continuous_scale='Reds',
                      hover_data=['Dias Zerados'])
    # Trava a ordem do eixo X com base na nossa query SQL que já trouxe ordenado
    fig_dias.update_xaxes(categoryorder='array', categoryarray=dados_dias_semana['Dia da Semana'])
    st.plotly_chart(fig_dias, use_container_width=True)

with tab2:
    st.subheader("Performance do Modelo Preditivo (Q1/2026)")
    st.markdown("**Produto:** Bússola de Bordo 702 | Previsão baseada em Média Móvel de 3 meses.")
    
    fig_prev = px.line(dados_previsao, x='Mês', y=['Realizado', 'Previsão (Baseline)'], markers=True,
                       title="Comparativo: Demanda Real vs. Modelo Baseline")
    st.plotly_chart(fig_prev, use_container_width=True)

with tab3:
    st.subheader("Vitrine Inteligente: Motor de Popa 1949")
    st.markdown("Top 5 produtos sugeridos pelo algoritmo de Similaridade de Cosseno (Filtragem Colaborativa).")
    
    fig_sim = px.bar(dados_similares.sort_values('Score de Similaridade', ascending=True), 
                     x='Score de Similaridade', y='Produto', orientation='h',
                     title="Grau de Afinidade de Compra", color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig_sim, use_container_width=True)

st.divider()
st.caption("Desenvolvido para o Desafio Técnico LH Nautical | Arquitetura Medalhão & Python")
