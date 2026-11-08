from __future__ import annotations
import gc
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.analysis import AGE_COLORS, ESC_COLORS, ETAPA_COLORS, MODEL_COLOR, URN_MODELS, ramp
from src.charts import (
    apply_base_layout,
    bar_chart,
    bar_chart_with_error,
    stacked_bar,
    donut_chart,
    bullet_gauge_chart,
    ink_on,
)
from src.ui_components import chart_card, metric_card_row, model_legend

CAMINHO_CONFIG_MODELOS = "data/datasets/Tabela_Configuracoes.csv"

_SHADES: dict[str, str] = MODEL_COLOR.copy()

_CAMPOS_CONFIG: list[str] = [
    "Processador", "Memoria RAM", "Memoria armazenamento interno",
    "Perimetro criptografico na CPU", "Fonte inteligente", "Teclado do TM",
    "Display do TE", "Teclado do TE", "Impressora", "Leitor biometrico", "Bateria",
]

_LABELS_CONFIG: dict[str, str] = {
    "Processador": "Processador",
    "Memoria RAM": "Memória RAM",
    "Memoria armazenamento interno": "Armazenamento",
    "Perimetro criptografico na CPU": "Perímetro criptográfico na CPU",
    "Fonte inteligente": "Fonte inteligente",
    "Teclado do TM": "Teclado do mesário",
    "Display do TE": "Display do eleitor",
    "Teclado do TE": "Teclado do eleitor",
    "Impressora": "Impressora",
    "Leitor biometrico": "Leitor biométrico",
    "Bateria": "Bateria",
}

# Altura padrão para todos os gráficos da aba de modelos
_CHART_HEIGHT = 520

@st.cache_data(show_spinner=False, ttl=3600)
def _carregar_config_modelos(caminho: str = CAMINHO_CONFIG_MODELOS) -> dict[str, list[tuple[str, str]]]:
    if not os.path.exists(caminho):
        return {}
    try:
        df_config = pd.read_csv(caminho)
    except Exception:
        return {}
    
    df_config = df_config.set_index("Modelo")
    specs: dict[str, list[tuple[str, str]]] = {}
    for modelo, row in df_config.iterrows():
        specs[str(modelo)] = [
            (_LABELS_CONFIG.get(campo, campo), row[campo])
            for campo in _CAMPOS_CONFIG
            if campo in df_config.columns and pd.notna(row.get(campo))
        ]
    return specs

def render_tab_modelo(analise) -> None:
    """Organiza os gráficos por grupo temático."""
    _render_kpi_resumo(analise)
    
    st.markdown(
        model_legend(URN_MODELS, _SHADES),
        unsafe_allow_html=True,
    )
    
    st.markdown(
        "<div class='section-intro'>Explore os indicadores por dimensão da análise.</div>",
        unsafe_allow_html=True,
    )
    
    tab_composicao, tab_operacao, tab_perfil = st.tabs([
        "Composição dos modelos", "Desempenho operacional", "Perfil do eleitorado"
    ])
    
    with tab_composicao:
        _render_distribuicao(analise)
    
    with tab_operacao:
        _render_tempos_medios(analise)
        _render_falhas_biometricas(analise)
        _render_inatividade(analise)
        _render_teclas_indevidas(analise)
    
    with tab_perfil:
        _render_escolaridade(analise)
        _render_faixa_etaria(analise)
        _render_pcd(analise)

def _render_kpi_resumo(analise) -> None:
    dist = analise.get_model_distribution()
    total_voters = sum(len(analise.voters[m]) for m in URN_MODELS)
    config_modelos = _carregar_config_modelos()
    
    metrics = []
    for i, m in enumerate(URN_MODELS):
        if dist["counts"][i] == 0:
            continue
        voters = len(analise.voters[m])
        pct_vot = (voters / total_voters * 100) if total_voters else 0
        metrics.append({
            "modelo": m,
            "cor": _SHADES.get(m, "#566B78"),
            "secoes": dist["counts"][i],
            "pct_secoes": dist["proportions"][i] * 100,
            "votantes": voters,
            "pct_votantes": pct_vot,
            "specs": config_modelos.get(m),
        })
    
    if not metrics:
        return
    
    st.markdown(metric_card_row(metrics), unsafe_allow_html=True)
    gc.collect()

