from __future__ import annotations
import gc
import io
import re
import unicodedata
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from src.analysis import (
    FILTER_LABELS,
    STATUS_LABELS,
    STATUS_PALETTE,
    MODEL_COLOR,
    COLOR_PRIMARY_BLUE,
    COLOR_PRIMARY_GREEN,
    COLOR_NEUTRAL_GRAY,
    COLOR_NEUTRAL_GRAY_LIGHT,
    COLOR_SECAO,
    COLOR_MEDIA,
    EVENT_COLOR,
    ESC_LABELS,
    ramp_perfil,
    tint,
)
from src.charts import apply_base_layout, donut_chart
from src.ui_components import (
    chart_card,
    section_header,
    alert_box,
    contingency_toggle_css,
    stat_tiles,
    callout,
    case_head,
    fmt_int,
    tabela_grupos,
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _fmt_min_sec(total_seconds: float) -> str:
    """Formata segundos totais em minutos e segundos (~XmYs)."""
    if pd.isna(total_seconds) or total_seconds <= 0:
        return "~0s"
    m = int(total_seconds) // 60
    s = int(total_seconds) % 60
    if m > 0:
        return f"~{m}m{s}s"
    return f"~{s}s"

def _fmt_horas_min(total_seconds: float) -> str:
    """Formata segundos totais em horas e minutos (~XhYYmin)."""
    if pd.isna(total_seconds) or total_seconds <= 0:
        return "N/D"
    total_seconds = int(total_seconds)
    h, resto = divmod(total_seconds, 3600)
    m, s = divmod(resto, 60)
    if h > 0:
        return f"~{h}h{m:02d}min"
    if m > 0:
        return f"~{m}min{s:02d}s"
    return f"~{s}s"

def _vazio(valor) -> bool:
    """Verifica se um valor vindo do dataset deve ser tratado como ausente."""
    return valor is None or (isinstance(valor, float) and pd.isna(valor)) or valor == ""

def _fmt_valor(valor, sufixo: str = "") -> str:
    """Formata um valor genérico vindo do dataset, tratando NaN/vazio como N/D."""
    if _vazio(valor):
        return "N/D"
    return f"{valor}{sufixo}"

def _spacer(altura: str = "0.6rem") -> None:
    """Espaçamento vertical consistente entre blocos."""
    st.markdown(f"<div style='height:{altura};'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Colunas de contingência
# ──────────────────────────────────────────────────────────────────────────────
_COLS_CONTINGENCIA = [
    "HOUVE_TROCA_POR_CONTINGENCIA", "EH_URNA_CONTINGENCIA",
    "CONTINGENCIA_DESDE_INICIO_VOTACAO", "OBSERVACAO_TROCA_URNA",
    "MODELO_URNA", "MODELO_URNA_PAR_CONTINGENCIA",
    "MODELO_URNA_PRINCIPAL", "MODELO_URNA_PROBLEMATICA", "URNA_ID",
    "URNA_ID_PRINCIPAL", "URNA_ID_PROBLEMATICA",
    "ULTIMO_EVENTO_URNA_PROBLEMATICA_DT", "ULTIMO_EVENTO_URNA_PROBLEMATICA_MSG",
    "INICIO_PROCEDIMENTO_CONTINGENCIA", "CONTINGENCIA_EXECUTADA_COM_SUCESSO",
    "DURACAO_PROCEDIMENTO_INTERNO_CONTINGENCIA_SEG", "URNA_PRONTA_PARA_RECEBER_VOTOS",
    "TEMPO_TOTAL_TROCA_URNA_SEG", "PAREAMENTO_SUSPEITO", "MOTIVO_PAREAMENTO_SUSPEITO",
]

# ──────────────────────────────────────────────────────────────────────────────
# Bloco de Contingência
# ──────────────────────────────────────────────────────────────────────────────
def _render_bloco_contingencia(urna: pd.Series) -> None:
    """Card com as informações de troca de urna por contingência."""
    houve_troca = bool(urna.get("HOUVE_TROCA_POR_CONTINGENCIA", False))
    eh_conting = bool(urna.get("EH_URNA_CONTINGENCIA", False))
    if not (houve_troca or eh_conting):
        return
    
    duracao_interna = urna.get("DURACAO_PROCEDIMENTO_INTERNO_CONTINGENCIA_SEG", 0)
    tempo_total_troca = urna.get("TEMPO_TOTAL_TROCA_URNA_SEG", 0)
    suspeito = bool(urna.get("PAREAMENTO_SUSPEITO", False))
    desde_inicio = bool(urna.get("CONTINGENCIA_DESDE_INICIO_VOTACAO", False))
    
    modelo_contingencia = urna.get("MODELO_URNA_PRINCIPAL")
    if _vazio(modelo_contingencia):
        modelo_contingencia = urna.get("MODELO_URNA")
    if _vazio(modelo_contingencia):
        modelo_contingencia = urna.get("MODELO_URNA_PAR_CONTINGENCIA")
    modelo_problematica = urna.get("MODELO_URNA_PROBLEMATICA")
    
    aviso_suspeito = ""
    if desde_inicio:
        observacao = urna.get(
            "OBSERVACAO_TROCA_URNA",
            "Urna de contingência já estava em operação desde o início da "
            "votação: não há intervalo de troca a ser medido.",
        )
        aviso_suspeito = (
            f'<div style="margin-top:0.75rem;padding:0.6rem 1rem;background:#E9EEF9;'
            f'border-left:3px solid {COLOR_PRIMARY_BLUE};border-radius:0 6px 6px 0;font-size:0.82rem;'
            f'color:#183247;">'
            f'<b>Contingência desde o início da votação:</b> {_fmt_valor(observacao)}</div>'
        )
    elif suspeito:
        motivo = urna.get("MOTIVO_PAREAMENTO_SUSPEITO", "")
        aviso_suspeito = (
            f'<div style="margin-top:0.75rem;padding:0.6rem 1rem;background:#FDF1F1;'
            f'border-left:3px solid #C62828;border-radius:0 6px 6px 0;font-size:0.82rem;'
            f'color:#7F1D1D;">'
            f'<b>Pareamento suspeito:</b> {motivo}</div>'
        )
    
    label_urna_problematica = "Urna original (sem atividade)" if desde_inicio else "Urna problemática"
    label_modelo_problematica = "Modelo (urna original)" if desde_inicio else "Modelo (urna problemática)"
    label_ultimo_evento = "Último evento (urna original)" if desde_inicio else "Último evento"
    label_msg_evento = "Mensagem do último evento (urna original)" if desde_inicio else "Mensagem do último evento"
    
    if desde_inicio:
        tempo_troca_exibido = "Não se aplica"
        tempo_troca_titulo = "Contingência ativa desde o início"
    else:
        tempo_troca_exibido = _fmt_horas_min(tempo_total_troca)
        tempo_troca_titulo = "Tempo total de troca"
    
    _campo = (
        lambda rotulo, valor: (
            f'<div style="background:var(--color-surface-2,#EEF1F6);padding:0.5rem 0.7rem;'
            f'border-radius:6px;">'
            f'<div style="font-size:0.65rem;color:#7A5C00;text-transform:uppercase;'
            f'letter-spacing:0.05em;font-weight:700;">{rotulo}</div>'
            f'<div style="font-weight:600;color:#3D2F00;">{valor}</div></div>'
        )
    )
    
    st.markdown(f"""
        <div style="
            background:#FFFDF2;
            border:1px solid #E6CE63;
            border-left:3px solid #E2B400;
            border-radius:var(--radius-card,8px);
            padding:0.9rem 1.1rem;
            margin-bottom:1rem;
        ">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.7rem;">
                <span style="font-size:0.9rem;font-weight:700;color:#6B5200;">
                    ↻ Troca de Urna por Contingência
                </span>
                <span style="font-size:0.72rem;color:#7A5C00;">
                    Procedimento de emergência realizado na seção
                </span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
                        gap:0.7rem 1.4rem;font-size:0.84rem;color:#6B5200;">
                {_campo("Modelo (contingência)", _fmt_valor(modelo_contingencia))}
                {_campo(label_modelo_problematica, _fmt_valor(modelo_problematica))}
                {_campo("Urna principal", _fmt_valor(urna.get("URNA_ID_PRINCIPAL")))}
                {_campo(label_urna_problematica, _fmt_valor(urna.get("URNA_ID_PROBLEMATICA")))}
                {_campo(label_ultimo_evento, _fmt_valor(urna.get("ULTIMO_EVENTO_URNA_PROBLEMATICA_DT")))}
                {_campo("Início do procedimento", _fmt_valor(urna.get("INICIO_PROCEDIMENTO_CONTINGENCIA")))}
                {_campo("Contingência concluída", _fmt_valor(urna.get("CONTINGENCIA_EXECUTADA_COM_SUCESSO")))}
                {_campo("Urna pronta p/ votos", _fmt_valor(urna.get("URNA_PRONTA_PARA_RECEBER_VOTOS")))}
                {_campo("Duração interna", _fmt_horas_min(duracao_interna))}
            </div>
            <div style="margin-top:0.7rem;padding:0.5rem 0.7rem;background:var(--color-surface-2,#EEF1F6);border-radius:6px;">
                <div style="font-size:0.65rem;color:#7A5C00;text-transform:uppercase;letter-spacing:0.05em;font-weight:700;">{label_msg_evento}</div>
                <div style="font-weight:500;color:#3D2F00;font-size:0.8rem;">{_fmt_valor(urna.get("ULTIMO_EVENTO_URNA_PROBLEMATICA_MSG"))}</div>
            </div>
            <div style="margin-top:0.7rem;display:flex;gap:1rem;">
                <div style="flex:1;background:var(--color-surface-2,#EEF1F6);padding:0.5rem 0.7rem;border-radius:6px;text-align:center;">
                    <div style="font-size:0.65rem;color:#7A5C00;text-transform:uppercase;letter-spacing:0.05em;font-weight:700;">{tempo_troca_titulo}</div>
                    <div style="font-weight:800;color:#3D2F00;font-size:1.1rem;">{tempo_troca_exibido}</div>
                </div>
            </div>
            {aviso_suspeito}
        </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Filtro de Contingência
# ──────────────────────────────────────────────────────────────────────────────
def _render_filtro_contingencia(df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza o filtro de urnas de contingência."""
    tem_col_conting = (
        "HOUVE_TROCA_POR_CONTINGENCIA" in df.columns
        or "EH_URNA_CONTINGENCIA" in df.columns
    )
    if not tem_col_conting:
        return df
    
    mask_total = pd.Series(False, index=df.index)
    if "HOUVE_TROCA_POR_CONTINGENCIA" in df.columns:
        mask_total |= df["HOUVE_TROCA_POR_CONTINGENCIA"].fillna(False).astype(bool)
    if "EH_URNA_CONTINGENCIA" in df.columns:
        mask_total |= df["EH_URNA_CONTINGENCIA"].fillna(False).astype(bool)
    
    qtd_conting_total = int(mask_total.sum())
    ativo = st.session_state.get("_chk_filtro_contingencia", False)
    
    st.markdown(contingency_toggle_css("filtro_conting"), unsafe_allow_html=True)
    
    col_grupo, _col_spacer = st.columns([2.75, 7.25])
    with col_grupo:
        with st.container(key="filtro_conting"):
            ativo = st.checkbox(
                f"Mostrar apenas urnas de contingência ({qtd_conting_total})",
                value=ativo,
                key="_chk_filtro_contingencia",
                disabled=(qtd_conting_total == 0 and not ativo),
                help=(
                    "Urnas de contingência são seções onde houve troca de equipamento "
                    "em campo — um evento operacionalmente crítico. Marque para isolar "
                    "apenas essas seções."
                ),
            )
    
    if not ativo:
        return df
    
    df_filtrado = df[mask_total].copy()
    if df_filtrado.empty:
        st.markdown(
            alert_box(
                "<b>Nenhuma urna de contingência encontrada</b> no filtro atual. "
                "As seções selecionadas não passaram por procedimento de troca de urna. "
                "Desative este filtro para visualizar todas as seções.",
                alert_type="warning",
            ),
            unsafe_allow_html=True,
        )
    
    return df_filtrado

# ──────────────────────────────────────────────────────────────────────────────
# Renderização da aba
# ──────────────────────────────────────────────────────────────────────────────
def render_tab_criticidade(
    df_secoes: pd.DataFrame | None,
    status_filter,
    estado_means: dict | None = None,
    estado_totais: dict | None = None,
) -> None:
    """Renderiza o conteúdo completo da aba 'Análise por Criticidade'."""
    if df_secoes is None or df_secoes.empty:
        st.error("Dados de seções não disponíveis para este filtro.")
        return
    
    df_secoes = _render_filtro_contingencia(df_secoes)
    if df_secoes.empty:
        return
    
    tab_analise, tab_secao = st.tabs(["Análise por nível de atraso", "Estudo de seção"])
    
    with tab_analise:
        if status_filter is None or status_filter == "Todas" or isinstance(status_filter, str):
            _render_visao_geral(df_secoes)
        elif status_filter in [0, 1, 2, 3, 4]:
            _render_detalhamento_nivel(df_secoes, status_filter, estado_means or {})
        else:
            _render_visao_geral(df_secoes)
    
    with tab_secao:
        _render_estudo_caso_secao(df_secoes, status_filter, estado_totais or {})

# ──────────────────────────────────────────────────────────────────────────────
# Visão 1 — Comparação entre todos os níveis
# ──────────────────────────────────────────────────────────────────────────────
def _render_visao_geral(df: pd.DataFrame) -> None:
    st.markdown(
        section_header(
            "Visão por Nível de Atraso",
            "Métricas operacionais comparadas entre todos os níveis de atraso.",
        ),
        unsafe_allow_html=True,
    )
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if "TIMEOUT_BIOMETRIA" not in df.columns:
            st.info("Coluna TIMEOUT_BIOMETRIA não disponível.")
        else:
            m_timeout = df.groupby("STATUS")["TIMEOUT_BIOMETRIA"].mean().dropna()
            if m_timeout.empty:
                st.info("Nenhum dado de timeout disponível para os status selecionados.")
            else:
                if "TPBSEC" in df.columns:
                    m_tempo = df.groupby("STATUS")["TPBSEC"].mean().dropna()
                    m_tempo = m_tempo.reindex(m_timeout.index)
                    text_timeout = [
                        f"{v:.1f} ocorr. {_fmt_min_sec(t)}"
                        for v, t in zip(m_timeout.values, m_tempo.values)
                    ]
                    del m_tempo
                else:
                    text_timeout = [f"{v:.1f} ocorr." for v in m_timeout.values]
                
                y_labels = [STATUS_LABELS.get(int(s), f"Nível {int(s)}") for s in m_timeout.index]
                
                with chart_card(
                    "Média de Timeout de Biometria",
                    "Número médio de timeouts e o tempo médio perdido com isso, por nível.",
                    "Compara o número médio de timeouts de biometria e o tempo "
                    "médio perdido com isso em cada nível de atraso.",
                ):
                    fig = go.Figure(go.Bar(
                        x=m_timeout.values,
                        y=y_labels,
                        orientation="h",
                        marker_color=[STATUS_PALETTE.get(int(v), COLOR_NEUTRAL_GRAY) for v in m_timeout.index],
                        text=text_timeout,
                        textposition="outside",
                    ))
                    fig = apply_base_layout(fig, height=360)
                    fig.update_layout(
                        yaxis=dict(
                            type="category",
                            tickfont=dict(color="#1B2D38", size=13),
                            categoryorder="total ascending",
                            automargin=True,
                        ),
                        xaxis=dict(automargin=True),
                    )
                    st.plotly_chart(fig, width='stretch')
                    del m_timeout, fig
    
    with col_v2:
        if "INATIVIDADE" not in df.columns:
            st.info("Coluna INATIVIDADE não disponível.")
        else:
            m_inat = df.groupby("STATUS")["INATIVIDADE"].mean().dropna()
            if m_inat.empty:
                st.info("Nenhum dado de inatividade disponível para os status selecionados.")
            else:
                if "TTPISEC" in df.columns:
                    m_t_inat = df.groupby("STATUS")["TTPISEC"].mean().dropna()
                    m_t_inat = m_t_inat.reindex(m_inat.index)
                    text_inat = [
                        f"{v:.1f} ocorr. {_fmt_min_sec(t)}"
                        for v, t in zip(m_inat.values, m_t_inat.values)
                    ]
                    del m_t_inat
                else:
                    text_inat = [f"{v:.1f} ocorr." for v in m_inat.values]
                
                y_labels = [STATUS_LABELS.get(int(s), f"Nível {int(s)}") for s in m_inat.index]
                
                with chart_card(
                    "Média de Inatividade do Eleitor",
                    "Tempo médio de inatividade do eleitor na urna, por nível de atraso.",
                    "Compara o tempo médio de inatividade do eleitor na urna "
                    "entre os níveis de atraso.",
                ):
                    fig = go.Figure(go.Bar(
                        x=m_inat.values,
                        y=y_labels,
                        orientation="h",
                        marker_color=[STATUS_PALETTE.get(int(v), COLOR_NEUTRAL_GRAY) for v in m_inat.index],
                        text=text_inat,
                        textposition="outside",
                    ))
                    fig = apply_base_layout(fig, height=360)
                    fig.update_layout(
                        yaxis=dict(
                            type="category",
                            tickfont=dict(color="#1B2D38", size=13),
                            categoryorder="total ascending",
                            automargin=True,
                        ),
                        xaxis=dict(automargin=True),
                    )
                    st.plotly_chart(fig, width='stretch')
                    del m_inat, fig
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if "QTD_PCD" not in df.columns:
            st.info("Coluna QTD_PCD não disponível.")
        else:
            pcd_sum = df.groupby("STATUS")["QTD_PCD"].sum().dropna()
            if pcd_sum.empty:
                st.info("Nenhum dado de PCD disponível.")
            else:
                labels = [STATUS_LABELS.get(int(s), f"Nível {int(s)}") for s in pcd_sum.index]
                tons = [STATUS_PALETTE.get(int(v), COLOR_NEUTRAL_GRAY) for v in pcd_sum.index]
                
                with chart_card(
                    "Distribuição de PCDs por Nível",
                    "Como o total de eleitores com deficiência atendidos se distribui entre os níveis.",
                    "Mostra como o total de eleitores com deficiência (PCD) "
                    "atendidos se distribui entre os níveis de atraso.",
                ):
                    fig = donut_chart(
                        pd.DataFrame({
                            "Status": labels,
                            "Quantidade": pcd_sum.values,
                        }),
                        label_col="Status",
                        value_col="Quantidade",
                        color_map={lbl: tons[i] for i, lbl in enumerate(labels)},
                        height=360,
                    )
                    st.plotly_chart(fig, width='stretch')
                    del pcd_sum, fig
    
    with col_p2:
        if "TECLA_INDEVIDA" not in df.columns:
            st.info("Coluna TECLA_INDEVIDA não disponível.")
        else:
            m_teclas = df.groupby("STATUS")["TECLA_INDEVIDA"].mean().dropna()
            if m_teclas.empty:
                st.info("Nenhum dado de teclas indevidas disponível.")
            else:
                y_labels = [STATUS_LABELS.get(int(s), f"Nível {int(s)}") for s in m_teclas.index]
                
                if "TEMPO_TECLA_INDEVIDA_SEG" in df.columns:
                    m_tempo_teclas = (
                        df.groupby("STATUS")["TEMPO_TECLA_INDEVIDA_SEG"]
                        .mean()
                        .reindex(m_teclas.index)
                    )
                    text_teclas = [
                        f"{v:.2f} ocorr.<br>{_fmt_min_sec(t)}"
                        for v, t in zip(m_teclas.values, m_tempo_teclas.values)
                    ]
                    del m_tempo_teclas
                else:
                    text_teclas = [
                        f"{v:.2f} ocorr."
                        for v in m_teclas.values
                    ]
                
                with chart_card(
                    "Média de Teclas Indevidas",
                    "Média de teclas inválidas digitadas por nível de atraso.",
                    "Compara a média de teclas inválidas digitadas em cada "
                    "nível de atraso.",
                ):
                    fig = go.Figure(go.Bar(
                        x=m_teclas.values,
                        y=y_labels,
                        orientation="h",
                        marker_color=[STATUS_PALETTE.get(int(v), COLOR_NEUTRAL_GRAY) for v in m_teclas.index],
                        text=text_teclas,
                        textposition="outside",
                    ))
                    fig = apply_base_layout(fig, height=360)
                    fig.update_layout(
                        yaxis=dict(
                            type="category",
                            tickfont=dict(color="#1B2D38", size=13),
                            automargin=True,
                        ),
                        xaxis=dict(automargin=True),
                    )
                    st.plotly_chart(fig, width='stretch')
                    del m_teclas, fig
    
    gc.collect()

# ──────────────────────────────────────────────────────────────────────────────
# Visão 2 — Diagnóstico detalhado de um nível específico (0–4)
# ──────────────────────────────────────────────────────────────────────────────
def _render_detalhamento_nivel(
    df: pd.DataFrame,
    status_filter: int,
    estado_means: dict,
) -> None:
    st.markdown(
        section_header(
            "Diagnóstico Detalhado por Nível",
            f"Análise do nível {STATUS_LABELS.get(status_filter, f'Nível {status_filter}')} "
            "contra a média estadual (todas as seções críticas).",
        ),
        unsafe_allow_html=True,
    )
    
    def _get_metrics(col_ocorr: str, col_tempo: str | None = None):
        m_niv = df[col_ocorr].mean() if col_ocorr in df.columns else 0
        m_est = estado_means.get(col_ocorr, m_niv)
        delta = ((m_niv / m_est) - 1) * 100 if m_est > 0 else 0
        tempo_str = ""
        if col_tempo:
            seg = df.get(col_tempo, pd.Series([0])).mean()
            if pd.notna(seg):
                tempo_str = f"Tempo total: {_fmt_min_sec(seg)}"
        return m_niv, delta, tempo_str
    
    col_k1, col_k2, col_k3 = st.columns(3)
    
    v, d, t = _get_metrics("INATIVIDADE", "TTPISEC")
    m_est_inat = estado_means.get("INATIVIDADE", 0)
    with col_k1:
        st.metric(
            "Inatividade",
            f"{v:.1f} ocorr.",
            f"{d:+.1f}% vs Estado",
            delta_color="inverse",
            help=f"Média do Estado: {m_est_inat:.2f} ocorrências por seção.",
        )
        st.caption(t)
    
    v, d, t = _get_metrics("TIMEOUT_BIOMETRIA", "TPBSEC")
    m_est_time = estado_means.get("TIMEOUT_BIOMETRIA", 0)
    with col_k2:
        st.metric(
            "Timeout Biometria",
            f"{v:.1f} ocorr.",
            f"{d:+.1f}% vs Estado",
            delta_color="inverse",
            help=f"Média do Estado: {m_est_time:.2f} ocorrências por seção.",
        )
        st.caption(t)
    
    v, d, _ = _get_metrics("TECLA_INDEVIDA")
    m_est_tecla = estado_means.get("TECLA_INDEVIDA", 0)
    with col_k3:
        st.metric(
            "Teclas Indevidas",
            f"{v:.2f} ocorr.",
            f"{d:+.1f}% vs Estado",
            delta_color="inverse",
            help=f"Média do Estado: {m_est_tecla:.2f} ocorrências por seção.",
        )
        st.caption("Erros de digitação")
    
    _spacer("1rem")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        cols_idade = [c for c in df.columns if "IDADE_" in c and "Inválido" not in c]
        if not cols_idade:
            st.info("Dados de idade não disponíveis.")
        else:
            sums = df[cols_idade].sum()
            if sums.sum() == 0:
                st.info("Todos os valores de idade são zero.")
            else:
                with chart_card(
                    "Perfil por Faixa Etária",
                    "Eleitores de cada faixa etária que votaram nas seções deste nível.",
                    "Mostra quantos eleitores de cada faixa etária votaram nas "
                    "seções deste nível de atraso.",
                ):
                    fig = go.Figure(go.Bar(
                        x=sums.values,
                        y=[c.replace("IDADE_", "").strip() for c in sums.index],
                        orientation="h",
                        marker_color=ramp_perfil(len(sums)),
                    ))
                    fig = apply_base_layout(fig, height=400)
                    fig.update_layout(
                        yaxis=dict(
                            type="category",
                            tickfont=dict(color="#1B2D38", size=13),
                            autorange="reversed",
                            automargin=True,
                        ),
                        xaxis=dict(automargin=True),
                    )
                    st.plotly_chart(fig, width='stretch')
                    del sums, fig
    
    with col_d2:
        cols_esc = [c for c in df.columns if "ESC_" in c]
        if not cols_esc:
            st.info("Dados de escolaridade não disponíveis.")
        else:
            sums_esc = df[cols_esc].sum()
            if sums_esc.sum() == 0:
                st.info("Todos os valores de escolaridade são zero.")
            else:
                with chart_card(
                    "Perfil por Escolaridade",
                    "Distribuição de eleitores por grau de escolaridade nas seções deste nível.",
                    "Mostra a distribuição de eleitores por grau de "
                    "escolaridade nas seções deste nível de atraso.",
                ):
                    fig = go.Figure(go.Bar(
                        x=sums_esc.values,
                        y=[c.replace("ESC_", "").title() for c in sums_esc.index],
                        orientation="h",
                        marker_color=ramp_perfil(len(sums_esc)),
                    ))
                    fig = apply_base_layout(fig, height=400)
                    fig.update_layout(
                        yaxis=dict(
                            type="category",
                            tickfont=dict(color="#1B2D38", size=13),
                            autorange="reversed",
                            automargin=True,
                        ),
                        xaxis=dict(automargin=True),
                    )
                    st.plotly_chart(fig, width='stretch')
                    del sums_esc, fig
    
    _, col_pcd, _ = st.columns([1, 2, 1])
    with col_pcd:
        cols_idade_all = [c for c in df.columns if "IDADE_" in c]
        if not cols_idade_all:
            st.info("Dados de idade não disponíveis para cálculo de PCD.")
        else:
            total_votos = df[cols_idade_all].sum().sum()
            qtd_pcd = df.get("QTD_PCD", pd.Series([0])).sum()
            
            with chart_card(
                "Proporção de Eleitores PCD",
                "Parcela de eleitores com deficiência sobre o total de votantes deste nível.",
                "Mostra a proporção de eleitores PCD em relação ao total de "
                "votantes neste nível de atraso.",
            ):
                fig = donut_chart(
                    pd.DataFrame({
                        "Categoria": ["PCD", "Não PCD"],
                        "Quantidade": [qtd_pcd, total_votos - qtd_pcd],
                    }),
                    label_col="Categoria",
                    value_col="Quantidade",
                    color_map={"PCD": EVENT_COLOR["Timeout de biometria"], "Não PCD": COLOR_MEDIA},
                    height=360,
                )
                st.plotly_chart(fig, width='stretch')
                del fig, total_votos, qtd_pcd
    
    gc.collect()

# ──────────────────────────────────────────────────────────────────────────────
# Visão 3 — Estudo de caso por seção
# ──────────────────────────────────────────────────────────────────────────────
def _titulo_contexto(status_filter) -> str:
    """Rótulo amigável do filtro atual."""
    if status_filter is None:
        return "Somente críticas"
    if isinstance(status_filter, str):
        return FILTER_LABELS.get(status_filter, status_filter)
    return STATUS_LABELS.get(status_filter, f"Nível {status_filter}")

_EVENTOS = (
    ("Timeout de biometria", "TIMEOUT_BIOMETRIA", "TPBSEC"),
    ("Inatividade do eleitor", "INATIVIDADE", "TTPISEC"),
    ("Teclas indevidas", "TECLA_INDEVIDA", "TEMPO_TECLA_INDEVIDA_SEG"),
)
_TODOS = "Todos os municípios"


def _num(v):
    r = pd.to_numeric(v, errors="coerce")
    return float(r) if pd.notna(r) else float("nan")


def _tempo(v):
    return "—" if pd.isna(v) else _fmt_min_sec(v)


def _modelo_da_urna(urna):
    for c in ("modelo", "MODELO_URNA_PRINCIPAL", "MODELO_URNA", "MODELO_URNA_PAR_CONTINGENCIA"):
        v = urna.get(c)
        if not _vazio(v):
            return str(v)
    return "Não identificado"


def _mascara_contingencia(df):
    m = pd.Series(False, index=df.index)
    for c in ("HOUVE_TROCA_POR_CONTINGENCIA", "EH_URNA_CONTINGENCIA"):
        if c in df.columns:
            m |= df[c].fillna(False).astype(bool)
    return m


def _rotulos_secoes(d):
    txt = "Z " + d["NR_ZONA"].astype(str) + " · S " + d["NR_SECAO"].astype(str)
    if "ATRASO_FILA_MINUTOS" in d.columns:
        atr = pd.to_numeric(d["ATRASO_FILA_MINUTOS"], errors="coerce").round().astype("Int64").astype(str)
        txt = txt + " · " + atr.replace("<NA>", "N/D") + " min"
    return txt + _mascara_contingencia(d).map({True: " · contingência", False: ""})


def _media_por_ocorrencia(tempo, ocorr):
    return tempo / ocorr if pd.notna(tempo) and pd.notna(ocorr) and ocorr > 0 else float("nan")


def _media_filtro_por_ocorrencia(df, c_o, c_t):
    if c_o not in df.columns or c_t not in df.columns:
        return float("nan")
    return _media_por_ocorrencia(df[c_t].sum(), df[c_o].sum())


def _fmt_seg(v):
    if pd.isna(v):
        return "—"
    return f"{v:.1f}s" if v < 60 else _fmt_min_sec(v)


def _linhas_eventos(urna, df, estado=None):
    estado = estado or {}
    nan = float("nan")
    linhas = []
    for rotulo, c_o, c_t in _EVENTOS:
        o_sec = _num(urna.get(c_o))
        t_sec = _num(urna.get(c_t)) if c_t in urna.index else nan
        e = estado.get(c_o, {})
        linhas.append({
            "rotulo": rotulo,
            "o_sec": o_sec,
            "o_med": float(df[c_o].mean()) if c_o in df.columns else nan,
            "t_sec": t_sec,
            "t_med": float(df[c_t].mean()) if c_t in df.columns else nan,
            "m_sec": _media_por_ocorrencia(t_sec, o_sec),
            "m_med": _media_filtro_por_ocorrencia(df, c_o, c_t),
            "o_tot_f": float(df[c_o].sum()) if c_o in df.columns else nan,
            "t_tot_f": float(df[c_t].sum()) if c_t in df.columns else nan,
            "o_tot_e": e.get("o_tot", nan),
            "t_tot_e": e.get("t_tot", nan),
            "o_med_e": e.get("o_med", nan),
            "t_med_e": e.get("t_med", nan),
            "m_est": _media_por_ocorrencia(e.get("t_tot", nan), e.get("o_tot", nan)),
        })
    return linhas


def _resumo_secao(linhas, rank, total):
    partes = []
    if rank is not None:
        partes.append(f"É a <b>{rank}ª seção mais atrasada</b> entre as {fmt_int(total)} deste filtro.")
    validos = [l for l in linhas if pd.notna(l["t_sec"]) and l["t_sec"] > 0]
    if not validos:
        partes.append("Não há tempo de eventos operacionais registrado para esta seção.")
    else:
        top = max(validos, key=lambda l: l["t_sec"])
        txt = f"O evento que mais consumiu tempo foi <b>{top['rotulo'].lower()}</b> ({_fmt_min_sec(top['t_sec'])}"
        if pd.notna(top["t_med"]) and top["t_med"] > 0:
            txt += f", {top['t_sec'] / top['t_med']:.1f}× o tempo total médio das seções do filtro"
        partes.append(txt + ").")
    return " ".join(partes)


def _grafico_tempos(linhas):
    ev = [l for l in linhas if pd.notna(l["t_sec"])]
    if not ev:
        st.info("Tempos de eventos operacionais não disponíveis para esta seção.")
        return
    nomes = [l["rotulo"] for l in ev]
    cores = [EVENT_COLOR[n] for n in nomes]
    claras = [tint(c, 0.62) for c in cores]
    t_sec = [l["t_sec"] / 60 for l in ev]
    t_med = [(0 if pd.isna(l["t_med"]) else l["t_med"]) / 60 for l in ev]
    m_sec = [None if pd.isna(l["m_sec"]) else l["m_sec"] for l in ev]
    m_med = [None if pd.isna(l["m_med"]) else l["m_med"] for l in ev]

    fig = make_subplots(
        rows=2, cols=1, vertical_spacing=0.2, row_heights=[0.5, 0.5],
        subplot_titles=("Tempo total perdido com o evento (minutos)", "Duração média de cada ocorrência (segundos)"),
    )
    fig.add_bar(
        name="Tempo total (esta seção)", x=nomes, y=t_sec, marker_color=cores,
        text=[_fmt_min_sec(l["t_sec"]) for l in ev], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Tempo total nesta seção: %{y:.1f} min<extra></extra>", row=1, col=1,
    )
    fig.add_bar(
        name="Tempo total médio por seção (filtro)", x=nomes, y=t_med, marker_color=claras,
        text=[_tempo(l["t_med"]) for l in ev], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Tempo total médio por seção do filtro: %{y:.1f} min<extra></extra>", row=1, col=1,
    )
    fig.add_bar(
        name="Tempo médio por ocorrência (esta seção)", x=nomes, y=m_sec, marker_color=cores,
        text=[_fmt_seg(l["m_sec"]) for l in ev], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Tempo médio por ocorrência nesta seção: %{y:.1f} s<extra></extra>", row=2, col=1,
    )
    fig.add_bar(
        name="Tempo médio por ocorrência (filtro)", x=nomes, y=m_med, marker_color=claras,
        text=[_fmt_seg(l["m_med"]) for l in ev], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Tempo médio por ocorrência no filtro: %{y:.1f} s<extra></extra>", row=2, col=1,
    )
    fig = apply_base_layout(fig, height=820)
    topo = max(t_sec + t_med + [1]) * 1.25
    topo_m = max([v for v in m_sec + m_med if v is not None] + [1]) * 1.25
    eixo_x = dict(type="category", automargin=True, tickfont=dict(color="#1B2D38", size=13))
    fig.update_layout(
        barmode="group",
        margin=dict(t=50, b=50, l=60, r=20),
        xaxis=eixo_x, xaxis2=eixo_x,
        yaxis=dict(title="Minutos", range=[0, topo], automargin=True),
        yaxis2=dict(title="Segundos", range=[0, topo_m], automargin=True, showgrid=True, gridcolor="#E5ECE8"),
    )
    fig.update_annotations(font=dict(size=14, color="#174A78"))
    st.plotly_chart(fig, width="stretch")


def _tempo_longo(v):
    if pd.isna(v):
        return "—"
    return _fmt_horas_min(v) if v >= 3600 else _fmt_min_sec(v)


def _n(v):
    return "—" if pd.isna(v) else fmt_int(v)


def _med(v):
    return "—" if pd.isna(v) else f"{v:.1f}".replace(".", ",")


def _slug(txt):
    txt = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", txt.lower()).strip("_")


def _df_exportacao(linhas, urna, d_all, contexto, estado):
    """Uma linha por evento; tempos em segundos (valores brutos, sem arredondar o que não é exibição)."""
    nan = float("nan")
    st_sel = urna.get("STATUS")
    base = {
        "Município": urna.get("NM_MUNICIPIO", ""),
        "Zona": urna.get("NR_ZONA"),
        "Seção": urna.get("NR_SECAO"),
        "Modelo da urna": _modelo_da_urna(urna),
        "ID da urna": "" if _vazio(urna.get("URNA_ID")) else urna.get("URNA_ID"),
        "Urna de contingência": "Sim" if bool(_mascara_contingencia(urna.to_frame().T).iloc[0]) else "Não",
        "Nível de atraso": "" if _vazio(st_sel) else STATUS_LABELS.get(int(st_sel), f"Nível {int(st_sel)}"),
        "Atraso na fila (min)": _num(urna.get("ATRASO_FILA_MINUTOS")),
        "Filtro aplicado": contexto,
        "Seções no filtro": len(d_all),
        "Seções no estado": estado.get("n_secoes", nan),
    }
    linhas_out = []
    for l in linhas:
        linhas_out.append({
            **base,
            "Evento": l["rotulo"],
            "Seção · nº de ocorrências": l["o_sec"],
            "Seção · tempo total (s)": l["t_sec"],
            "Seção · tempo médio por ocorrência (s)": l["m_sec"],
            "Filtro · total de ocorrências": l["o_tot_f"],
            "Filtro · tempo total (s)": l["t_tot_f"],
            "Filtro · ocorrências médias por seção": l["o_med"],
            "Filtro · tempo total médio por seção (s)": l["t_med"],
            "Filtro · tempo médio por ocorrência (s)": l["m_med"],
            "Estado · total de ocorrências": l["o_tot_e"],
            "Estado · tempo gasto total (s)": l["t_tot_e"],
            "Estado · tempo médio por ocorrência (s)": l["m_est"],
            "Estado · ocorrências médias por seção": l["o_med_e"],
            "Estado · tempo total médio por seção (s)": l["t_med_e"],
        })
    return pd.DataFrame(linhas_out).round(2)


def _xlsx_bytes(df):
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Estudo de seção")
            ws = w.sheets["Estudo de seção"]
            ws.freeze_panes = "A2"
            for col in ws.columns:
                larg = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(larg + 2, 48)
        return buf.getvalue()
    except Exception:
        return None


def _render_tabela_eventos(linhas, urna, d_all, contexto, idx, estado):
    tem_estado = bool(estado.get("n_secoes"))
    grupos = [
        {"titulo": "Esta seção", "cor": COLOR_SECAO, "destaque": True,
         "colunas": ["Ocorrências", "Tempo total", "Tempo médio por ocorrência"]},
        {"titulo": f"Filtro · média de {fmt_int(len(d_all))} seções", "cor": COLOR_NEUTRAL_GRAY,
         "colunas": ["Ocorrências médias por seção", "Tempo total médio por seção", "Tempo médio por ocorrência"]},
    ]
    if tem_estado:
        grupos.append({
            "titulo": f"Estado · {fmt_int(estado['n_secoes'])} seções", "cor": COLOR_PRIMARY_GREEN,
            "colunas": ["Total de ocorrências", "Tempo gasto (total)", "Tempo médio por ocorrência"],
        })
    linhas_tab = []
    for l in linhas:
        cel = [_n(l["o_sec"]), _tempo(l["t_sec"]), _fmt_seg(l["m_sec"]),
               _med(l["o_med"]), _tempo(l["t_med"]), _fmt_seg(l["m_med"])]
        if tem_estado:
            cel += [_n(l["o_tot_e"]), _tempo_longo(l["t_tot_e"]), _fmt_seg(l["m_est"])]
        linhas_tab.append({"rotulo": l["rotulo"], "cor": EVENT_COLOR[l["rotulo"]], "celulas": cel})
    st.markdown(tabela_grupos(grupos, linhas_tab), unsafe_allow_html=True)

    df_exp = _df_exportacao(linhas, urna, d_all, contexto, estado)
    nome = f"estudo_secao_{_slug(urna.get('NM_MUNICIPIO', ''))}_z{urna['NR_ZONA']}_s{urna['NR_SECAO']}"
    chave = f"{contexto}_{idx}"
    st.markdown('<div class="dt-export-label">Exportar tabela</div>', unsafe_allow_html=True)
    c_csv, c_xlsx, _ = st.columns([1.1, 1.1, 5])
    with c_csv:
        st.download_button(
            "CSV", data=df_exp.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
            file_name=f"{nome}.csv", mime="text/csv", key=f"_dl_csv_{chave}",
            icon=":material/download:", on_click="ignore", width="stretch",
        )
    xlsx = _xlsx_bytes(df_exp)
    if xlsx is not None:
        with c_xlsx:
            st.download_button(
                "Excel", data=xlsx, file_name=f"{nome}.xlsx", key=f"_dl_xlsx_{chave}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                icon=":material/download:", on_click="ignore", width="stretch",
            )

    ex = next((l for l in linhas if pd.notna(l["m_sec"])), None)
    exemplo = ""
    if ex is not None:
        exemplo = (
            f" Exemplo nesta seção: {ex['rotulo'].lower()} ocorreu {fmt_int(ex['o_sec'])} vez(es), "
            f"somando {_fmt_min_sec(ex['t_sec'])}; {_fmt_min_sec(ex['t_sec'])} ÷ {fmt_int(ex['o_sec'])} "
            f"= {_fmt_seg(ex['m_sec'])} por ocorrência."
        )
    st.caption(
        "**Como ler.** *Esta seção* = números desta seção. *Filtro* = médias entre as seções do filtro atual. "
        "*Estado* = soma de todas as seções do ano (mesma base do total no cabeçalho): total de ocorrências, tempo gasto e tempo médio por ocorrência. "
        "**Tempo médio por ocorrência** = tempo total ÷ nº de ocorrências; no filtro e no estado divide o tempo somado pelas ocorrências somadas (não é média de médias). "
        "\"—\" = evento sem ocorrência ou sem dado. A exportação traz também os totais do filtro e as médias por seção do estado, com tempos em segundos."
        + exemplo
    )


def _grafico_perfil(urna, df, cols, rotulos):
    v_sec = pd.to_numeric(urna[cols], errors="coerce").fillna(0).astype(float)
    v_med = df[cols].sum().astype(float)
    p_sec = v_sec / v_sec.sum() * 100 if v_sec.sum() > 0 else v_sec
    p_med = v_med / v_med.sum() * 100 if v_med.sum() > 0 else v_med
    fig = go.Figure()
    fig.add_bar(
        name="Esta seção", x=rotulos, y=p_sec.values, marker_color=COLOR_SECAO,
        text=[f"{v:.1f}%" for v in p_sec.values], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Esta seção: %{y:.1f}%<extra></extra>",
    )
    fig.add_bar(
        name="Média do filtro", x=rotulos, y=p_med.values, marker_color=COLOR_MEDIA,
        text=[f"{v:.1f}%" for v in p_med.values], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Média do filtro: %{y:.1f}%<extra></extra>",
    )
    fig = apply_base_layout(fig, height=430)
    fig.update_layout(
        barmode="group", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
        xaxis=dict(type="category", automargin=True, tickfont=dict(color="#1B2D38", size=13)),
        yaxis=dict(ticksuffix="%", range=[0, max(list(p_sec.values) + list(p_med.values) + [1]) * 1.25], automargin=True),
        margin=dict(t=50, b=50, l=50, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def _render_estudo_caso_secao(df, status_filter=None, estado=None):
    estado = estado or {}
    contexto = _titulo_contexto(status_filter)

    st.markdown(
        section_header(
            f"Estudo de seção · {contexto}",
            "Escolha um município e uma seção para ver o que aconteceu ali, sempre comparado à média das seções do filtro atual.",
        ),
        unsafe_allow_html=True,
    )
    if df.empty:
        st.info(f'Não há seções em "{contexto}" neste cenário.')
        return

    d_all = df
    if "ATRASO_FILA_MINUTOS" in d_all.columns:
        d_all = d_all.sort_values("ATRASO_FILA_MINUTOS", ascending=False)
    d_all = d_all.reset_index(drop=True)
    ordenado = "ATRASO_FILA_MINUTOS" in d_all.columns
    rotulos = _rotulos_secoes(d_all)

    col_m, col_s = st.columns([1, 1.6])
    with col_m:
        muni = _TODOS
        if "NM_MUNICIPIO" in d_all.columns:
            contagem = d_all["NM_MUNICIPIO"].value_counts()
            muni = st.selectbox(
                "Município",
                [_TODOS] + sorted(contagem.index),
                format_func=lambda m: m if m == _TODOS else f"{m} ({contagem[m]})",
                key=f"_sec_muni_{contexto}",
            )
    sub = d_all if muni == _TODOS else d_all[d_all["NM_MUNICIPIO"] == muni]
    with col_s:
        idx = st.selectbox(
            "Seção (da mais para a menos atrasada)" if ordenado else "Seção",
            list(sub.index),
            format_func=lambda i: rotulos[i],
            key=f"_sec_sel_{contexto}_{muni}_{len(d_all)}",
        )

    urna = d_all.loc[idx]
    rank = idx + 1 if ordenado else None
    contingencia = bool(_mascara_contingencia(d_all.loc[[idx]]).iloc[0])
    st_sel = int(urna["STATUS"]) if "STATUS" in urna.index and pd.notna(urna["STATUS"]) else 0
    cor_st = STATUS_PALETTE.get(st_sel, COLOR_NEUTRAL_GRAY)
    atraso = _num(urna.get("ATRASO_FILA_MINUTOS"))
    atraso_med = float(d_all["ATRASO_FILA_MINUTOS"].mean()) if ordenado else float("nan")

    cols_idade = [c for c in d_all.columns if c.startswith("IDADE_") and "Inválido" not in c]
    cols_esc = [c for c in d_all.columns if c.startswith("ESC_") and "Inválido" not in c]
    eleitores = float(pd.to_numeric(urna[cols_idade], errors="coerce").fillna(0).sum()) if cols_idade else float("nan")
    eleitores_med = float(d_all[cols_idade].sum(axis=1).mean()) if cols_idade else float("nan")
    pcd = _num(urna.get("QTD_PCD"))
    tempo_votacao = _num(urna.get("TEMPO_SECAO_PRIMEIRO_ULTIMO_VOTO_SEG"))

    chips = [f"Modelo <b>{_modelo_da_urna(urna)}</b>"]
    if rank is not None:
        chips.append(f"<b>#{rank}</b> de {fmt_int(len(d_all))} em atraso")
    if contingencia:
        chips.append("<b>Urna de contingência</b>")
    nome = f"{urna['NM_MUNICIPIO']} · Zona {urna['NR_ZONA']} · Seção {urna['NR_SECAO']}" if "NM_MUNICIPIO" in urna.index else f"Zona {urna['NR_ZONA']} · Seção {urna['NR_SECAO']}"
    st.markdown(
        case_head(nome, "Prontuário da seção", STATUS_LABELS.get(st_sel, f"Nível {st_sel}"), cor_st, chips),
        unsafe_allow_html=True,
    )

    st.markdown(stat_tiles([
        {"label": "Atraso na fila", "value": "N/D" if pd.isna(atraso) else f"{atraso:.0f} min", "cor": cor_st,
         "sub": "" if pd.isna(atraso_med) else f"média do filtro: {atraso_med:.0f} min"},
        {"label": "Duração da votação", "value": "N/D" if pd.isna(tempo_votacao) else _fmt_horas_min(tempo_votacao),
         "sub": f"1º voto {_fmt_valor(urna.get('PRIMEIRO_VOTO'))} · último {_fmt_valor(urna.get('ULTIMO_VOTO'))}"},
        {"label": "Eleitores na seção", "value": "N/D" if pd.isna(eleitores) else fmt_int(eleitores),
         "sub": "" if pd.isna(eleitores_med) else f"média do filtro: {fmt_int(eleitores_med)}"},
        {"label": "Eleitores PCD", "value": "N/D" if pd.isna(pcd) else fmt_int(pcd),
         "sub": f"{pcd / eleitores:.1%} dos eleitores" if pd.notna(pcd) and eleitores > 0 else ""},
    ]), unsafe_allow_html=True)

    linhas = _linhas_eventos(urna, d_all, estado)
    st.markdown(callout(_resumo_secao(linhas, rank, len(d_all))), unsafe_allow_html=True)

    _render_bloco_contingencia(urna)

    st.markdown(
        section_header("Onde o tempo foi perdido", "Tempo acumulado por tipo de evento, nesta seção e na média do filtro."),
        unsafe_allow_html=True,
    )
    with chart_card(
        "Eventos operacionais",
        "Barra colorida = esta seção; barra clara = filtro. Em cima, o tempo total perdido com cada evento; embaixo, quanto dura cada ocorrência, em média.",
        "Soma do tempo gasto em cada tipo de evento registrado na seção (timeout de biometria, "
        "inatividade do eleitor e teclas indevidas), comparada com a média das seções do filtro atual. "
        "A tabela abaixo traz o número de ocorrências, o tempo total e a média de tempo por ocorrência, "
        "contra a média do filtro (tempo total somado ÷ ocorrências somadas).",
    ):
        _grafico_tempos(linhas)
        _render_tabela_eventos(linhas, urna, d_all, contexto, idx, estado)

    st.markdown(
        section_header("Perfil dos eleitores", "Participação de cada grupo na seção, comparada à média do filtro."),
        unsafe_allow_html=True,
    )
    with chart_card(
        "Faixa etária",
        "Percentual de eleitores de cada faixa etária.",
        "Percentual de eleitores de cada faixa etária nesta seção, contra o percentual no conjunto de seções do filtro.",
    ):
        if cols_idade:
            _grafico_perfil(urna, d_all, cols_idade, [c.replace("IDADE_", "").strip() for c in cols_idade])
        else:
            st.info("Dados de idade não disponíveis.")
    _spacer("1rem")
    with chart_card(
        "Escolaridade",
        "Percentual de eleitores de cada nível de escolaridade.",
        "Percentual de eleitores de cada nível de escolaridade nesta seção, contra o percentual no conjunto de seções do filtro.",
    ):
        if cols_esc:
            _grafico_perfil(urna, d_all, cols_esc, [ESC_LABELS.get(c, c.replace("ESC_", "").title()) for c in cols_esc])
        else:
            st.info("Dados de escolaridade não disponíveis.")

    gc.collect()
