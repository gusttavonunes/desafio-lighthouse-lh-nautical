## 1. Por que é necessário utilizar uma tabela de datas (calendário) em vez de agrupar diretamente a tabela de vendas?

É necessário utilizar uma tabela de datas porque bancos de dados relacionais não registram o que não aconteceu. Se em um determinado domingo a loja física da LH Nautical abriu as portas, mas não realizou nenhuma venda, não haverá nenhuma linha gravada na tabela `orders` para aquele dia.  

Se agruparmos diretamente a tabela `orders`, o banco de dados calculará a média (Soma / Quantidade) dividindo o faturamento apenas pelos domingos em que houve vendas. Isso gera o chamado "Viés de Sobrevivência". A tabela de calendário atua como uma "espinha dorsal" contínua de tempo. Ao fazermos um `LEFT JOIN` do calendário com as vendas, forçamos o banco de dados a reconhecer a existência dos domingos vazios, substituindo a ausência de dados por R$ 0,00, o que garante a precisão matemática e temporal do relatório.

## 2. O que aconteceria com a média de vendas se um dia da semana tivesse muitos dias sem nenhuma venda registrada?

Sem o uso de um calendário, a média de vendas permaneceria artificialmente alta e maquiada.Por exemplo: Imagine que em um mês tivemos 4 domingos. Em apenas um domingo houve uma venda de R$ 5.000, e nos outros três a loja vendeu R$ 0.

- Erro do Estagiário (Direto na tabela): O banco acha que só existiu 1 domingo. Média = 5.000 / 1 = R$ 5.000,00.

- Realidade com Calendário (Sua abordagem): O banco sabe que existiram 4 domingos (5.000 + 0 + 0 + 0). Média = 5.000 / 4 = R$ 1.250,00.

Se um dia tem muitos registros zerados, a média real deve despencar de forma proporcional. Apresentar a média errada faria o Sr. Almir tomar a péssima decisão de manter a loja aberta e pagar funcionários em dias de prejuízo crônico, acreditando que esses dias são lucrativos.