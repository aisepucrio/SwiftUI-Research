from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

matplotlib.use("Agg")


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_PROCESSED_GITHUB_DIR = BASE_DIR / "data" / "processed" / "github"
DATA_PROCESSED_SO_DIR = BASE_DIR / "data" / "processed" / "stackoverflow"
DATA_PROCESSED_FORMS_DIR = BASE_DIR / "data" / "processed" / "forms"
DATA_PROCESSED_COMPARISON_DIR = BASE_DIR / "data" / "processed" / "comparacao"
OUTPUTS_COMPARISON_DIR = BASE_DIR / "outputs" / "comparacao"

ARQ_GITHUB_FREQ = DATA_PROCESSED_GITHUB_DIR / "freq_arquiteturas_total.csv"
ARQ_GITHUB_POP = DATA_PROCESSED_GITHUB_DIR / "popularidade_por_arquitetura.csv"
ARQ_SO_FREQ = DATA_PROCESSED_SO_DIR / "freq_arquiteturas_total.csv"
ARQ_SO_SCORE = DATA_PROCESSED_SO_DIR / "score_medio_por_arquitetura.csv"
ARQ_SO_SENT = DATA_PROCESSED_SO_DIR / "sentimento_por_arquitetura_resumo.csv"
ARQ_FORMS_USED = DATA_PROCESSED_FORMS_DIR / "arquiteturas_utilizadas_forms.csv"
ARQ_FORMS_MAIN = DATA_PROCESSED_FORMS_DIR / "arquitetura_principal_forms.csv"
ARQ_FORMS_BEST = DATA_PROCESSED_FORMS_DIR / "arquitetura_mais_adequada_forms.csv"

ENGLISH_COLUMNS = {
    "arquitetura": "architecture",
    "forms_ja_utilizou": "survey_used",
    "forms_ja_utilizou_share": "survey_used_share",
    "forms_ja_utilizou_rank": "survey_used_rank",
    "forms_principal": "survey_main",
    "forms_principal_share": "survey_main_share",
    "forms_principal_rank": "survey_main_rank",
    "forms_mais_adequada": "survey_most_suitable",
    "forms_mais_adequada_share": "survey_most_suitable_share",
    "forms_mais_adequada_rank": "survey_most_suitable_rank",
    "forms_unificado": "survey_used_main_combined",
    "forms_unificado_share": "survey_used_main_combined_share",
    "forms_unificado_rank": "survey_used_main_combined_rank",
    "stars_medio": "average_stars",
    "forks_medio": "average_forks",
    "score_medio_total": "average_stackoverflow_score",
    "score_medio_questions": "average_question_score",
    "score_medio_answers": "average_answer_score",
    "so_sent_positivo": "stackoverflow_positive",
    "so_sent_neutro": "stackoverflow_neutral",
    "so_sent_negativo": "stackoverflow_negative",
    "so_sent_total": "stackoverflow_sentiment_total",
    "so_sent_pos_share": "stackoverflow_positive_share",
    "so_sent_neu_share": "stackoverflow_neutral_share",
    "so_sent_neg_share": "stackoverflow_negative_share",
    "so_sentimento_predominante": "predominant_stackoverflow_sentiment",
    "presente_no_github": "present_on_github",
    "presente_no_stackoverflow": "present_on_stackoverflow",
    "presente_no_forms_utilizada": "present_in_survey_used",
    "presente_no_forms_principal": "present_in_survey_main",
    "presente_no_forms_adequada": "present_in_survey_most_suitable",
    "fontes_presentes": "sources_count",
    "presenca_fontes": "source_presence",
    "delta_share_github_vs_forms_principal": "delta_share_github_vs_survey_main",
    "delta_share_stackoverflow_vs_forms_principal": "delta_share_stackoverflow_vs_survey_main",
    "delta_share_forms_principal_vs_adequada": "delta_share_survey_main_vs_most_suitable",
    "gap_abs_github_vs_forms_principal": "gap_abs_github_vs_survey_main",
    "gap_abs_stackoverflow_vs_forms_principal": "gap_abs_stackoverflow_vs_survey_main",
    "media_share_gh_so_forms": "average_share_gh_so_survey",
    "amplitude_share_gh_so_forms": "share_range_gh_so_survey",
    "forms_ja_utilizou_share_norm": "survey_used_share_norm",
    "forms_mais_adequada_share_norm": "survey_most_suitable_share_norm",
    "stars_medio_norm": "average_stars_norm",
    "score_medio_total_norm": "average_stackoverflow_score_norm",
    "indice_alinhamento_gh_so_forms": "alignment_index_gh_so_survey",
    "indice_multicriterio": "multicriteria_index",
    "perfil_interpretativo": "interpretive_profile",
    "indicador": "indicator",
    "valor": "value",
    "quantidade": "count",
    "arquiteturas": "architectures",
    "media_github_share": "average_github_share",
    "media_stackoverflow_share": "average_stackoverflow_share",
    "media_forms_uso_share": "average_survey_used_share",
    "media_indice_multicriterio": "average_multicriteria_index",
    "indicador": "indicator",
    "ranking_multicriterio": "multicriteria_rank",
}


