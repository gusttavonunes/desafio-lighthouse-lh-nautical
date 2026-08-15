-- Script: Análise de Clientes Fiéis (Elite) e Categoria Favorita
-- Objetivo: Identificar o Top 10 clientes com maior Ticket Médio (min 13 categorias) 
--           e a categoria de produto mais consumida por eles.

WITH faturamento_frequencia AS (
    -- Passo 1: Calcula Faturamento Total e Frequência por cliente a partir da tabela orders
    SELECT 
        customer_id,
        SUM(total) AS faturamento_total,
        COUNT(id) AS frequencia
    FROM orders
    GROUP BY customer_id
),
diversidade_clientes AS (
    -- Passo 2: Calcula a Diversidade de Categorias por cliente
    -- Navegação: orders -> order_items -> product_variants -> products -> categories
    SELECT 
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    GROUP BY o.customer_id
),
top_10_clientes_elite AS (
    -- Passo 3: Une as métricas, calcula o Ticket Médio e aplica os filtros da Diretoria
    SELECT 
        ff.customer_id,
        ff.faturamento_total,
        ff.frequencia,
        (ff.faturamento_total / ff.frequencia) AS ticket_medio,
        dc.diversidade_categorias
    FROM faturamento_frequencia ff
    JOIN diversidade_clientes dc ON ff.customer_id = dc.customer_id
    WHERE dc.diversidade_categorias >= 13
    ORDER BY ticket_medio DESC, ff.customer_id ASC
    LIMIT 10
)

-- ============================================================================
-- RESULTADO: Categoria de produto que concentra a maior quantidade total de itens
-- (Filtro aplicado apenas aos 10 clientes de elite)
-- ============================================================================
SELECT 
    c.name AS nome_categoria,
    SUM(oi.quantity) AS total_itens_comprados
FROM top_10_clientes_elite tce
JOIN orders o ON tce.customer_id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN product_variants pv ON oi.product_variant_id = pv.id
JOIN products p ON pv.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY c.name
ORDER BY total_itens_comprados DESC
LIMIT 10;
