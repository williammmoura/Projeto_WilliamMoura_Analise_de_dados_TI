-- sql/02_criar_tabelas.sql
-- Cria as tabelas da camada Raw e da camada Tratada.

DROP TABLE IF EXISTS vendas_tratadas;
DROP TABLE IF EXISTS raw_vendas;

-- Camada Raw: copia fiel do CSV, tudo como texto, na mesma ordem
CREATE TABLE raw_vendas (
    invoice_id              TEXT,
    branch                  TEXT,
    city                    TEXT,
    customer_type           TEXT,
    gender                  TEXT,
    product_line            TEXT,
    unit_price              TEXT,
    quantity                TEXT,
    tax_5pct                TEXT,
    sales                   TEXT,
    sale_date               TEXT,
    sale_time               TEXT,
    payment                 TEXT,
    cogs                    TEXT,
    gross_margin_percentage TEXT,
    gross_income            TEXT,
    rating                  TEXT
);

-- Camada Tratada: tipos corretos e restricoes
CREATE TABLE vendas_tratadas (
    id_venda          VARCHAR(50)   PRIMARY KEY NOT NULL,
    filial            VARCHAR(10)   NOT NULL,
    cidade            VARCHAR(100)  NOT NULL,
    tipo_cliente      VARCHAR(50),
    genero            VARCHAR(20),
    linha_produto     VARCHAR(150)  NOT NULL,
    preco_unitario    NUMERIC(10,2) CHECK (preco_unitario >= 0),
    quantidade        INTEGER       CHECK (quantidade > 0),
    imposto           NUMERIC(10,2) CHECK (imposto >= 0),
    valor_total       NUMERIC(12,2) CHECK (valor_total >= 0),
    data_venda        DATE,
    hora_venda        TIME,
    forma_pagamento   VARCHAR(50)   NOT NULL,
    custo_mercadoria  NUMERIC(12,2) CHECK (custo_mercadoria >= 0),
    margem_percentual NUMERIC(10,2),
    receita_bruta     NUMERIC(12,2) CHECK (receita_bruta >= 0),
    avaliacao         NUMERIC(4,2)  CHECK (avaliacao BETWEEN 0 AND 10)
);