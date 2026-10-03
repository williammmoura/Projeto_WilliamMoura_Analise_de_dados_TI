-- sql/03_consultas.sql
-- Consultas sobre a camada Raw. Todas as colunas estao como TEXT,
-- entao os numeros precisam de conversao com ::NUMERIC ou ::INT.
-- Executar na raiz do projeto:
--   psql -U postgres -d supermercado -f sql/03_consultas.sql

-- 1. Inspecao: total de linhas e amostra
SELECT COUNT(*) AS total_linhas FROM raw_vendas;
SELECT invoice_id, branch, city, product_line, sales FROM raw_vendas LIMIT 5;

-- 2. Formato da data: se a 1a parte nunca passa de 12 e a 2a chega a 30 ou 31,
--    o formato e mes/dia/ano
SELECT MAX(SPLIT_PART(sale_date, '/', 1)::INT) AS maior_primeira_parte,
       MAX(SPLIT_PART(sale_date, '/', 2)::INT) AS maior_segunda_parte
FROM raw_vendas;

-- 3. Qual filial apresentou o maior faturamento?
SELECT branch AS filial,
       ROUND(SUM(sales::NUMERIC), 2) AS faturamento
FROM raw_vendas
GROUP BY branch
ORDER BY faturamento DESC;

-- 4. Qual filial realizou a maior quantidade de vendas?
SELECT branch AS filial,
       COUNT(*) AS qtd_vendas,
       SUM(quantity::INT) AS itens_vendidos
FROM raw_vendas
GROUP BY branch
ORDER BY qtd_vendas DESC;

-- 5. Qual linha de produto apresentou o maior faturamento?
SELECT product_line AS linha_produto,
       ROUND(SUM(sales::NUMERIC), 2) AS faturamento
FROM raw_vendas
GROUP BY product_line
ORDER BY faturamento DESC;

-- 6. Qual linha de produto recebeu a melhor avaliacao media?
SELECT product_line AS linha_produto,
       ROUND(AVG(rating::NUMERIC), 2) AS avaliacao_media
FROM raw_vendas
GROUP BY product_line
ORDER BY avaliacao_media DESC;

-- 7. Qual foi a forma de pagamento mais utilizada?
SELECT payment AS forma_pagamento,
       COUNT(*) AS qtd_vendas
FROM raw_vendas
GROUP BY payment
ORDER BY qtd_vendas DESC;

-- 8. Qual foi o valor medio das vendas?
SELECT ROUND(AVG(sales::NUMERIC), 2) AS valor_medio_venda
FROM raw_vendas;

-- 9. Qual foi a maior venda registrada?
SELECT invoice_id, branch, product_line, sales::NUMERIC AS valor_total
FROM raw_vendas
ORDER BY sales::NUMERIC DESC
LIMIT 1;

-- 10. Em qual dia da semana ocorreu a maior quantidade de vendas?
--     Assume formato mes/dia/ano (confira na consulta 2).
SELECT TO_CHAR(TO_DATE(sale_date, 'MM/DD/YYYY'), 'FMDay') AS dia_semana,
       COUNT(*) AS qtd_vendas
FROM raw_vendas
GROUP BY dia_semana
ORDER BY qtd_vendas DESC;

-- 11. Uso do WHERE: vendas com nota 9 ou mais, por linha de produto
SELECT product_line AS linha_produto,
       COUNT(*) AS qtd_vendas_nota_alta
FROM raw_vendas
WHERE rating::NUMERIC >= 9
GROUP BY product_line
ORDER BY qtd_vendas_nota_alta DESC;

-- Exportacao 1: base completa (o Python le este arquivo na etapa seguinte)
\copy (SELECT * FROM raw_vendas) TO 'data/raw/vendas_exportadas.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

-- Exportacao 2: resultado de uma consulta agregada
\copy (SELECT branch AS filial, ROUND(SUM(sales::NUMERIC), 2) AS faturamento FROM raw_vendas GROUP BY branch ORDER BY faturamento DESC) TO 'resultados/sql_faturamento_por_filial.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')