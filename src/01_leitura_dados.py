"""Leitura e inspeção inicial do CSV exportado do PostgreSQL (camada Raw)."""

from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_CSV = RAIZ_PROJETO / "data" / "raw" / "vendas_exportadas.csv"

COLUNAS_CATEGORICAS = [
    "branch",
    "city",
    "customer_type",
    "gender",
    "product_line",
    "payment",
]


def configurar_exibicao():
    """Evita que o Pandas esconda colunas ao imprimir."""
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)


def titulo(texto):
    """Imprime um título para separar as seções da saída."""
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def carregar_dados(caminho):
    """Lê o CSV e devolve um DataFrame."""
    return pd.read_csv(caminho)


def inspecionar_estrutura(df):
    """Mostra tamanho, primeiras linhas e tipos de dados."""
    titulo("1. Estrutura (linhas, colunas)")
    print(df.shape)

    titulo("2. Primeiras linhas")
    print(df.head())

    titulo("3. Tipos de dados e valores não nulos")
    df.info()


def inspecionar_qualidade(df):
    """Procura valores ausentes, duplicatas e categorias inconsistentes."""
    titulo("4. Valores ausentes por coluna")
    print(df.isnull().sum())

    titulo("5. Duplicidades")
    print(f"Linhas duplicadas: {df.duplicated().sum()}")
    print(f"IDs de venda repetidos: {df['invoice_id'].duplicated().sum()}")

    titulo("6. Valores únicos das colunas categóricas")
    for coluna in COLUNAS_CATEGORICAS:
        print(f"\n{coluna}:")
        print(df[coluna].value_counts(dropna=False))


def inspecionar_estatisticas(df):
    """Mostra estatísticas descritivas e o formato de data e hora."""
    titulo("7. Estatísticas descritivas (colunas numéricas)")
    print(df.describe().T.round(2))

    titulo("8. Formato de data e hora (amostra)")
    print(df[["sale_date", "sale_time"]].head())


def inspecionar_consistencia(df):
    """Conta valores que violam regras básicas do negócio."""
    titulo("9. Verificações de consistência")
    print(f"Preços negativos: {(df['unit_price'] < 0).sum()}")
    print(f"Quantidades menores ou iguais a zero: {(df['quantity'] <= 0).sum()}")
    print(f"Notas fora do intervalo 0 a 10: {(~df['rating'].between(0, 10)).sum()}")


def main():
    """Executa a inspeção completa."""
    configurar_exibicao()
    df = carregar_dados(CAMINHO_CSV)
    inspecionar_estrutura(df)
    inspecionar_qualidade(df)
    inspecionar_estatisticas(df)
    inspecionar_consistencia(df)


if __name__ == "__main__":
    main()