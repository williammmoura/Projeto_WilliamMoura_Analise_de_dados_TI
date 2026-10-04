"""ETL das vendas: limpeza, tipagem, ausentes e colunas derivadas."""

from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_ENTRADA = RAIZ_PROJETO / "data" / "raw" / "vendas_exportadas.csv"
CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "processed" / "vendas_tratadas.csv"

RENOMEAR_COLUNAS = {
    "invoice_id": "id_venda",
    "branch": "filial",
    "city": "cidade",
    "customer_type": "tipo_cliente",
    "gender": "genero",
    "product_line": "linha_produto",
    "unit_price": "preco_unitario",
    "quantity": "quantidade",
    "tax_5pct": "imposto",
    "sales": "valor_total",
    "sale_date": "data_venda",
    "sale_time": "hora_venda",
    "payment": "forma_pagamento",
    "cogs": "custo_mercadoria",
    "gross_margin_percentage": "margem_percentual",
    "gross_income": "receita_bruta",
    "rating": "avaliacao",
}

COLUNAS_TEXTO = [
    "id_venda",
    "filial",
    "cidade",
    "tipo_cliente",
    "genero",
    "linha_produto",
    "forma_pagamento",
]
COLUNAS_OPCIONAIS = ["tipo_cliente", "genero"]
COLUNAS_DECIMAIS = [
    "preco_unitario",
    "imposto",
    "valor_total",
    "custo_mercadoria",
    "margem_percentual",
    "receita_bruta",
    "avaliacao",
]
TOLERANCIA_TOTAL = 0.02
DIAS_SEMANA = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}


def carregar_dados(caminho):
    """Lê o CSV exportado do banco (camada Raw)."""
    return pd.read_csv(caminho)


def renomear_colunas(df):
    """Troca os nomes em inglês pelos nomes do dicionário de dados."""
    return df.rename(columns=RENOMEAR_COLUNAS)


def limpar_texto(df):
    """Remove espaços extras no início e no fim dos textos."""
    for coluna in COLUNAS_TEXTO:
        df[coluna] = df[coluna].str.strip()
    return df


def converter_tipos(df):
    """Converte datas, horas e números. Valores inválidos viram nulos."""
    df["data_venda"] = pd.to_datetime(
        df["data_venda"], format="%m/%d/%Y", errors="coerce"
    )
    hora = pd.to_datetime(
        df["hora_venda"], format="%I:%M:%S %p", errors="coerce"
    )
    df["hora_venda"] = hora.dt.strftime("%H:%M:%S")
    df["quantidade"] = pd.to_numeric(
        df["quantidade"], errors="coerce"
    ).astype("Int64")
    for coluna in COLUNAS_DECIMAIS:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce").round(2)
    return df


def tratar_ausentes(df):
    """Preenche textos opcionais e remove linhas sem campos obrigatórios."""
    print(f"Ausentes antes do tratamento: {df.isnull().sum().sum()}")
    df[COLUNAS_OPCIONAIS] = df[COLUNAS_OPCIONAIS].fillna("Não informado")
    obrigatorias = [c for c in df.columns if c not in COLUNAS_OPCIONAIS]
    antes = len(df)
    df = df.dropna(subset=obrigatorias)
    print(f"Linhas removidas por ausência de dados: {antes - len(df)}")
    return df


def remover_duplicatas(df):
    """Remove linhas repetidas e vendas com o mesmo id."""
    antes = len(df)
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="id_venda")
    print(f"Duplicatas removidas: {antes - len(df)}")
    return df


def aplicar_regras_de_negocio(df):
    """Mantém só as linhas que respeitam as regras CHECK do banco."""
    regras = (
        (df["preco_unitario"] >= 0)
        & (df["quantidade"] > 0)
        & (df["imposto"] >= 0)
        & (df["valor_total"] >= 0)
        & (df["custo_mercadoria"] >= 0)
        & (df["receita_bruta"] >= 0)
        & df["avaliacao"].between(0, 10)
    )
    print(f"Linhas que violam regras de negócio: {(~regras).sum()}")
    return df[regras].copy()


def criar_colunas_derivadas(df):
    """Cria colunas novas a partir das existentes (feature engineering)."""
    df["mes"] = df["data_venda"].dt.month
    df["dia_semana"] = df["data_venda"].dt.dayofweek.map(DIAS_SEMANA)
    df["hora"] = df["hora_venda"].str[:2].astype(int)
    df["faixa_valor"] = pd.qcut(
        df["valor_total"],
        q=4,
        labels=["Baixo", "Médio", "Alto", "Muito alto"],
    ).astype(str)
    calculado = df["preco_unitario"] * df["quantidade"] + df["imposto"]
    diferenca = (df["valor_total"] - calculado).abs()
    df["total_confere"] = diferenca <= TOLERANCIA_TOTAL
    return df


def salvar_dados(df, caminho):
    """Grava a base tratada em CSV, criando a pasta se preciso."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8", date_format="%Y-%m-%d")
    print(f"Arquivo salvo em: {caminho}")


def relatorio_final(df):
    """Mostra um resumo do resultado para conferência."""
    print(f"\nLinhas finais: {len(df)} | Colunas: {df.shape[1]}")
    print("\nTipos de dados:")
    print(df.dtypes)
    print(f"\nTotal não confere em {(~df['total_confere']).sum()} vendas")
    igual = (df["imposto"] == df["receita_bruta"]).all()
    print(f"Imposto igual à receita bruta em todas as linhas: {igual}")
    print(f"Valores distintos de margem: {df['margem_percentual'].nunique()}")
    print(df.head())


def main():
    """Executa o ETL completo."""
    df = carregar_dados(CAMINHO_ENTRADA)
    print(f"Linhas lidas: {len(df)}")
    df = renomear_colunas(df)
    df = limpar_texto(df)
    df = converter_tipos(df)
    df = tratar_ausentes(df)
    df = remover_duplicatas(df)
    df = aplicar_regras_de_negocio(df)
    df = criar_colunas_derivadas(df)
    df = df.reset_index(drop=True)
    salvar_dados(df, CAMINHO_SAIDA)
    relatorio_final(df)


if __name__ == "__main__":
    main()