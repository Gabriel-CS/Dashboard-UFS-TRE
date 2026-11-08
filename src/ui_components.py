"""Componentes de UI reutilizáveis do dashboard."""
from __future__ import annotations
import html
import re
from contextlib import contextmanager
import streamlit as st

_LEADING_WS_RE = re.compile(r"\n[ \t]*")
_CARD_SEQ = 0

def _flatten(fragment: str) -> str:
    return _LEADING_WS_RE.sub("", fragment).strip()

def _tip_html(texto: str, icon: str = "ⓘ") -> str:
    return (
        '<span class="info-tip-btn">' + icon
        + '<span class="info-tip-box">' + html.escape(texto) + '</span>'
        + '</span>'
    )

@contextmanager
def chart_card(title: str, description: str = "", info: str = ""):
    global _CARD_SEQ
    _CARD_SEQ += 1
    key = f"cc{_CARD_SEQ}"
    
    # `info` é mantido na assinatura por compatibilidade, mas não é mais exibido:
    # repetia a descrição visível e o conteúdo completo está na aba Sobre.
    tip_html = ""
    desc_html = (
        f'<div class="chart-card-desc">{html.escape(description)}</div>'
        if description else ""
    )
    
    head = _flatten(f"""
        <div class="chart-card-head">
            <div class="chart-card-title">
                <span>{html.escape(title)}</span>
                {tip_html}
            </div>
            {desc_html}
        </div>
    """)
    
    with st.container(key=key):
        st.markdown(head, unsafe_allow_html=True)
        yield

def info_card(texto: str, icon: str = "ⓘ") -> None:
    st.markdown(
        '<div class="info-tip-wrap">' + _tip_html(texto, icon) + '</div>',
        unsafe_allow_html=True,
    )

def section_header(title: str, description: str = "") -> str:
    desc_html = (
        f'<div class="section-desc">{html.escape(description)}</div>'
        if description else ""
    )
    return _flatten(f"""
        <div class="section-header"><h2>{html.escape(title)}</h2></div>
        {desc_html}
    """)

def metric_card_row(metrics: list[dict]) -> str:
    """
    Cards de modelos remodelados com labels explícitos para cada métrica.
    """
    cards_html = ""
    for m in metrics:
        cor = m.get("cor") or "#174B7A"
        specs = m.get("specs")
        
        if specs:
            tooltip_lines = "<br>".join(
                f"<b>{html.escape(str(c))}:</b> {html.escape(str(v))}"
                for c, v in specs
            )
        else:
            tooltip_lines = "Configuração técnica não disponível para este modelo."
        
        name_html = _flatten(f"""
            <div class="metric-card-name-wrap" tabindex="0">
                <span class="metric-card-model" style="color:{cor};">
                    {m['modelo']}
                </span>
                <div class="metric-card-tooltip">
                    <b style="color:#fff;">{m['modelo']}</b><br>{tooltip_lines}
                </div>
            </div>
        """)
        
        cards_html += _flatten(f"""
            <div class="metric-card" style="border-top-color:{cor};">
                <div class="metric-card-header">{name_html}</div>
                <div class="metric-card-stats">
                    <div class="metric-card-stat">
                        <div class="metric-card-stat-label">Seções</div>
                        <div class="metric-card-stat-value" style="color:{cor};">
                            {m['secoes']:,}
                        </div>
                        <div class="metric-card-stat-pct">{m['pct_secoes']:.1f}% do total</div>
                    </div>
                    <div class="metric-card-stat">
                        <div class="metric-card-stat-label">Votantes</div>
                        <div class="metric-card-stat-value" style="color:{cor};">
                            {m['votantes']:,}
                        </div>
                        <div class="metric-card-stat-pct">{m['pct_votantes']:.1f}% do total</div>
                    </div>
                </div>
                <div class="metric-card-track">
                    <div class="metric-card-fill"
                         style="width:{min(m['pct_secoes'], 100):.1f}%;background:{cor};"></div>
                </div>
            </div>
        """)
    
    return f'<div class="metric-row">{cards_html}</div>'

