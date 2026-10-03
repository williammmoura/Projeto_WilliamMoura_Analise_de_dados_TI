-- sql/02b_carga_raw.sql
-- Carga da camada Raw: copia o CSV para raw_vendas sem alterar nada.
-- Executar a partir da raiz do projeto (o caminho do arquivo e relativo).

TRUNCATE TABLE raw_vendas;

\copy raw_vendas FROM 'data/raw/supermarket_analysis.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

SELECT COUNT(*) AS total_linhas FROM raw_vendas;