def salvar_csv(df: pd.DataFrame, filename: str) -> None:
    """Saves a DataFrame in the processed comparison directory."""
    out = DATA_PROCESSED_COMPARISON_DIR / filename
    df.rename(columns=ENGLISH_COLUMNS).to_csv(out, index=False)
    print(f"Saved: {out}")


def salvar_plot(filename: str) -> None:
    """Adjusts, saves, and closes the current Matplotlib figure."""
    out = OUTPUTS_COMPARISON_DIR / filename
    plt.tight_layout()
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Chart saved: {out}")


def normalizar_serie(series: pd.Series) -> pd.Series:
    """Normalizes a numeric series to the 0-1 range."""
    max_value = series.max()
    min_value = series.min()
    if pd.isna(max_value) or max_value == min_value:
        return pd.Series(0, index=series.index)
    return (series - min_value) / (max_value - min_value)


def adicionar_share_rank(df: pd.DataFrame, count_col: str, prefix: str) -> pd.DataFrame:
    """Adds relative share and dense ranking to a count metric."""
    total = df[count_col].sum()
    df[f"{prefix}_share"] = df[count_col] / total if total else 0
    df[f"{prefix}_rank"] = df[count_col].rank(method="dense", ascending=False).astype(int)
    return df


def classificar_perfil(row: pd.Series) -> str:
    """Classifies an architecture into an article-friendly interpretive profile."""
    gh = row["github_share"]
    so = row["stackoverflow_share"]
    forms = row["forms_ja_utilizou_share"]
    best = row["forms_mais_adequada_share"]

    if row["fontes_presentes"] == 3 and row["amplitude_share_gh_so_forms"] <= 0.10:
        return "consistent_across_sources"
    if gh >= so and gh >= forms and gh >= best:
        return "github_strong"
    if so >= gh and so >= forms and so >= best:
        return "stackoverflow_strong"
    if forms >= gh and forms >= so:
        return "survey_strong"
    if best > forms:
        return "survey_aspirational"
    return "fragmented_presence"


def carregar_github() -> pd.DataFrame:
    """Loads GitHub frequency and popularity metrics by architecture."""
    freq = pd.read_csv(ARQ_GITHUB_FREQ).rename(
        columns={"architecture": "arquitetura", "count_repos": "github_repos"}
    )
    freq = adicionar_share_rank(freq, "github_repos", "github")

    pop = pd.read_csv(ARQ_GITHUB_POP).rename(columns={"arch": "arquitetura"})
    return freq.merge(pop, on="arquitetura", how="left")