def model_legend(models: list[str], color_map: dict[str, str]) -> str:
    items = "".join(
        f'<div class="model-legend-item">'
        f'<span class="model-legend-dot" style="background:{color_map.get(m, "#527080")};"></span>'
        f'<span>{html.escape(str(m))}</span>'
        f'</div>'
        for m in models
    )
    return f'<div class="model-legend-wrap">{items}</div>'

def kpi_strip(items: list[dict]) -> str:
    cells = "".join(
        f'<div class="kpi-cell" title="{html.escape(i.get("hint", ""))}">'
        f'<div class="kpi-label">{html.escape(i["label"])}</div>'
        f'<div class="kpi-value {(("kpi-" + i["tone"]) if i.get("tone") else "")}">'
        f'{html.escape(str(i["value"]))}</div>'
        f'</div>'
        for i in items
    )
    return f'<div class="kpi-strip">{cells}</div>'

_SUBTITULO_LEGENDA = (
    '<div style="font-size:0.72rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;'
    'color:var(--color-brand);margin:{margem} 0 4px;">{texto}</div>'
)

def _linhas_legenda(detalhes) -> str:
    return "".join(
        f'<div style="display:grid;grid-template-columns:14px 1fr;gap:10px;padding:8px 0;'
        f'border-bottom:1px solid var(--color-border);">'
        f'<div style="width:10px;height:10px;margin-top:5px;border-radius:2px;background:{d["cor"]};"></div>'
        f'<div><div style="font-size:0.88rem;font-weight:600;color:var(--color-ink);">'
        f'{html.escape(titulo)}'
        f'<span style="font-weight:400;color:var(--color-ink-soft);">  {html.escape(d["intervalo"])}</span></div>'
        f'<div style="font-size:0.8rem;color:var(--color-ink-soft);line-height:1.4;">{html.escape(d["desc"])}</div>'
        f'</div></div>'
        for titulo, d in detalhes
    )

def legenda_status(detalhes: dict[int, dict], titulo: str = "Níveis de atraso") -> str:
    itens = [(f'Nível {lvl} · {d["label"]}', d) for lvl, d in detalhes.items()]
    return (
        '<div style="min-width:300px">'
        + _SUBTITULO_LEGENDA.format(margem="0", texto=html.escape(titulo))
        + _linhas_legenda(itens) + '</div>'
    )

def legenda_filtros(detalhes: dict[str, dict], titulo: str = "Filtros agrupados") -> str:
    itens = [(d["label"], d) for d in detalhes.values()]
    return (
        '<div style="min-width:300px">'
        + _SUBTITULO_LEGENDA.format(margem="16px", texto=html.escape(titulo))
        + _linhas_legenda(itens) + '</div>'
    )

def alert_box(message: str, alert_type: str = "warning") -> str:
    styles = {
        "danger":  {"bg": "#FDF1F1", "border": "#C62828", "color": "#7F1D1D", "icon": "⚠"},
        "success": {"bg": "#EDF7F1", "border": "#0B8A47", "color": "#095F33", "icon": "✔"},
        "warning": {"bg": "#FFF9E0", "border": "#E2B400", "color": "#6B5200", "icon": "⚠"},
        "info":    {"bg": "#E9EEF9", "border": "#174A78", "color": "#183247", "icon": "ℹ"},
    }
    s = styles.get(alert_type, styles["info"])
    
    return _flatten(f"""
        <div style="
            background: {s['bg']};
            border-left: 3px solid {s['border']};
            border-radius: 0 var(--radius-card, 8px) var(--radius-card, 8px) 0;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
            color: {s['color']};
            font-size: 0.88rem;
            line-height: 1.5;
        ">
            <span style="font-size:1rem;margin-right:0.3rem;">{s['icon']}</span> {message}
        </div>
    """)

