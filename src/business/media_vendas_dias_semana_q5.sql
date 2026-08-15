-- Script: Análise de Média de Vendas por Dia da Semana (Lojas Físicas)
-- Objetivo: Corrigir a média diária considerando dias com R$ 0,00 de faturamento
-- Banco de Destino: PostgreSQL

WITH limites_data AS (
    -- Passo 1: Descobre a data mínima e máxima para gerar o calendário
    SELECT 
        MIN(DATE(created_at)) AS data_inicio,
        MAX(DATE(created_at)) AS data_fim
    FROM orders
    WHERE channel = 'pos' -- Garante que estamos olhando apenas para o período das lojas físicas
),
calendario AS (
    -- Passo 2: Gera a dimensão de datas (uma linha para cada dia do período)
    SELECT 
        data_calendario::DATE AS data_calendario,
        -- Extrai o dia da semana (0=Domingo, 1=Segunda... no PostgreSQL)
        EXTRACT(DOW FROM data_calendario) AS num_dia_semana,
        -- Traduz o dia da semana para o Português
        CASE EXTRACT(DOW FROM data_calendario)
            WHEN 0 THEN 'Domingo'
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
        END AS nome_dia_semana
    FROM limites_data, 
         GENERATE_SERIES(data_inicio, data_fim, '1 day'::interval) AS data_calendario
),
vendas_diarias AS (
    -- Passo 3: Soma as vendas por dia, apenas nas lojas físicas
    SELECT 
        DATE(created_at) AS data_venda,
        SUM(total) AS total_vendido
    FROM orders
    WHERE channel = 'pos'
    GROUP BY DATE(created_at)
),
cruzamento_calendario_vendas AS (
    -- Passo 4: LEFT JOIN para garantir que todos os dias existam, trocando NULL por 0
    SELECT 
        c.data_calendario,
        c.num_dia_semana,
        c.nome_dia_semana,
        COALESCE(v.total_vendido, 0) AS valor_venda_diaria
    FROM calendario c
    LEFT JOIN vendas_diarias v ON c.data_calendario = v.data_venda
)

-- Passo 5: Calcula a média correta por dia da semana
SELECT 
    nome_dia_semana,
    ROUND(AVG(valor_venda_diaria), 2) AS media_vendas,
    -- Contagens adicionais úteis para o Sr. Almir entender a volumetria
    COUNT(*) AS total_dias_analisados,
    SUM(CASE WHEN valor_venda_diaria = 0 THEN 1 ELSE 0 END) AS dias_com_zero_vendas
FROM cruzamento_calendario_vendas
GROUP BY 
    num_dia_semana, 
    nome_dia_semana
ORDER BY 
    num_dia_semana;
