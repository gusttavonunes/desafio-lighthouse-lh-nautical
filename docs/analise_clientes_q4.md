## Questão 4.2 - Explique
### 1. Como você chegou nas categorias mais vendidas? (Mapeamento da cadeia de chaves)
Para chegar à categoria final consumida, foi necessário mapear o relacionamento correto entre os itens comprados e a árvore de produtos, já que a tabela `order_items` não se relaciona diretamente com `products`. A cadeia lógica foi:

- Partimos de `orders` (para isolar os clientes) e conectamos a `order_items` via `order_id`.

- Em `order_items`, temos o `product_variant_id` (que representa a variação física vendida, como uma cor ou tamanho específico).

- Fizemos um JOIN de `order_items` com `product_variants` usando a chave `product_variant_id = id`.

- A partir de `product_variants`, recuperamos o produto "pai" através da chave `product_id`.

- Com o produto "pai" (`products`) em mãos, acessamos o `category_id`.

- Por fim, conectamos à tabela `categories` para obter o nome final (`name`) da categoria.

### 2. Qual lógica utilizou para filtrar os clientes com diversidade mínima?
A lógica foi isolada na CTE (Common Table Expression) chamada `diversidade_clientes`. Nela, agrupamos o histórico de compras por `customer_id` e aplicamos a função `COUNT(DISTINCT p.category_id)`. É crucial usar o `DISTINCT` para garantir que, se um cliente comprou 50 itens da mesma categoria, isso conte apenas como "1" categoria explorada. Em seguida, na CTE `top_10_clientes_elite`, usamos a cláusula `WHERE dc.diversidade_categorias >= 13` para eliminar do ranking qualquer cliente que não atendeu a essa premissa de negócio estipulada pela Diretoria.

### 3. Como garantiu que a contagem de itens refletisse apenas os Top 10?
A garantia ocorreu no bloco de consulta final (`RESULTADO`). Em vez de fazer uma consulta global em todos os pedidos da empresa, eu utilizei a tabela virtual `top_10_clientes_elite` (que já estava filtrada e limitada a 10 registros por causa do `ORDER BY ... LIMIT 10`) como o ponto de partida do JOIN. Ao fazer `JOIN orders o ON tce.customer_id = o.customer_id`, o banco de dados descarta instantaneamente qualquer pedido que não pertença aos IDs desses 10 clientes específicos. A partir daí, as somas de `quantity` geradas nos JOINs seguintes refletem matematicamente e de forma isolada apenas o comportamento da elite.