def carregar_stackoverflow() -> pd.DataFrame:
    """Loads Stack Overflow frequency, average score, and sentiment metrics."""
    freq = pd.read_csv(ARQ_SO_FREQ).rename(
        columns={
            "architecture": "arquitetura",
            "count_questions": "stackoverflow_questions",
            "count_answers": "stackoverflow_answers",
            "count_total": "stackoverflow_total",
        }
    )
    freq = adicionar_share_rank(freq, "stackoverflow_total", "stackoverflow")

    score = pd.read_csv(ARQ_SO_SCORE).rename(columns={"arch": "arquitetura"})
    sent = pd.read_csv(ARQ_SO_SENT).rename(
        columns={
            "arch": "arquitetura",
            "positivo": "so_sent_positivo",
            "neutro": "so_sent_neutro",
            "negativo": "so_sent_negativo",
            "positive": "so_sent_positivo",
            "neutral": "so_sent_neutro",
            "negative": "so_sent_negativo",
            "total": "so_sent_total",
        }
    )
    total = sent[["so_sent_positivo", "so_sent_neutro", "so_sent_negativo"]].sum(axis=1)
    sent["so_sent_pos_share"] = sent["so_sent_positivo"] / total
    sent["so_sent_neu_share"] = sent["so_sent_neutro"] / total
    sent["so_sent_neg_share"] = sent["so_sent_negativo"] / total
    sent["so_sentimento_predominante"] = sent[
        ["so_sent_positivo", "so_sent_neutro", "so_sent_negativo"]
    ].idxmax(axis=1)
    sent["so_sentimento_predominante"] = sent["so_sentimento_predominante"].str.replace(
        "so_sent_", "", regex=False
    )
    sent["so_sentimento_predominante"] = sent["so_sentimento_predominante"].replace(
        {"positivo": "positive", "neutro": "neutral", "negativo": "negative"}
    )

    return freq.merge(score, on="arquitetura", how="left").merge(sent, on="arquitetura", how="left")


