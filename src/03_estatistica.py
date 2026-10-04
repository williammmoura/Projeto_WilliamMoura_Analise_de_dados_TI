"""Estatística descritiva, respostas de negócio e gráficos."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

plt.switch_backend("Agg")

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_DADOS = RAIZ_PROJETO / "data" / "processed" / "vendas_tratadas.csv"
PASTA_RESULTADOS = RAIZ_PROJETO / "resultados"

COR_DESTAQUE = "#1f77b4"
COR_NEUTRA = "#b8c4d0"
ORDEM_DIAS = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]
COLUNAS_NUMERICAS = [
    "preco_unitario",
    "quantidade",
    "imposto",
    "valor_total",
    "avaliacao",
]


def carregar_dados(caminho):
    """Lê a base tratada."""
    return pd.read_csv(caminho)


def estatisticas_descritivas(df):
    """Calcula as estatísticas descritivas das colunas numéricas."""
    resumo = df[COLUNAS_NUMERICAS].describe().T.round(2)
    resumo["assimetria"] = df[COLUNAS_NUMERICAS].skew().round(2)
    print(resumo)
    return resumo


def calcular_metricas(df):
    """Calcula as métricas usadas nas respostas e nos gráficos."""
    filial = df.groupby("filial")
    linha = df.groupby("linha_produto")
    return {
        "faturamento_filial": (
            filial["valor_total"].sum().round(2).sort_values(ascending=False)
        ),
        "vendas_filial": filial.size().sort_values(ascending=False),
        "ticket_filial": filial["valor_total"].mean().round(2),
        "faturamento_linha": (
            linha["valor_total"].sum().round(2).sort_values(ascending=False)
        ),
        "vendas_linha": linha.size().sort_values(ascending=False),
        "avaliacao_linha": (
            linha["avaliacao"].mean().round(2).sort_values(ascending=False)
        ),
        "pagamento": df["forma_pagamento"].value_counts(),
        "dia_semana": df["dia_semana"].value_counts().reindex(ORDEM_DIAS),
    }


def registrar(respostas, numero, pergunta, hipotese, resposta):
    """Imprime a pergunta com hipótese e resposta e guarda para o CSV."""
    print(f"\nPergunta {numero}: {pergunta}")
    print(f"  Hipótese: {hipotese}")
    print(f"  Resposta: {resposta}")
    respostas.append(
        {
            "numero": numero,
            "pergunta": pergunta,
            "hipotese": hipotese,
            "resposta": resposta,
        }
    )


def responder_perguntas(df, m):
    """Responde as 8 perguntas de negócio e devolve a tabela de respostas."""
    respostas = []

    fat = m["faturamento_filial"]
    ticket = m["ticket_filial"][fat.idxmax()]
    registrar(
        respostas,
        1,
        "Qual filial apresentou o maior faturamento?",
        "A filial com mais vendas também é a de maior faturamento.",
        f"{fat.idxmax()} com {fat.max():.2f} (ticket médio {ticket:.2f}).",
    )

    vendas = m["vendas_filial"]
    dif = (vendas.max() - vendas.min()) / vendas.min() * 100
    registrar(
        respostas,
        2,
        "Qual filial realizou a maior quantidade de vendas?",
        "A diferença de vendas entre as filiais é pequena (menos de 10%).",
        f"{vendas.idxmax()} com {vendas.max()} vendas "
        f"(diferença de {dif:.1f}% entre a maior e a menor filial).",
    )

    fat_linha = m["faturamento_linha"]
    mais_vendida = m["vendas_linha"].idxmax()
    registrar(
        respostas,
        3,
        "Qual linha de produto apresentou o maior faturamento?",
        "A linha com mais vendas também é a de maior faturamento.",
        f"{fat_linha.idxmax()} com {fat_linha.max():.2f}. "
        f"A linha com mais vendas é {mais_vendida}.",
    )

    nota = m["avaliacao_linha"]
    registrar(
        respostas,
        4,
        "Qual linha de produto recebeu a melhor avaliação média?",
        "A linha de maior faturamento também tem a melhor avaliação.",
        f"{nota.idxmax()} com nota média {nota.max():.2f} "
        f"(a menor é {nota.idxmin()}, com {nota.min():.2f}).",
    )

    pag = m["pagamento"]
    percentual = pag.iloc[0] / len(df) * 100
    registrar(
        respostas,
        5,
        "Qual foi a forma de pagamento mais utilizada?",
        "Dinheiro (Cash) é a forma de pagamento mais usada.",
        f"{pag.index[0]} com {pag.iloc[0]} vendas ({percentual:.1f}%). "
        f"Em segundo, {pag.index[1]} com {pag.iloc[1]}.",
    )

    media = df["valor_total"].mean()
    mediana = df["valor_total"].median()
    desvio = df["valor_total"].std()
    registrar(
        respostas,
        6,
        "Qual foi o valor médio das vendas?",
        "A média é puxada para cima por poucas vendas muito altas.",
        f"Média {media:.2f} (mediana {mediana:.2f}, "
        f"desvio padrão {desvio:.2f}).",
    )

    maior = df.loc[df["valor_total"].idxmax()]
    registrar(
        respostas,
        7,
        "Qual foi a maior venda registrada?",
        "A maior venda ocorreu na filial de maior faturamento.",
        f"{maior['valor_total']:.2f} (fatura {maior['id_venda']}, "
        f"filial {maior['filial']}, {maior['linha_produto']}).",
    )

    dia = m["dia_semana"]
    registrar(
        respostas,
        8,
        "Em qual dia da semana ocorreu a maior quantidade de vendas?",
        "O dia com mais vendas é sábado ou domingo.",
        f"{dia.idxmax()} com {int(dia.max())} vendas.",
    )

    return pd.DataFrame(respostas)


def salvar_barras(
    serie, titulo, rotulo_y, arquivo, formato="%.2f", limite_y=None
):
    """Desenha barras, destaca a maior e salva a figura em PNG."""
    cores = [COR_NEUTRA] * len(serie)
    cores[serie.to_numpy().argmax()] = COR_DESTAQUE
    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.bar(list(serie.index), serie.to_numpy(), color=cores)
    ax.bar_label(barras, fmt=formato, padding=3)
    ax.margins(y=0.12)
    if limite_y:
        ax.set_ylim(*limite_y)
    ax.set_title(titulo)
    ax.set_ylabel(rotulo_y)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(PASTA_RESULTADOS / arquivo, dpi=150)
    plt.close(fig)


def salvar_histograma(df):
    """Mostra a distribuição do valor das vendas com média e mediana."""
    media = df["valor_total"].mean()
    mediana = df["valor_total"].median()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df["valor_total"], bins=20, color=COR_NEUTRA, edgecolor="white")
    ax.axvline(media, color="red", linestyle="--", label=f"Média: {media:.2f}")
    ax.axvline(
        mediana,
        color=COR_DESTAQUE,
        linestyle="-",
        label=f"Mediana: {mediana:.2f}",
    )
    ax.set_title("Distribuição do valor das vendas")
    ax.set_xlabel("Valor total da venda")
    ax.set_ylabel("Quantidade de vendas")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PASTA_RESULTADOS / "06_distribuicao_valor_vendas.png", dpi=150)
    plt.close(fig)


def gerar_graficos(df, m):
    """Gera e salva os gráficos que sustentam as respostas."""
    salvar_barras(
        m["faturamento_filial"],
        "Faturamento por filial",
        "Faturamento",
        "01_faturamento_filial.png",
    )
    salvar_barras(
        m["vendas_filial"],
        "Quantidade de vendas por filial",
        "Vendas",
        "02_vendas_filial.png",
        formato="%d",
    )
    salvar_barras(
        m["faturamento_linha"],
        "Faturamento por linha de produto",
        "Faturamento",
        "03_faturamento_linha_produto.png",
    )
    salvar_barras(
        m["avaliacao_linha"],
        "Avaliação média por linha de produto",
        "Nota média (0 a 10)",
        "04_avaliacao_linha_produto.png",
        limite_y=(0, 10),
    )
    salvar_barras(
        m["pagamento"],
        "Vendas por forma de pagamento",
        "Vendas",
        "05_forma_pagamento.png",
        formato="%d",
    )
    salvar_histograma(df)
    salvar_barras(
        m["dia_semana"],
        "Vendas por dia da semana",
        "Vendas",
        "07_vendas_dia_semana.png",
        formato="%d",
    )


def salvar_tabelas(resumo, respostas):
    """Salva as estatísticas e as respostas em CSV."""
    resumo.to_csv(
        PASTA_RESULTADOS / "estatisticas_descritivas.csv", encoding="utf-8"
    )
    respostas.to_csv(
        PASTA_RESULTADOS / "respostas_negocio.csv",
        index=False,
        encoding="utf-8",
    )


def main():
    """Executa a análise completa."""
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    df = carregar_dados(CAMINHO_DADOS)
    print(f"Base carregada: {len(df)} linhas")

    print("\n=== Estatísticas descritivas ===")
    resumo = estatisticas_descritivas(df)

    metricas = calcular_metricas(df)
    print("\n=== Perguntas de negócio ===")
    respostas = responder_perguntas(df, metricas)

    gerar_graficos(df, metricas)
    salvar_tabelas(resumo, respostas)
    print(f"\nGráficos e tabelas salvos em: {PASTA_RESULTADOS}")


if __name__ == "__main__":
    main()