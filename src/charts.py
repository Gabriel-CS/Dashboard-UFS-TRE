"""Construtores de gráficos Plotly padronizados."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
from src.analysis import MODEL_COLOR, URN_MODELS, ramp, ramp_neutro

_INK, _SOFT, _RULE, _GRID = "#1B2D38", "#536873", "#CBD8D2", "#E5ECE8"
_ACCENT = "#16845B"
_ACCENT_BLUE = "#246B9A"
_NEUTRAL = "#527080"

_MODEL_SHADES: dict[str, str] = MODEL_COLOR.copy()

def _is_model_axis(x) -> bool:
    xs = [str(v) for v in x]
    return bool(xs) and all(v in _MODEL_SHADES for v in xs)

def _cat_color(cat, i: int) -> str:
    name = str(cat)
    if name in _MODEL_SHADES:
        return _MODEL_SHADES[name]
    return _NEUTRAL

def _derive_shade(base_color: str, position: int, total: int) -> str:
    """
    Deriva um tom de uma cor base.
    position=0 → mais claro (quase branco)
    position=total-1 → cor base pura
    """
    h = base_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    
    # Interpola entre branco (255,255,255) e a cor base
    factor = 0.35 + 0.65 * position / max(total - 1, 1)
    # Começa claro e vai escurecendo
    nr = int(255 - (255 - r) * factor)
    ng = int(255 - (255 - g) * factor)
    nb = int(255 - (255 - b) * factor)
    
    # Clamp
    nr = max(0, min(255, nr))
    ng = max(0, min(255, ng))
    nb = max(0, min(255, nb))
    
    return f"#{nr:02x}{ng:02x}{nb:02x}"

_LAYOUT_BASE = dict(
    paper_bgcolor="#FAFCFA",
    plot_bgcolor="#FAFCFA",
    font=dict(family="JetBrains Mono, monospace", color=_SOFT, size=15, weight="bold"),
    title=dict(
        font=dict(size=18, color="#174A78", family="JetBrains Mono, monospace", weight="bold"),
        x=0, xanchor="left",
    ),
    margin=dict(t=30, b=40, l=50, r=20),
    xaxis=dict(showgrid=False, linecolor=_RULE, ticks="outside", tickcolor=_RULE, zeroline=False,
               tickfont=dict(color="#1B2D38", size=14, weight="bold")),
    yaxis=dict(showgrid=True, gridcolor=_GRID, linecolor=_RULE, zeroline=False, zerolinecolor=_RULE,
               tickfont=dict(color="#1B2D38", size=14, weight="bold")),
    legend=dict(bgcolor="rgba(27, 75, 122, 0.9)", bordercolor=_RULE, borderwidth=1,
                font=dict(color="#FFFFFF", size=14, weight="bold")),
    hoverlabel=dict(
        bgcolor="#174A78",
        font=dict(color="white", family="JetBrains Mono, monospace", size=14, weight="bold"),
        bordercolor="#174A78",
    ),
    showlegend=False,
)

def _ink_on(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return _INK if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "white"

ink_on = _ink_on


def _ordem_modelos(x):
    presentes = {str(v) for v in x}
    return [m for m in URN_MODELS if m in presentes]


def apply_base_layout(fig: go.Figure, height: int = 480) -> go.Figure:
    fig.update_layout(**_LAYOUT_BASE)
    fig.update_layout(height=height)
    return fig

def _maybe_title(fig: go.Figure, title: str | None) -> None:
    if title:
        fig.update_layout(title=title)
        fig.update_layout(margin=dict(t=56, b=40, l=50, r=20))

def _add_model_identity_strip(
    fig: go.Figure,
    x_categories: list[str],
    y_bottom: float = -0.08,
    y_top: float = -0.03,
) -> None:
    for j, cat in enumerate(x_categories):
        cor = _MODEL_SHADES.get(str(cat))
        if cor is None:
            continue
        fig.add_shape(
            type="rect",
            x0=j - 0.4, x1=j + 0.4, y0=y_bottom, y1=y_top,
            xref="x", yref="paper",
            fillcolor=cor,
            line=dict(width=0),
            layer="below",
        )

def bar_chart(
    x,
    y,
    text=None,
    title: str | None = None,
    yfmt: str | None = None,
    yrange: list | None = None,
    height: int = 480,
    x_categoryorder: list | None = None,
    model_identity_strip: bool = False,
) -> go.Figure:
    if _is_model_axis(x):
        if x_categoryorder is None:
            x_categoryorder = _ordem_modelos(x)
        model_identity_strip = False  # a própria barra já carrega a cor do modelo
    cores = [_cat_color(cat, i) for i, cat in enumerate(x)]
    fig = go.Figure(go.Bar(
        x=x, y=y,
        marker_color=cores,
        marker_line=dict(color="rgba(255,255,255,0.85)", width=0.8),
        text=text or [f"{v:.1%}" if isinstance(v, float) and v < 1 else str(v) for v in y],
        textposition="outside",
        textfont=dict(size=14, color=_INK, weight="bold"),
        width=0.6,
    ))
    _maybe_title(fig, title)
    if yfmt:
        fig.update_layout(yaxis_tickformat=yfmt)
    if yrange:
        fig.update_layout(yaxis_range=yrange)
    if x_categoryorder is not None:
        fig.update_layout(xaxis=dict(
            categoryorder="array",
            categoryarray=x_categoryorder,
            showgrid=False,
            linecolor=_RULE,
        ))
    fig = apply_base_layout(fig, height)
    if model_identity_strip:
        cats = list(x_categoryorder) if x_categoryorder is not None else list(x)
        _add_model_identity_strip(fig, cats)
        fig.update_layout(margin=dict(t=30, b=60, l=50, r=20))
    return fig

def bar_chart_with_error(
    x,
    y,
    errors,
    text=None,
    title: str | None = None,
    yfmt: str | None = None,
    yrange: list | None = None,
    height: int = 480,
    error_suffix: str = "",
    model_identity_strip: bool = False,
) -> go.Figure:
    model_identity_strip = False  # barras já levam a cor do modelo
    cores = [_cat_color(cat, i) for i, cat in enumerate(x)]
    text_labels = text or [f"{v:.1f}" for v in y]
    fig = go.Figure(go.Bar(
        x=x, y=y,
        marker_color=cores,
        marker_line=dict(color="rgba(255,255,255,0.85)", width=0.8),
        error_y=dict(
            type="data", array=list(errors), visible=True,
            color="#527080", thickness=1.5, width=6,
        ),
        text=text_labels, textposition="outside",
        textfont=dict(size=14, color=_INK, weight="bold"),
        width=0.6,
        hovertemplate=(
            "<b>%{x}</b><br>Média: %{y:.1f}" + error_suffix +
            "<br>Desvio padrão: %{error_y.array:.1f}" + error_suffix +
            "<extra></extra>"
        ),
    ))
    _maybe_title(fig, title)
    if yfmt:
        fig.update_layout(yaxis_tickformat=yfmt)
    if yrange:
        fig.update_layout(yaxis_range=yrange)
    else:
        max_val = max((v + (e or 0) for v, e in zip(y, errors)), default=1)
        fig.update_layout(yaxis_range=[0, max_val * 1.3 or 1])
    if _is_model_axis(x):
        fig.update_layout(xaxis=dict(categoryorder="array", categoryarray=_ordem_modelos(x)))
    fig = apply_base_layout(fig, height)
    if model_identity_strip:
        _add_model_identity_strip(fig, list(x))
        fig.update_layout(margin=dict(t=30, b=60, l=50, r=20))
    return fig

def derive_shade(base_color, position, total):
    return _derive_shade(base_color, position, total)


# Base cinza-escura: a escala claro -> escuro da legenda fica legível e não imita nenhum modelo.
_BASE_LEGENDA = "#34424B"

# Legenda sobre fundo claro (a antiga, azul-escura, "apagava" os tons pálidos da escala).
LEGENDA_TONS = dict(
    orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
    bgcolor="rgba(255,255,255,0.95)", bordercolor=_RULE, borderwidth=1,
    font=dict(color=_INK, size=14, weight="bold"),
)


def legenda_tons(fig, nomes, base=_BASE_LEGENDA):
    """Entradas de legenda neutras (claro -> escuro), na mesma escala de tons aplicada a cada modelo."""
    for i, nome in enumerate(nomes):
        fig.add_trace(go.Bar(
            x=[None], y=[None], name=nome, showlegend=True,
            marker_color=_derive_shade(base, i, len(nomes)),
        ))


def stacked_bar(df_pct, labels, colors, title=None, height=500, model_colors=None,
                shade_by_model=True, cat_colors=None):
    """
    Barras empilhadas (100%) por modelo, sem legenda. Com `cat_colors` (categoria -> cor) cada
    categoria tem cor fixa; sem ele, cada barra usa tons da cor do modelo. A identificação
    das categorias é feita no hover (modelo, categoria e percentual).
    `colors` é mantido por compatibilidade.
    """
    fig = go.Figure()
    labels = [l for l in labels if l in df_pct.columns]
    n_cats = len(labels)
    cores_modelo = model_colors or _MODEL_SHADES

    for i, col in enumerate(labels):
        vals = df_pct[col].values
        if cat_colors:
            cores = [cat_colors.get(col, _NEUTRAL)] * len(URN_MODELS)
        else:
            cores = [_derive_shade(cores_modelo.get(m, _NEUTRAL), i, n_cats) for m in URN_MODELS]
        fig.add_trace(go.Bar(
            x=URN_MODELS, y=vals, name=col, showlegend=False,
            marker_color=cores,
            marker_line=dict(color="rgba(255,255,255,0.6)", width=0.5),
            text=[f"{v*100:.1f}%" if v > 0.04 else "" for v in vals],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(size=12, color=[_ink_on(c) for c in cores], weight="bold"),
            hovertemplate=f"<b>%{{x}}</b><br>{col}: %{{y:.1%}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        margin=dict(t=30, b=40, l=50, r=20),
        xaxis=dict(categoryorder="array", categoryarray=URN_MODELS, showgrid=False, linecolor=_RULE,
                   tickfont=dict(color="#1B2D38", size=14, weight="bold")),
    )
    fig.update_layout(yaxis=dict(
        tickformat=".0%", range=[0, 1.0], gridcolor=_GRID, linecolor=_RULE,
        tickfont=dict(color="#1B2D38", size=14, weight="bold"),
    ))
    _maybe_title(fig, title)
    fig = apply_base_layout(fig, height)
    fig.update_layout(showlegend=False)
    return fig

def donut_chart(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str | None = None,
    color_map: dict[str, str] | None = None,
    height: int = 460,
    show_legend: bool = True,
    hole: float = 0.55,
) -> go.Figure:
    if color_map is not None:
        cores = [color_map.get(str(lbl), _cat_color(lbl, i))
                 for i, lbl in enumerate(df[label_col])]
    elif _is_model_axis(df[label_col]):
        cores = [_MODEL_SHADES[str(lbl)] for lbl in df[label_col]]
    else:
        tons = ramp(len(df))
        cores = [tons[i % len(tons)] for i in range(len(df))]
    fig = go.Figure(go.Pie(
        labels=df[label_col],
        values=df[value_col],
        hole=hole,
        marker=dict(colors=cores, line=dict(color="white", width=2)),
        textinfo="percent+label" if len(df) <= 6 else "percent",
        textposition="outside",
        textfont=dict(size=14, color=_INK, weight="bold"),
        insidetextfont=dict(size=13, color="white", weight="bold"),
        pull=[0.02] * len(df),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Valor: %{value:,}<br>"
            "Proporção: %{percent}<br>"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        showlegend=show_legend,
        legend=dict(orientation="v", yanchor="middle", y=0.5,
                    xanchor="left", x=1.02,
                    font=dict(color="#FFFFFF", size=14, weight="bold"),
                    bgcolor="rgba(27, 75, 122, 0.9)"),
        margin=dict(t=60, b=60, l=40, r=130),
    )
    _maybe_title(fig, title)
    height = max(height, 70 * len(df) + 160)
    total = df[value_col].sum()
    fig.add_annotation(
        text=f"<b>{total:,.0f}</b><br>total",
        showarrow=False,
        font=dict(size=17, color=_SOFT, weight="bold"),
        x=0.5, y=0.5,
    )
    return apply_base_layout(fig, height)

def bullet_gauge_chart(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str | None = None,
    color_map: dict[str, str] | None = None,
    suffix: str = "%",
    max_val: float | None = None,
    height: int = 460,
) -> go.Figure:
    if max_val is None:
        max_val = df[value_col].max() * 1.2 if len(df) > 0 else 100
    def _cor(lbl) -> str:
        if color_map and str(lbl) in color_map:
            return color_map[str(lbl)]
        if str(lbl) in _MODEL_SHADES:
            return _MODEL_SHADES[str(lbl)]
        return _ACCENT
    cores = [_cor(lbl) for lbl in df[label_col]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df[label_col], x=[max_val] * len(df),
        orientation="h",
        marker_color=_GRID,
        width=0.42,
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.add_trace(go.Bar(
        y=df[label_col], x=df[value_col],
        orientation="h",
        marker_color=cores,
        marker_line=dict(color="rgba(255,255,255,0.6)", width=0.5),
        width=0.42,
        text=[f"{v:.1f}{suffix}" for v in df[value_col]],
        textposition="outside",
        textfont=dict(size=14, color=_INK, weight="bold"),
        hovertemplate=("<b>%{y}</b><br>" + f"{value_col}: %{{x:.1f}}{suffix}<br><extra></extra>"),
        showlegend=False,
    ))
    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="#FAFCFA",
        plot_bgcolor="#FAFCFA",
        font=dict(family="JetBrains Mono, monospace", color=_SOFT, size=15, weight="bold"),
        margin=dict(t=30, b=40, l=100, r=80),
        xaxis=dict(showgrid=False, linecolor=_RULE,
                   range=[0, max_val * 1.15], ticksuffix=suffix,
                   tickfont=dict(color="#1B2D38", size=14, weight="bold")),
        yaxis=dict(showgrid=False, linecolor=_RULE,
                   categoryorder="total ascending", automargin=True,
                   tickfont=dict(color="#1B2D38", size=14, weight="bold")),
        height=height,
    )
    _maybe_title(fig, title)
    return fig


add_model_strip = _add_model_identity_strip