def _render_distribuicao(analise) -> None:
    dist = analise.get_model_distribution()
    
    with chart_card(
        "Seções por Modelo de Urna",
        "Quantidade absoluta de seções atendidas por cada modelo; o rótulo traz também o percentual do total geral.",
        "Quantidade absoluta de seções atendidas por cada modelo de urna. "
        "O rótulo de cada barra traz também o percentual que ela representa "
        "no total geral de seções.",
    ):
        fig = bar_chart(
            [m for i, m in enumerate(URN_MODELS) if dist["counts"][i] > 0],
            [c for c in dist["counts"] if c > 0],
            text=[f"{v:,} · ({dist['proportions'][i]*100:.1f}%)"
                  for i, v in enumerate(dist["counts"]) if v > 0],
            yrange=[0, max(dist["counts"]) * 1.3 or 1],
            height=_CHART_HEIGHT,
        )
        st.plotly_chart(fig, width='stretch')
        del fig
    
    del dist
    gc.collect()

def _render_tempos_medios(analise) -> None:
    """Composição do tempo médio operacional com cores derivadas dos modelos."""
    fila = analise.get_queue_times()
    auth = analise.get_auth_duration()
    inat = analise.get_inactivity_times()
    
    totals = [f + a + ii for f, a, ii in zip(fila["means"], auth["means"], inat["means"])]
    total_geral = sum(totals)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with chart_card(
            "Composição do Tempo Médio por Eleitor",
            "Soma média (segundos) das três etapas da votação — fila, autenticação e inatividade — por modelo.",
            "Cada etapa tem cor fixa: Fila (azul), Autenticação (amarelo) e Inatividade (vinho). "
            "Passe o mouse sobre a barra para ver o valor de cada etapa.",
        ):
            etapas = (("T. Inatividade", inat), ("T. Autenticação", auth), ("T. Fila", fila))
            fig = go.Figure()
            for nome, serie in etapas:
                cor = ETAPA_COLORS[nome]
                fig.add_trace(go.Bar(
                    x=URN_MODELS, y=serie["means"], name=nome, showlegend=False, marker_color=cor,
                    text=[f"{v:.1f}s" if v > 0 else "" for v in serie["means"]],
                    textposition="inside", insidetextanchor="middle",
                    textfont=dict(color=ink_on(cor), size=12, weight="bold"),
                    hovertemplate=f"<b>%{{x}}</b><br>{nome}: %{{y:.1f}}s<extra></extra>",
                ))
            fig = apply_base_layout(fig, height=_CHART_HEIGHT)
            fig.update_layout(
                barmode="stack", showlegend=False,
                xaxis=dict(categoryorder="array", categoryarray=URN_MODELS),
                yaxis=dict(title="Tempo Médio Total (segundos)"),
                margin=dict(t=30, b=40, l=50, r=20),
            )

            st.plotly_chart(fig, width='stretch')
            del fig
    
    with col2:
        df_gauge = pd.DataFrame({
            "Modelo": URN_MODELS,
            "Tempo Total (s)": totals,
        })
        df_gauge = df_gauge[df_gauge["Tempo Total (s)"] > 0]
        
        if total_geral > 0 and not df_gauge.empty:
            df_gauge["% do Total"] = (df_gauge["Tempo Total (s)"] / total_geral * 100).round(1)
            
            with chart_card(
                "Representatividade do Tempo (%)",
                "Participação de cada modelo no tempo operacional total acumulado (todas as etapas).",
                "A barra colorida mostra, para cada modelo, o percentual que ele "
                "representa no tempo operacional total acumulado.",
            ):
                fig = bullet_gauge_chart(
                    df_gauge,
                    label_col="Modelo",
                    value_col="% do Total",
                    suffix="%",
                    color_map=_SHADES,
                    height=_CHART_HEIGHT,
                )
                st.plotly_chart(fig, width='stretch')
                del fig
        
        del df_gauge
    
    del fila, auth, inat, totals
    gc.collect()
    
