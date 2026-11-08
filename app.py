import gc
import os
import streamlit as st
from src.analysis import (
    FILTER_CONTINGENCIA,
    FILTER_SOMENTE_CRITICAS,
    STATUS_OPCOES,
    UrnasCriticasAnalysis,
)
from src.data_source import (
    DATA_CONFIG,
    baixar_dados_ausentes,
    count_rows,
    load_csv,
    load_estado_means,
    nivel_key,
)
from src.tab_criticidade import render_tab_criticidade
from src.tab_geo import render_tab_geo
from src.tab_modelo import render_tab_modelo
from src.tab_sobre import render_tab_sobre
from src.theme import aplicar_tema
from src.ui_components import app_header, fmt_int

st.set_page_config(
    page_title="Urnas eletrônicas em Sergipe | UFS · TRE-SE",
    page_icon=":material/how_to_vote:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_tema()

# ── Cabeçalho (preenchido depois do carregamento) e filtros globais ─────────
slot_cabecalho = st.container()

with st.container(key="filtros_globais"):
    col_ano, col_nivel = st.columns([1, 2], gap="large")
    with col_ano:
        anos = sorted(DATA_CONFIG)
        ano = st.radio("Eleição", anos, index=len(anos) - 1, horizontal=True)
    with col_nivel:
        status_label = st.selectbox("Nível de atraso", list(STATUS_OPCOES))
    status_filter = STATUS_OPCOES[status_label]

# ── Carregamento ─────────────────────────────────────────────────────────────
erros = baixar_dados_ausentes()
if erros:
    st.error(
        "Não foi possível baixar os dados do Google Drive:\n\n"
        + "\n".join(f"- {e}" for e in erros)
        + "\n\nConfira as permissões de compartilhamento e a cota de downloads."
    )
    st.stop()

cfg = DATA_CONFIG[ano]

if status_filter == FILTER_CONTINGENCIA:
    nivel_path = modelo_path = cfg["contingencia"]
else:
    chave = nivel_key(status_filter)
    nivel_path, modelo_path = cfg["niveis"][chave], cfg["modelos_urnas"][chave]

for caminho in dict.fromkeys((nivel_path, modelo_path)):
    if not os.path.exists(caminho):
        st.error(f"Arquivo não encontrado: `{caminho}`")
        st.stop()

n_all_path = cfg["niveis"][FILTER_SOMENTE_CRITICAS]
n_0_path = cfg["niveis"][0]

with st.spinner("Carregando e organizando os dados…"):
    df_secoes = load_csv(nivel_path)
    df_voter_log = df_secoes.copy() if modelo_path == nivel_path else load_csv(modelo_path)
    total_secoes_global = sum(
        count_rows(p) for p in (n_all_path, n_0_path) if os.path.exists(p)
    )
    estado_means = load_estado_means(n_all_path) if os.path.exists(n_all_path) else {}

analise = UrnasCriticasAnalysis.from_dataframes(
    df_2022=df_voter_log,
    df_completas=df_secoes,
    status_filter=status_filter,
    prefiltered=True,
    total_secoes_override=total_secoes_global,
)

# ── Cabeçalho ────────────────────────────────────────────────────────────────
ov = analise.get_overview()
df_c = analise.df_criticas
taxa = ov["total_secoes_criticas"] / max(ov["total_secoes"], 1)
modelos = ", ".join(ov["modelos_presentes"]) or "nenhum modelo identificado"
n_mun = int(df_c["NM_MUNICIPIO"].nunique()) if "NM_MUNICIPIO" in df_c.columns else None
atraso_max = df_c["ATRASO_FILA_MINUTOS"].max() if "ATRASO_FILA_MINUTOS" in df_c.columns else None
kpis = [{"label": "Votantes nas seções", "value": fmt_int(ov["total_votantes"]), "sub": "eleitores processados"}]
if n_mun is not None:
    kpis.append({"label": "Municípios no recorte", "value": n_mun, "sub": "com ao menos uma seção"})
if atraso_max is not None and atraso_max == atraso_max:
    kpis.append({"label": "Maior atraso na fila", "value": f"{atraso_max:.0f} min", "sub": "seção mais atrasada"})
kpis.append({"label": "Modelos de urna", "value": len(ov["modelos_presentes"]), "sub": modelos})

with slot_cabecalho:
    st.markdown(
        app_header(
            {"label": "Seções no recorte", "value": fmt_int(ov["total_secoes_criticas"]), "pct": taxa,
             "sub": f"das {fmt_int(ov['total_secoes'])} seções do estado"},
            kpis[:3],
        ),
        unsafe_allow_html=True,
    )

tab_geo, tab_crit, tab_modelo, tab_sobre = st.tabs([
    ":material/map: Território",
    ":material/warning: Criticidade",
    ":material/memory: Modelos de urna",
    ":material/info: Sobre",
])

with tab_geo:
    render_tab_geo(ano, status_filter, estado_means)

with tab_crit:
    render_tab_criticidade(analise.df_criticas, status_filter, estado_means)

with tab_modelo:
    render_tab_modelo(analise)

with tab_sobre:
    render_tab_sobre()

del ov, df_c, analise, df_secoes, df_voter_log
gc.collect()

st.markdown(
    '<div class="footer">'
    'Universidade Federal de Sergipe · Tribunal Regional Eleitoral de Sergipe.<br>'
    'Desenvolvido pela <a href="https://sites.google.com/mat.ufs.br/lame/lame?authuser=0" '
    'target="_blank" rel="noopener">LAME — Liga Acadêmica de Matemática e Empresa</a>. '
    'Dados: Tribunal Superior Eleitoral (TSE).</div>',
    unsafe_allow_html=True,
)
