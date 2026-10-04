# Dicionário de dados: vendas_tratadas.csv

Base tratada gerada por `src/02_etl_vendas.py` a partir de
`data/raw/vendas_exportadas.csv` (dataset Supermarket Sales, Kaggle).
1000 linhas e 22 colunas (17 originais e 5 derivadas).

## Colunas originais

| Coluna | Tipo | Origem (CSV original) | Descrição e regras |
|---|---|---|---|
| id_venda | VARCHAR(50) | Invoice ID | Número da fatura. Identifica a venda (chave primária, não repete) |
| filial | VARCHAR(10) | Branch | Filial da venda: Alex, Cairo ou Giza. Obrigatório |
| cidade | VARCHAR(100) | City | Cidade da filial: Yangon, Mandalay ou Naypyitaw. Obrigatório |
| tipo_cliente | VARCHAR(50) | Customer type | Member ou Normal. Se ausente, "Não informado" |
| genero | VARCHAR(20) | Gender | Female ou Male. Se ausente, "Não informado" |
| linha_produto | VARCHAR(150) | Product line | Categoria do produto (6 linhas). Obrigatório |
| preco_unitario | NUMERIC(10,2) | Unit price | Preço de uma unidade. Maior ou igual a 0 |
| quantidade | INTEGER | Quantity | Unidades vendidas. Maior que 0 |
| imposto | NUMERIC(10,2) | Tax 5% | Imposto de 5% sobre o custo da mercadoria. Maior ou igual a 0 |
| valor_total | NUMERIC(12,2) | Sales | Valor total da venda com imposto. Maior ou igual a 0 |
| data_venda | DATE | Date | Data da venda, no formato AAAA-MM-DD (original em mês/dia/ano) |
| hora_venda | TIME | Time | Hora da venda, no formato HH:MM:SS de 24 horas (original em 12 horas com AM/PM) |
| forma_pagamento | VARCHAR(50) | Payment | Cash, Credit card ou Ewallet. Obrigatório |
| custo_mercadoria | NUMERIC(12,2) | cogs | Custo da mercadoria vendida (preço unitário x quantidade, antes do imposto). Maior ou igual a 0 |
| margem_percentual | NUMERIC(10,2) | gross margin percentage | Margem bruta percentual. Vale 4,76 em todas as linhas |
| receita_bruta | NUMERIC(12,2) | gross income | Receita bruta da venda. Igual ao imposto em todas as linhas. Maior ou igual a 0 |
| avaliacao | NUMERIC(4,2) | Rating | Nota de satisfação do cliente, entre 0 e 10 (na base, de 4 a 10) |

## Colunas derivadas (criadas no ETL)

| Coluna | Tipo | Descrição |
|---|---|---|
| mes | INTEGER | Mês da venda (1 a 12), extraído de data_venda |
| dia_semana | VARCHAR | Dia da semana por extenso, de Segunda-feira a Domingo |
| hora | INTEGER | Hora cheia da venda (0 a 23), extraída de hora_venda |
| faixa_valor | VARCHAR | Quartil de valor_total: Baixo, Médio, Alto ou Muito alto |
| total_confere | BOOLEAN | Verdadeiro se valor_total é igual a preco_unitario x quantidade + imposto, com tolerância de 0,02 |

## Observações

- Valores monetários e a margem foram arredondados para 2 casas decimais.
- Cada filial corresponde a uma única cidade (Alex/Yangon, Cairo/Mandalay, Giza/Naypyitaw).
- As colunas derivadas existem apenas no CSV, e não na tabela `vendas_tratadas` do banco.