def _render_falhas_biometricas(analise) -> None:
    bio = analise.get_bio_failure_rates()
    
    # 50/50 - ambos os gráficos do mesmo tamanho
    col_bio1, col_bio2 = st.columns([1, 1])
    
    with col_bio1:
        with chart_card(
            "Taxa de Falha Biométrica por Modelo",
            "Percentual de votantes com falha biométrica, entre os que tiveram biometria solicitada.",
            "Taxa de falha na leitura biométrica, calculada apenas sobre os "
            "eleitores para os quais a biometria foi solicitada.",
        ):
            fig = bar_chart(
                URN_MODELS, bio["rates"],
                text=[f"{v*100:.1f}%" for v in bio["rates"]],
                yfmt=".0%", yrange=[0, 1.0],
                height=_CHART_HEIGHT,
            )
            avg_rate = (
                sum(bio["rates"]) / len([r for r in bio["rates"] if r > 0])
                if any(r > 0 for r in bio["rates"]) else 0
            )
            fig.add_hline(
                y=avg_rate,
                line_dash="dash",
                line_color="#8794AA",
                annotation_text=f"Média geral: {avg_rate*100:.1f}%",
                annotation_position="right",
            )
            st.plotly_chart(fig, width='stretch')
            del fig
    
    with col_bio2:
        _rows = []
        total_falhas_geral = 0
        bio_cols_ausentes = False
        
        for i, m in enumerate(URN_MODELS):
            vm = analise.voters[m]
            if "bio_solicitada" not in vm.columns or "n_falhas_bio" not in vm.columns:
                bio_cols_ausentes = True
                _rows.append((m, "0", "0", 0, 0))
                del vm
                continue
            
            bio_m = vm[vm["bio_solicitada"] == True]
            n_sol = len(bio_m)
            falhas = int((bio_m["n_falhas_bio"] > 0).sum())
            total_falhas_geral += falhas
            _rows.append((m, f"{n_sol:,}", f"{falhas:,}", n_sol, falhas))
            del vm, bio_m
        
        if total_falhas_geral > 0:
            df_falhas = pd.DataFrame({
                "Modelo": [r[0] for r in _rows if r[4] > 0],
                "Falhas": [r[4] for r in _rows if r[4] > 0],
            })
            
            with chart_card(
                "Concentração das Falhas (%)",
                "Do total de falhas biométricas registradas (todos os modelos), quanto cada modelo concentra.",
                "Do total de falhas biométricas registradas, esta fatia mostra quanto cada modelo concentra.",
            ):
                fig = donut_chart(
                    df_falhas,
                    label_col="Modelo",
                    value_col="Falhas",
                    color_map=_SHADES,
                    height=_CHART_HEIGHT,
                )
                st.plotly_chart(fig, width='stretch')
                del fig, df_falhas
        
        elif bio_cols_ausentes:
            st.info(
                "Dados de biometria (solicitação/falhas) não estão disponíveis "
                "para o filtro selecionado."
            )
    
    del bio
    gc.collect()

