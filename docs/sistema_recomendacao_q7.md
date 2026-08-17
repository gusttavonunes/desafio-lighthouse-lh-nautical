### Questão 7.2 - Validação

Após a execução do algoritmo de Filtragem Colaborativa sobre os dados operacionais, o nome do produto com a MAIOR similaridade ao "Motor de Popa 1949" é o Motor de Popa 5331 (com um score de 0.2565).

(Os próximos do ranking, compondo o Top 5, são: "Cabo Náutico 2105", "Vela Mestra 1913", "Cabo Náutico 9048" e "GPS Plotter 6249").

## Questão 7.3

Como a matriz foi construída?

A matriz foi construída primeiro unindo o caminho transacional inteiro: orders -> order_items -> product_variants -> products. Isso permitiu descobrir qual customer_id comprou qual product_id. Em seguida, aplicamos a regra de negócio exigida: ignoramos a quantidade e a repetição de compras (usando .drop_duplicates()), atribuindo o valor numérico 1 para indicar presença. Por fim, aplicamos a operação de .pivot(), transformando cada cliente único em uma linha, cada produto do catálogo em uma coluna, e preenchendo com 0 os cruzamentos onde não houve compra.

O que significa a similaridade de cosseno nesse contexto?

Na Similaridade de Cosseno, cada produto do catálogo é tratado como um vetor matemático cujas coordenadas são os clientes (se o cliente A comprou, a coordenada do cliente A vale 1, caso contrário, 0). O cosseno calcula o ângulo entre dois vetores de produto no espaço multidimensional de clientes. Na prática da LH Nautical, isso significa que produtos com um valor mais próximo de 1.0 compartilham a mesma base de clientes compradores. O motor recomenda produtos baseando-se no comportamento de rebanho: "a maioria dos clientes que comprou o Motor 1949, também comprou o Motor 5331 e o Cabo Náutico 2105".

Uma limitação desse método de recomendação.

A principal limitação é o conhecido problema de Cold Start (Partida Fria). Como o cálculo de similaridade depende integralmente do comportamento passado de compras conjuntas, um produto novo cadastrado ontem (ex: uma nova Defensa de alta performance) terá um vetor completamente preenchido por zeros. Sendo assim, sua similaridade com qualquer outro item da loja será zero. O sistema não conseguirá recomendá-lo até que um volume mínimo de clientes o descubra organicamente e o compre junto com outros itens, limitando a divulgação de lançamentos.