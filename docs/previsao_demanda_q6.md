### Questão 6.2 - Validação
Rodando o modelo com os dados brutos históricos, os resultados para o produto "Bússola de Bordo 702" são:

Janeiro de 2026: Previsão de ~25,33 unidades

Fevereiro de 2026: Previsão de ~39,66 unidades

Março de 2026: Previsão de ~41,66 unidades

A soma total da previsão de vendas para o primeiro trimestre de 2026 é de `107 unidades` (arredondado).


### Questão 6.3

a. Como o baseline foi construído?
O baseline foi construído unificando as tabelas de pedidos, itens e produtos para isolar o histórico da "Bússola de Bordo 702". Agrupamos as quantidades vendidas por mês de forma contínua (preenchendo meses sem vendas com zero) e aplicamos uma regra matemática simples: a previsão do mês atual é a média aritmética das vendas dos últimos 3 meses imediatamente anteriores.

b. Como evitou o Data Leakage (Vazamento de Dados)?
O vazamento de dados ocorre quando um modelo usa informações do futuro para prever o próprio futuro. No pandas, ao aplicarmos o método .rolling(window=3).mean(), ele calcula a média incluindo a própria linha atual. Para evitar isso, apliquei o método .shift(1). Dessa forma, o cálculo é empurrado uma linha para baixo, garantindo estritamente que a previsão de Janeiro de 2026, por exemplo, não tenha "visto" o que aconteceu em Janeiro, enxergando apenas os dados até 31/12/2025.

c. Uma limitação do modelo proposto (e se é adequado):

- Limitação: A média móvel é "míope" e não captura sazonalidade e tendência. Em um negócio náutico (LH Nautical), sabemos que as vendas disparam no verão. Como a média móvel olha apenas para os últimos 3 meses, ao tentar prever o início do verão, ela vai usar os meses de inverno/primavera como base, puxando a previsão drasticamente para baixo e causando rupturas de estoque (exatamente o que irritou o Sr. Almir no ano passado).

- É adequado? Não para uso final, mas cumpre perfeitamente o seu papel de Baseline. Ele serve como a "pior nota a ser superada". Se agora o Gabriel treinar um modelo de Prophet ou XGBoost e ele tiver um MAE maior que 16.44, saberemos que a complexidade da IA não está agregando valor ao negócio.