def _render_inatividade(analise) -> None:
    inat = analise.get_inactivity_times()
    
    # 50/50 - ambos os gráficos do mesmo tamanho
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with chart_card(
            "Tempo de Inatividade (média ± DP)",
            "Média e desvio padrão do tempo de inatividade do eleitor na urna, em segundos (excluindo zeros).",
            "Barra = tempo médio de inatividade do eleitor na urna, em segundos, por modelo.",
        ):
            fig = bar_chart_with_error(
                URN_MODELS, inat["means"], inat["stds"],
                text=[f"{m:.1f}s" for m in inat["means"]],
                error_suffix="s",
                height=_CHART_HEIGHT,
            )
            st.plotly_chart(fig, width='stretch')
            del fig
    
    with col2:
        total_inat = sum(inat["means"])
        
        if total_inat > 0:
            df_inat = pd.DataFrame({
                "Modelo": [m for i, m in enumerate(URN_MODELS) if inat["means"][i] > 0],
                "% do Total": [
                    round(inat["means"][i] / total_inat * 100, 1)
                    for i in range(len(URN_MODELS)) if inat["means"][i] > 0
                ],
            })
            
            with chart_card(
                "Representatividade da Inatividade (%)",
                "Participação de cada modelo no tempo total de inatividade acumulado (soma 100%).",
                "Percentual que cada modelo contribui para o tempo total de inatividade acumulado.",
            ):
                fig = bullet_gauge_chart(
                    df_inat,
                    label_col="Modelo",
                    value_col="% do Total",
                    suffix="%",
                    color_map=_SHADES,
                    height=_CHART_HEIGHT,
                )
                st.plotly_chart(fig, width='stretch')
                del fig, df_inat
    
    del inat
    gc.collect()

def _render_teclas_indevidas(analise) -> None:
    inv_keys = analise.get_invalid_keys()
    total_kp = analise.df_log["n_teclas_inv"].sum() if "n_teclas_inv" in analise.df_log.columns else 0
    
    qtds: list[int] = []
    for m in URN_MODELS:
        vm = analise.voters[m]
        if "n_teclas_inv" not in vm.columns:
            qtds.append(0)
            del vm
            continue
        qtds.append(int(vm[vm["n_teclas_inv"] > 0]["n_teclas_inv"].sum()))
        del vm
    
    with chart_card(
        "Teclas Indevidas por Modelo",
        "Quantidade de teclas inválidas registradas por modelo e o percentual que concentra do total geral.",
        "Proporção de teclas inválidas em relação ao total de teclas digitadas nos votos registrados em cada modelo.",
    ):
        if total_kp > 0:
            fig = bar_chart(
                URN_MODELS, inv_keys["proportions"],
                text=[f"{q:,} · ({p*100:.1f}%)"
                      for q, p in zip(qtds, inv_keys["proportions"])],
                yfmt=".0%", yrange=[0, 1.0],
                height=_CHART_HEIGHT,
            )
            st.plotly_chart(fig, width='stretch')
            del fig
        elif "n_teclas_inv" not in analise.df_log.columns:
            st.info(
                "Dados de teclas indevidas não estão disponíveis para o "
                "filtro selecionado."
            )
    
    del inv_keys, total_kp, qtds
    gc.collect()

def _render_escolaridade(analise) -> None:
    edu = analise.get_education_distribution()
    low_edu = analise.get_low_education()
    
    # 50/50 - ambos os gráficos do mesmo tamanho
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with chart_card(
            "Distribuição por Escolaridade (%)",
            "Como os eleitores atendidos por cada modelo se distribuem entre os níveis de escolaridade (cada barra soma 100%). Passe o mouse sobre um trecho para ver a categoria.",
            "Cada barra soma 100% e mostra como os eleitores atendidos por cada modelo se distribuem entre os níveis de escolaridade.",
        ):
            fig = stacked_bar(
                edu["df_proportions"], edu["labels"],
                None,
                height=_CHART_HEIGHT,
                cat_colors=ESC_COLORS,
            )
            st.plotly_chart(fig, width='stretch')
            del fig
    
    with col2:
        df_low = pd.DataFrame({
            "Modelo": URN_MODELS,
            "Baixa Escolaridade (%)": [v * 100 for v in low_edu["proportions"]],
        })
        df_low = df_low[df_low["Baixa Escolaridade (%)"] > 0]
        
        if not df_low.empty:
            with chart_card(
                "Baixa Escolaridade por Modelo",
                "Proporção de eleitores com baixa escolaridade (até fundamental incompleto) por modelo.",
                "Proporção de eleitores com baixa escolaridade em relação ao total de eleitores atendidos por cada modelo.",
            ):
                fig = bar_chart(
                    df_low["Modelo"].tolist(),
                    (df_low["Baixa Escolaridade (%)"] / 100).tolist(),
                    text=[f"{v:.1f}%" for v in df_low["Baixa Escolaridade (%)"]],
                    yfmt=".0%",
                    yrange=[0, 1.0],
                    x_categoryorder=URN_MODELS,
                    height=_CHART_HEIGHT,
                    model_identity_strip=True,
                )
                st.plotly_chart(fig, width='stretch')
                del fig
        
        del df_low
    
    del edu, low_edu
    gc.collect()