def contingency_toggle_css(container_key: str) -> str:
    return _flatten(f"""
        <style>
        div.st-key-{container_key},
        div.st-key-{container_key} > div,
        div.st-key-{container_key} div[data-testid="stVerticalBlock"],
        div.st-key-{container_key} div[data-testid="stVerticalBlockBorderWrapper"] {{
            width: fit-content !important;
        }}
        div.st-key-{container_key} {{
            display: inline-flex;
            align-items: center;
            background: #FFF9E0;
            border: 1px solid #E6CE63;
            border-radius: var(--radius-sm, 6px);
            padding: 0.1rem 0.55rem;
        }}
        div.st-key-{container_key}:has(input:checked) {{
            background: #FBF1C4;
            border-color: #E2B400;
        }}
        div.st-key-{container_key} label[data-testid="stWidgetLabel"] p {{
            font-weight: 600;
            font-size: 0.82rem;
            color: #6B5200;
            white-space: nowrap;
        }}
        div.st-key-{container_key} div[data-testid="stCheckbox"] {{
            gap: 0.35rem;
        }}
        </style>
    """)

def fmt_int(n):
    return f"{int(n):,}".replace(",", ".")

_ICONE_URNA = (
    '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="9" rx="2"/>'
    '<path d="M8 11V7.5L12 4l4 3.5V11"/><path d="M9.5 15.5l1.7 1.7 3.3-3.4"/></svg>'
)

def app_header(principal, kpis):
    """Cabeçalho do painel: marca e faixa de KPIs do recorte ativo."""
    pct = min(principal["pct"] * 100, 100)
    kpi_main = (
        '<div class="app-kpi app-kpi-main">'
        f'<div class="app-kpi-label">{html.escape(principal["label"])}</div>'
        f'<div class="app-kpi-value">{html.escape(principal["value"])}</div>'
        f'<div class="app-kpi-sub"><b>{principal["pct"]:.1%}</b> {html.escape(principal["sub"])}</div>'
        f'<div class="app-kpi-bar"><div style="width:{pct:.1f}%"></div></div></div>'
    )
    kpi_rest = "".join(
        '<div class="app-kpi">'
        f'<div class="app-kpi-label">{html.escape(k["label"])}</div>'
        f'<div class="app-kpi-value">{html.escape(str(k["value"]))}</div>'
        f'<div class="app-kpi-sub">{html.escape(k.get("sub", ""))}</div></div>'
        for k in kpis
    )
    return _flatten(f"""
        <div class="app-header">
            <div class="app-header-top">
                <div class="app-header-brand">
                    <div class="app-header-mark">{_ICONE_URNA}</div>
                    <div>
                        <div class="app-header-eyebrow">UFS · TRE-SE · Painel analítico</div>
                        <h1 class="app-header-title">Urnas eletrônicas em Sergipe</h1>
                        <p class="app-header-sub">Onde a votação atrasou, quais modelos estavam em campo e quem votou nessas seções.</p>
                    </div>
                </div>
            </div>
            <div class="app-kpis">{kpi_main}{kpi_rest}</div>
        </div>
    """)

def stat_tiles(items):
    """Cartões de indicadores: label, value, sub opcional, cor opcional da borda."""
    cells = "".join(
        f'<div class="stat-tile" style="--tile-color:{i.get("cor", "#1B4B7A")};">'
        f'<div class="stat-tile-label">{html.escape(i["label"])}</div>'
        f'<div class="stat-tile-value">{html.escape(str(i["value"]))}</div>'
        f'<div class="stat-tile-sub">{html.escape(i.get("sub", ""))}</div></div>'
        for i in items
    )
    return f'<div class="stat-tiles">{cells}</div>'

def callout(texto_html):
    return f'<div class="callout">{texto_html}</div>'

def case_head(titulo, subtitulo, status_label, status_cor, chips):
    chips_html = "".join(f'<span class="case-chip">{c}</span>' for c in chips)
    return _flatten(f"""
        <div class="case-head" style="--case-color:{status_cor};">
            <div class="case-head-row">
                <div>
                    <div class="case-head-kicker">{html.escape(subtitulo)}</div>
                    <h3 class="case-head-title">{html.escape(titulo)}</h3>
                </div>
                <span class="status-pill" style="background:{status_cor};">{html.escape(status_label)}</span>
            </div>
            <div class="case-head-chips">{chips_html}</div>
        </div>
    """)