def carregar_forms() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads survey metrics and calculates share and ranking."""
    used = pd.read_csv(ARQ_FORMS_USED).rename(
        columns={"architecture": "arquitetura", "quantidade": "forms_ja_utilizou"}
    )
    main = pd.read_csv(ARQ_FORMS_MAIN).rename(
        columns={"architecture": "arquitetura", "quantidade": "forms_principal"}
    )
    best = pd.read_csv(ARQ_FORMS_BEST).rename(
        columns={"architecture": "arquitetura", "quantidade": "forms_mais_adequada"}
    )

    for df, count_col, prefix in [
        (used, "forms_ja_utilizou", "forms_ja_utilizou"),
        (main, "forms_principal", "forms_principal"),
        (best, "forms_mais_adequada", "forms_mais_adequada"),
    ]:
        adicionar_share_rank(df, count_col, prefix)

    return used, main, best


def consolidar() -> pd.DataFrame:
    """Integrates GitHub, Stack Overflow, and survey data into one comparison table."""
    github = carregar_github()
    stackoverflow = carregar_stackoverflow()
    forms_used, forms_main, forms_best = carregar_forms()

    base = github.merge(stackoverflow, on="arquitetura", how="outer")
    base = base.merge(forms_used, on="arquitetura", how="outer")
    base = base.merge(forms_main, on="arquitetura", how="outer")
    base = base.merge(forms_best, on="arquitetura", how="outer")

    numeric_cols = base.select_dtypes(include=["number"]).columns
    base[numeric_cols] = base[numeric_cols].fillna(0)

    base["presente_no_github"] = base["github_repos"] > 0
    base["presente_no_stackoverflow"] = base["stackoverflow_total"] > 0
    base["presente_no_forms_utilizada"] = base["forms_ja_utilizou"] > 0
    base["presente_no_forms_principal"] = base["forms_principal"] > 0
    base["presente_no_forms_adequada"] = base["forms_mais_adequada"] > 0
    base["forms_unificado"] = base["forms_ja_utilizou"] + base["forms_principal"]
    adicionar_share_rank(base, "forms_unificado", "forms_unificado")

    base["fontes_presentes"] = (
        base[["presente_no_github", "presente_no_stackoverflow", "presente_no_forms_utilizada"]]
        .sum(axis=1)
        .astype(int)
    )
    base["presenca_fontes"] = base.apply(descrever_fontes_presentes, axis=1)

    base["delta_share_github_vs_stackoverflow"] = (
        base["github_share"] - base["stackoverflow_share"]
    )
    base["delta_share_github_vs_forms_principal"] = (
        base["github_share"] - base["forms_principal_share"]
    )
    base["delta_share_stackoverflow_vs_forms_principal"] = (
        base["stackoverflow_share"] - base["forms_principal_share"]
    )
    base["delta_share_forms_principal_vs_adequada"] = (
        base["forms_principal_share"] - base["forms_mais_adequada_share"]
    )

    gap_cols = [
        "delta_share_github_vs_stackoverflow",
        "delta_share_github_vs_forms_principal",
        "delta_share_stackoverflow_vs_forms_principal",
    ]
    for col in gap_cols:
        base[f"gap_abs_{col.removeprefix('delta_share_')}"] = base[col].abs()

    base["indice_alinhamento_gh_so_forms"] = 1 - base[
        [f"gap_abs_{col.removeprefix('delta_share_')}" for col in gap_cols]
    ].mean(axis=1)

    share_cols = ["github_share", "stackoverflow_share", "forms_ja_utilizou_share"]
    base["media_share_gh_so_forms"] = base[share_cols].mean(axis=1)
    base["amplitude_share_gh_so_forms"] = base[share_cols].max(axis=1) - base[share_cols].min(axis=1)
    base["github_share_norm"] = normalizar_serie(base["github_share"])
    base["stackoverflow_share_norm"] = normalizar_serie(base["stackoverflow_share"])
    base["forms_ja_utilizou_share_norm"] = normalizar_serie(base["forms_ja_utilizou_share"])
    base["forms_mais_adequada_share_norm"] = normalizar_serie(base["forms_mais_adequada_share"])
    base["stars_medio_norm"] = normalizar_serie(base["stars_medio"])
    base["score_medio_total_norm"] = normalizar_serie(base["score_medio_total"])
    base["indice_multicriterio"] = (
        base["github_share_norm"] * 0.25
        + base["stackoverflow_share_norm"] * 0.25
        + base["forms_ja_utilizou_share_norm"] * 0.20
        + base["forms_mais_adequada_share_norm"] * 0.15
        + base["stars_medio_norm"] * 0.10
        + base["score_medio_total_norm"] * 0.05
    )
    base["perfil_interpretativo"] = base.apply(classificar_perfil, axis=1)

    base = base.sort_values(
        ["fontes_presentes", "indice_multicriterio", "github_repos", "stackoverflow_total"],
        ascending=[False, False, False, False],
    )
    return base


def descrever_fontes_presentes(row: pd.Series) -> str:
    """Describes in which sources an architecture appears."""
    fontes = []
    if row["presente_no_github"]:
        fontes.append("github")
    if row["presente_no_stackoverflow"]:
        fontes.append("stackoverflow")
    if row["presente_no_forms_utilizada"]:
        fontes.append("forms")
    return "+".join(fontes) if fontes else "none"


def cruzamento_rankings(base: pd.DataFrame) -> None:
    """Generates the main table with rankings, shares, and cross-source gaps."""
    cols = [
        "arquitetura",
        "github_repos",
        "github_share",
        "github_rank",
        "stackoverflow_total",
        "stackoverflow_share",
        "stackoverflow_rank",
        "forms_ja_utilizou",
        "forms_ja_utilizou_share",
        "forms_ja_utilizou_rank",
        "forms_principal",
        "forms_principal_share",
        "forms_principal_rank",
        "forms_mais_adequada",
        "forms_mais_adequada_share",
        "forms_mais_adequada_rank",
        "stars_total",
        "stars_medio",
        "forks_total",
        "forks_medio",
        "score_medio_total",
        "so_sent_pos_share",
        "so_sent_neg_share",
        "so_sentimento_predominante",
        "delta_share_github_vs_stackoverflow",
        "delta_share_github_vs_forms_principal",
        "delta_share_stackoverflow_vs_forms_principal",
        "delta_share_forms_principal_vs_adequada",
        "indice_alinhamento_gh_so_forms",
        "fontes_presentes",
        "presenca_fontes",
    ]
    salvar_csv(base[cols].copy(), "cruzamento_github_stackoverflow_forms_rankings.csv")


def cruzamento_convergencia(base: pd.DataFrame) -> None:
    """Separates architectures present in all sources and exclusive to one source."""
    todas = base[base["fontes_presentes"] == 3].copy()
    salvar_csv(todas, "cruzamento_github_stackoverflow_forms_todas_fontes.csv")

    so_github = base[
        base["presente_no_github"]
        & ~base["presente_no_stackoverflow"]
        & ~base["presente_no_forms_utilizada"]
    ].copy()
    salvar_csv(so_github, "cruzamento_github_stackoverflow_forms_so_github.csv")

    so_stackoverflow = base[
        ~base["presente_no_github"]
        & base["presente_no_stackoverflow"]
        & ~base["presente_no_forms_utilizada"]
    ].copy()
    salvar_csv(so_stackoverflow, "cruzamento_github_stackoverflow_forms_so_stackoverflow.csv")

    so_forms = base[
        ~base["presente_no_github"]
        & ~base["presente_no_stackoverflow"]
        & base["presente_no_forms_utilizada"]
    ].copy()
    salvar_csv(so_forms, "cruzamento_github_stackoverflow_forms_so_forms.csv")


def cruzamento_resumo(base: pd.DataFrame) -> None:
    """Creates an executive summary of the main quantitative findings."""
    rows = []

    if not base.empty:
        indicadores = [
            ("most_present_on_github", "github_repos"),
            ("most_discussed_on_stackoverflow", "stackoverflow_total"),
            ("most_used_in_survey", "forms_ja_utilizou"),
            ("main_architecture_in_survey", "forms_principal"),
            ("most_suitable_in_survey", "forms_mais_adequada"),
            ("highest_alignment_gh_so_survey", "indice_alinhamento_gh_so_forms"),
            ("highest_average_stackoverflow_score", "score_medio_total"),
            ("highest_average_github_stars", "stars_medio"),
        ]
        for indicador, col in indicadores:
            row = base.sort_values(col, ascending=False).iloc[0]
            rows.append(
                {
                    "indicador": indicador,
                    "arquitetura": row["arquitetura"],
                    "valor": round(float(row[col]), 4),
                }
            )

    salvar_csv(pd.DataFrame(rows), "cruzamento_github_stackoverflow_forms_resumo.csv")


def tabela_artigo_resumo(base: pd.DataFrame) -> None:
    """Generates a short, rounded, article-ready summary table."""
    cols = [
        "arquitetura",
        "github_repos",
        "github_share",
        "stackoverflow_total",
        "stackoverflow_share",
        "forms_ja_utilizou",
        "forms_ja_utilizou_share",
        "forms_principal",
        "forms_principal_share",
        "forms_mais_adequada",
        "forms_mais_adequada_share",
        "stars_medio",
        "score_medio_total",
        "indice_multicriterio",
        "perfil_interpretativo",
    ]
    tabela = base[cols].copy().sort_values("indice_multicriterio", ascending=False)
    percent_cols = [col for col in tabela.columns if col.endswith("_share")]
    for col in percent_cols:
        tabela[col] = (tabela[col] * 100).round(2)
    tabela["stars_medio"] = tabela["stars_medio"].round(2)
    tabela["score_medio_total"] = tabela["score_medio_total"].round(2)
    tabela["indice_multicriterio"] = tabela["indice_multicriterio"].round(4)
    salvar_csv(tabela, "tabela_artigo_resumo_arquiteturas.csv")


def matriz_presenca_fontes(base: pd.DataFrame) -> None:
    """Generates a binary source-presence matrix for quick reading."""
    matriz = base[
        [
            "arquitetura",
            "presente_no_github",
            "presente_no_stackoverflow",
            "presente_no_forms_utilizada",
            "presente_no_forms_principal",
            "presente_no_forms_adequada",
            "fontes_presentes",
            "presenca_fontes",
        ]
    ].copy()
    bool_cols = [col for col in matriz.columns if col.startswith("presente_")]
    matriz[bool_cols] = matriz[bool_cols].astype(int)
    matriz = matriz.sort_values(["fontes_presentes", "arquitetura"], ascending=[False, True])
    salvar_csv(matriz, "matriz_presenca_fontes_github_stackoverflow_forms.csv")


def ranking_multicriterio(base: pd.DataFrame) -> None:
    """Generates a composite ranking with normalized indicators."""
    cols = [
        "arquitetura",
        "indice_multicriterio",
        "github_share_norm",
        "stackoverflow_share_norm",
        "forms_ja_utilizou_share_norm",
        "forms_mais_adequada_share_norm",
        "stars_medio_norm",
        "score_medio_total_norm",
        "perfil_interpretativo",
    ]
    ranking = base[cols].copy().sort_values("indice_multicriterio", ascending=False)
    numeric_cols = ranking.select_dtypes(include=["number"]).columns
    ranking[numeric_cols] = ranking[numeric_cols].round(4)
    ranking["ranking_multicriterio"] = range(1, len(ranking) + 1)
    salvar_csv(ranking, "ranking_multicriterio_arquiteturas.csv")


def perfis_interpretativos(base: pd.DataFrame) -> None:
    """Summarizes how many architectures fall into each interpretive profile."""
    resumo = (
        base.groupby("perfil_interpretativo")
        .agg(
            arquiteturas=("arquitetura", lambda values: ", ".join(sorted(values))),
            quantidade=("arquitetura", "count"),
            media_github_share=("github_share", "mean"),
            media_stackoverflow_share=("stackoverflow_share", "mean"),
            media_forms_uso_share=("forms_ja_utilizou_share", "mean"),
            media_indice_multicriterio=("indice_multicriterio", "mean"),
        )
        .reset_index()
        .sort_values("quantidade", ascending=False)
    )
    numeric_cols = resumo.select_dtypes(include=["number"]).columns
    resumo[numeric_cols] = resumo[numeric_cols].round(4)
    salvar_csv(resumo, "perfis_interpretativos_arquiteturas.csv")


def matriz_correlacao_indicadores(base: pd.DataFrame) -> None:
    """Calculates simple correlations among the main quantitative indicators."""
    cols = [
        "github_share",
        "stackoverflow_share",
        "forms_ja_utilizou_share",
        "forms_principal_share",
        "forms_mais_adequada_share",
        "stars_medio",
        "score_medio_total",
        "so_sent_pos_share",
    ]
    corr = base[cols].corr().round(4).reset_index().rename(columns={"index": "indicador"})
    salvar_csv(corr, "matriz_correlacao_indicadores.csv")


def grafico_participacao_relativa(base: pd.DataFrame) -> None:
    """Compares relative share across sources using grouped bars."""
    top = base.sort_values("fontes_presentes", ascending=False).head(10)
    plot_df = top[
        [
            "arquitetura",
            "github_share",
            "stackoverflow_share",
            "forms_unificado_share",
            "forms_mais_adequada_share",
        ]
    ].set_index("arquitetura")
    plot_df = plot_df.rename(
        columns={
            "github_share": "GitHub repositories",
            "stackoverflow_share": "Stack Overflow Q&A",
            "forms_unificado_share": "Survey (experienced)",
            "forms_mais_adequada_share": "Survey (suitable)",
        }
    )

    ax = plot_df.plot(kind="bar", figsize=(13, 6))
    ax.set_xlabel("Architecture")
    ax.set_ylabel("Cross-source participation")
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    plt.xticks(rotation=30, ha="right")
    ax.legend(title="Source", loc="upper right", frameon=True, framealpha=0.95)
    salvar_plot("grafico_cruzamento_github_stackoverflow_forms_participacao.png")


def grafico_gap_github_stackoverflow_forms(base: pd.DataFrame) -> None:
    """Shows gaps between GitHub, Stack Overflow, and the survey main architecture."""
    top = base.sort_values("github_repos", ascending=False).head(10)
    plot_df = top[
        [
            "arquitetura",
            "delta_share_github_vs_stackoverflow",
            "delta_share_github_vs_forms_principal",
            "delta_share_stackoverflow_vs_forms_principal",
        ]
    ].set_index("arquitetura")
    plot_df = plot_df.rename(
        columns={
            "delta_share_github_vs_stackoverflow": "GitHub - Stack Overflow",
            "delta_share_github_vs_forms_principal": "GitHub - Survey main",
            "delta_share_stackoverflow_vs_forms_principal": "Stack Overflow - Survey main",
        }
    )

    plot_df.plot(kind="bar", figsize=(13, 6))
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xlabel("Architecture")
    plt.ylabel("Share difference")
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
    plt.xticks(rotation=30, ha="right")
    plt.legend(title="Gap")
    salvar_plot("grafico_cruzamento_github_stackoverflow_forms_gaps.png")


def grafico_popularidade_vs_forms(base: pd.DataFrame) -> None:
    """Crosses GitHub popularity with declared survey usage."""
    plot_df = base[(base["github_repos"] > 0) | (base["forms_ja_utilizou"] > 0)].copy()

    plt.figure(figsize=(10, 6))
    plt.scatter(plot_df["stars_medio"], plot_df["forms_ja_utilizou_share"], s=80)
    for _, row in plot_df.iterrows():
        plt.annotate(row["arquitetura"], (row["stars_medio"], row["forms_ja_utilizou_share"]))
    plt.xlabel("Average GitHub stars")
    plt.ylabel("Share among architectures used in the survey")
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
    salvar_plot("grafico_cruzamento_github_stars_forms_uso.png")


def grafico_heatmap_participacao(base: pd.DataFrame) -> None:
    """Generates a heatmap of normalized share composition by source."""
    plot_df = (
        base.sort_values("indice_multicriterio", ascending=False)
        .set_index("arquitetura")[
            [
                "github_share",
                "stackoverflow_share",
                "forms_unificado_share",
                "forms_mais_adequada_share",
            ]
        ]
        .head(12)
    )
    labels = ["GitHub", "Stack Overflow", "Survey: used + main", "Survey: suitable"]
    row_totals = plot_df.sum(axis=1).replace(0, pd.NA)
    plot_df = plot_df.div(row_totals, axis=0).fillna(0)

    plt.figure(figsize=(11, 6))
    plt.imshow(plot_df.values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    plt.colorbar(label="Share composition")
    plt.xticks(range(len(labels)), labels, rotation=25, ha="right")
    plt.yticks(range(len(plot_df.index)), plot_df.index)
    for y in range(plot_df.shape[0]):
        for x in range(plot_df.shape[1]):
            plt.text(x, y, f"{plot_df.iloc[y, x] * 100:.1f}%", ha="center", va="center", fontsize=8)
    salvar_plot("grafico_heatmap_participacao_fontes.png")


def grafico_ranking_multicriterio(base: pd.DataFrame) -> None:
    """Plots the composite architecture ranking."""
    plot_df = base.sort_values("indice_multicriterio", ascending=True).tail(12)

    plt.figure(figsize=(10, 6))
    plt.barh(plot_df["arquitetura"], plot_df["indice_multicriterio"], color="#2b6cb0")
    plt.xlabel("Normalized multicriteria index")
    plt.ylabel("Architecture")
    salvar_plot("grafico_ranking_multicriterio_arquiteturas.png")


def grafico_bolhas_fontes(base: pd.DataFrame) -> None:
    """Shows GitHub, Stack Overflow, and survey usage in a bubble chart."""
    plot_df = base[
        (base["github_share"] > 0)
        | (base["stackoverflow_share"] > 0)
        | (base["forms_ja_utilizou_share"] > 0)
    ].copy()
    sizes = 1200 * plot_df["forms_ja_utilizou_share"].clip(lower=0.015) + 80

    plt.figure(figsize=(11, 6))
    plt.scatter(plot_df["github_share"], plot_df["stackoverflow_share"], s=sizes, alpha=0.65)
    offsets = [(6, 6), (6, -12), (-28, 8), (-28, -12), (10, 0), (-36, 0)]
    for idx, (_, row) in enumerate(plot_df.sort_values("github_share").iterrows()):
        plt.annotate(
            row["arquitetura"],
            (row["github_share"], row["stackoverflow_share"]),
            textcoords="offset points",
            xytext=offsets[idx % len(offsets)],
            fontsize=9,
        )
    plt.xlabel("Relative share on GitHub")
    plt.ylabel("Relative share on Stack Overflow")
    plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
    plt.grid(alpha=0.2)
    salvar_plot("grafico_bolhas_github_stackoverflow_forms.png")


def grafico_perfis_interpretativos(base: pd.DataFrame) -> None:
    """Plots an interpretable heatmap of architecture prominence by source."""
    plot_df = (
        base[
            (base["github_share"] > 0)
            | (base["stackoverflow_share"] > 0)
            | (base["forms_ja_utilizou_share"] > 0)
        ]
        .sort_values("indice_multicriterio", ascending=False)
        .head(10)
        .copy()
    )
    heatmap_df = plot_df.set_index("arquitetura")[
        [
            "github_share",
            "stackoverflow_share",
            "forms_ja_utilizou_share",
            "forms_principal_share",
            "forms_mais_adequada_share",
        ]
    ]
    labels = ["GitHub", "Stack Overflow", "Survey: used", "Survey: main", "Survey: suitable"]

    plt.figure(figsize=(9, 5))
    plt.imshow(heatmap_df.values, aspect="auto", cmap="YlGnBu")
    colorbar = plt.colorbar(label="Relative share within source")
    colorbar.ax.tick_params(labelsize=8)
    colorbar.set_label("Relative share within source", fontsize=9)
    plt.xticks(range(len(labels)), labels, rotation=25, ha="right", fontsize=9)
    plt.yticks(range(len(heatmap_df.index)), heatmap_df.index, fontsize=9)
    for y in range(heatmap_df.shape[0]):
        for x in range(heatmap_df.shape[1]):
            value = heatmap_df.iloc[y, x]
            text_color = "white" if value >= 0.35 else "#1a202c"
            plt.text(
                x,
                y,
                f"{value * 100:.1f}%",
                ha="center",
                va="center",
                fontsize=7,
                color=text_color,
            )
    plt.xlabel("Evidence source", fontsize=10)
    plt.ylabel("Architecture", fontsize=10)
    salvar_plot("grafico_perfis_interpretativos_arquiteturas.png")


def main() -> None:
    """Executa os cruzamentos entre GitHub, Stack Overflow e Forms."""
    DATA_PROCESSED_COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

    required = [
        ARQ_GITHUB_FREQ,
        ARQ_GITHUB_POP,
        ARQ_SO_FREQ,
        ARQ_SO_SCORE,
        ARQ_SO_SENT,
        ARQ_FORMS_USED,
        ARQ_FORMS_MAIN,
        ARQ_FORMS_BEST,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("ERROR: required files not found:")
        for path in missing:
            print(f"- {path}")
        return

    base = consolidar()
    salvar_csv(base, "cruzamento_github_stackoverflow_forms_consolidado.csv")
    cruzamento_rankings(base)
    cruzamento_convergencia(base)
    cruzamento_resumo(base)
    tabela_artigo_resumo(base)
    matriz_presenca_fontes(base)
    ranking_multicriterio(base)
    perfis_interpretativos(base)
    matriz_correlacao_indicadores(base)
    grafico_participacao_relativa(base)
    grafico_gap_github_stackoverflow_forms(base)
    grafico_popularidade_vs_forms(base)
    grafico_heatmap_participacao(base)
    grafico_ranking_multicriterio(base)
    grafico_bolhas_fontes(base)
    grafico_perfis_interpretativos(base)


if __name__ == "__main__":
    main()