def _render_faixa_etaria(analise) -> None:
    age = analise.get_age_distribution()
    elderly = analise.get_elderly_proportion()
    
    # 50/50 - ambos os gráficos do mesmo tamanho
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with chart_card(
            "Distribuição por Faixa Etária (%)",
            "Como os eleitores atendidos por cada modelo se distribuem entre as faixas etárias (cada barra soma 100%). Passe o mouse sobre um trecho para ver a categoria.",
            "Cada barra soma 100% e mostra como os eleitores atendidos por cada modelo se distribuem entre as faixas etárias.",
        ):
            fig = stacked_bar(
                age["df_proportions"], age["groups"],
                None,
                height=_CHART_HEIGHT,
                cat_colors=AGE_COLORS,
            )
            st.plotly_chart(fig, width='stretch')
            del fig
    
    with col2:
        with chart_card(
            "Eleitores Idosos (≥ 60 anos)",
            "Proporção de eleitores com 60 anos ou mais em relação ao total atendido por cada modelo.",
            "Proporção de eleitores idosos (60 anos ou mais) em relação ao total de eleitores atendidos por cada modelo.",
        ):
            fig = bar_chart(
                URN_MODELS, elderly["proportions"],
                text=[f"{v*100:.1f}%" for v in elderly["proportions"]],
                yfmt=".0%", yrange=[0, 1.0],
                x_categoryorder=URN_MODELS,
                height=_CHART_HEIGHT,
                model_identity_strip=True,
            )
            st.plotly_chart(fig, width='stretch')
            del fig
    
    del age, elderly
    gc.collect()

def _render_pcd(analise) -> None:
    pcd = analise.get_pcd_stats()
    
    # 50/50 - já estava assim, mantido
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with chart_card(
            "Total de Eleitores PCD",
            "Quantidade absoluta de eleitores com deficiência atendidos por cada modelo.",
            "Quantidade absoluta de eleitores com deficiência (PCD) atendidos por cada modelo de urna.",
        ):
            fig = bar_chart(
                URN_MODELS, pcd["totals"],
                text=[f"{v:,}" for v in pcd["totals"]],
                yrange=[0, max(pcd["totals"]) * 1.25 or 1],
                height=_CHART_HEIGHT,
                model_identity_strip=True,
            )
            st.plotly_chart(fig, width='stretch')
            del fig
    
    with col2:
        with chart_card(
            "Taxa de Eleitores PCD",
            "Percentual de eleitores com deficiência sobre o total de votantes de cada modelo.",
            "Taxa de eleitores PCD: percentual de eleitores com deficiência em relação ao total de votantes atendidos por cada modelo.",
        ):
            fig = bar_chart(
                URN_MODELS, pcd["taxas"],
                text=[f"{v*100:.2f}%" for v in pcd["taxas"]],
                yfmt=".2%", yrange=[0, max(pcd["taxas"]) * 1.3 or 1],
                height=_CHART_HEIGHT,
                model_identity_strip=True,
            )
            st.plotly_chart(fig, width='stretch')
            del fig
    
    del pcd
    gc.collect()
