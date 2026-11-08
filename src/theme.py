"""Identidade visual do painel de análise das urnas eletrônicas."""
import streamlit as st

_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800;900&display=swap');

:root {
    --color-primary-blue: #1B4B7A;
    --color-primary-blue-dark: #0F2E4F;
    --color-primary-blue-light: #4A90C8;
    --color-primary-green: #2D5F3F;
    --color-primary-green-light: #5A8F6B;
    --color-milk-white: #FAF8F3;
    --color-neutral-gray: #527080;
    --color-neutral-gray-light: #8794AA;
    --color-canvas: #F5F3ED;
    --color-surface: #FAF8F3;
    --color-surface-2: #EDE9E0;
    --color-border: #D4CFC4;
    --color-ink: #1B2D38;
    --color-ink-mid: #1B2D38;
    --color-ink-soft: #1B2D38;
    --color-ink-muted: #1B2D38;
    --navy: #1B4B7A;
    --blue: #4A90C8;
    --cyan: #2D5F3F;
    --ink: #1B2D38;
    --muted: #1B2D38;
    --canvas: #F5F3ED;
    --surface: #FAF8F3;
    --line: #D4CFC4;
    --soft: #E8E4DA;
    --radius: 8px;
    --color-brand: #2D5F3F;
}

html, body, [class*="css"], .stApp {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    color: var(--color-ink);
    font-size: 16px !important;
}

.stApp, [data-testid="stAppViewContainer"] {
    background: var(--color-canvas);
}

.block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding: 2rem 2.4rem 3rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stDecoration"] {
    display: none;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FILTROS GLOBAIS (barra no topo da página, substitui a sidebar)
   ═══════════════════════════════════════════════════════════════════════════ */
.st-key-filtros_globais {
    background: #FFFFFF;
    border: 2px solid #D4CFC4;
    border-radius: 14px;
    padding: 0.8rem 1.2rem 0.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 14px rgba(27, 75, 122, 0.06);
}
.st-key-filtros_globais [data-testid="stWidgetLabel"] p {
    color: #1B4B7A;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 13px;
    font-weight: 800;
}
.st-key-filtros_globais [data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 2px solid #1B4B7A !important;
    border-radius: 10px;
}
.st-key-filtros_globais [role="radiogroup"] { gap: 0.5rem; }
.st-key-filtros_globais [role="radiogroup"] label {
    background: #FAF8F3;
    border: 2px solid #1B4B7A;
    border-radius: 10px;
    padding: 0.4rem 0.9rem;
    transition: background 0.2s ease;
}
.st-key-filtros_globais [role="radiogroup"] label:hover { background: #EDE9E0; }
.st-key-filtros_globais [role="radiogroup"] label:has(input:checked) {
    background: #2D5F3F;
    border-color: #2D5F3F;
}
.st-key-filtros_globais [role="radiogroup"] label:has(input:checked) * { color: #FFFFFF; }

/* ═══════════════════════════════════════════════════════════════════════════
   APP HEADER
   ═══════════════════════════════════════════════════════════════════════════ */
.app-header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(120deg, #0F2E4F 0%, #1B4B7A 62%, #24604A 100%);
    border-radius: 20px;
    padding: 1.5rem 2rem 1.4rem;
    margin: 0 0 1.4rem;
    color: #FFFFFF;
    box-shadow: 0 18px 44px rgba(15, 46, 79, 0.30);
}
.app-header::after {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(135deg, rgba(255,255,255,0.035) 0 2px, transparent 2px 26px);
    pointer-events: none;
}
.app-header > * { position: relative; z-index: 1; }
.app-header-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1.5rem;
    flex-wrap: wrap;
}
.app-header-brand { display: flex; gap: 1.1rem; align-items: center; min-width: 0; }
.app-header-mark {
    flex: 0 0 60px;
    width: 60px;
    height: 60px;
    border-radius: 16px;
    display: grid;
    place-items: center;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.28);
}
.app-header-eyebrow {
    font-size: 12px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #A8D5E8;
}
.app-header-title {
    font-size: clamp(1.6rem, 2.6vw, 2.25rem);
    font-weight: 900;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 0.2rem 0 0.3rem;
    color: #FFFFFF;
}
.app-header-sub { margin: 0; font-size: 14px; color: #D4E4F0; max-width: 640px; }
.app-kpis {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr 1fr;
    gap: 0.8rem;
    margin-top: 1.3rem;
}
.app-kpi {
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 14px;
    padding: 0.85rem 1.1rem;
    min-width: 0;
}
.app-kpi-label { font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #A8D5E8; }
.app-kpi-value {
    font-size: clamp(1.5rem, 2.4vw, 2.15rem);
    font-weight: 900;
    line-height: 1.15;
    color: #FFFFFF;
    overflow-wrap: anywhere;
}
.app-kpi-sub { font-size: 13px; color: #C3DBEA; }
.app-kpi-sub b { color: #FFFFFF; }
.app-kpi-bar {
    height: 6px;
    margin-top: 0.55rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.16);
    overflow: hidden;
}
.app-kpi-bar > div { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #7FC4EC, #8FD3A6); }

/* ═══════════════════════════════════════════════════════════════════════════
   KPI STRIP
   ═══════════════════════════════════════════════════════════════════════════ */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 0 0 2rem;
}

.kpi-cell {
    position: relative;
    background: #FFFFFF;
    border: 2px solid #1B4B7A;
    border-radius: 14px;
    padding: 1.4rem 1.2rem;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.12), 0 2px 8px rgba(27, 75, 122, 0.08);
    transition: all 0.25s ease;
    overflow: hidden;
}

.kpi-cell::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #1B4B7A 0%, #2D5F3F 100%);
}

.kpi-cell:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(27, 75, 122, 0.18), 0 4px 12px rgba(27, 75, 122, 0.12);
    border-color: #2D5F3F;
}

.kpi-cell::after {
    content: "";
    position: absolute;
    bottom: -20px;
    right: -20px;
    width: 80px;
    height: 80px;
    border: 2px solid rgba(27, 75, 122, 0.06);
    border-radius: 50%;
    pointer-events: none;
}

.kpi-label {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #1B4B7A;
    margin-bottom: 0.6rem;
    position: relative;
    z-index: 1;
}

.kpi-value {
    font-size: 24px;
    font-weight: 900;
    color: #1B2D38;
    line-height: 1.1;
    position: relative;
    z-index: 1;
    letter-spacing: -0.02em;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION HEADERS
   ═══════════════════════════════════════════════════════════════════════════ */
.section-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 2rem 0 0.5rem;
    padding-bottom: 0.8rem;
    border-bottom: 3px solid #1B4B7A;
    position: relative;
}

.section-header::after {
    content: "";
    position: absolute;
    bottom: -3px;
    left: 0;
    width: 80px;
    height: 3px;
    background: #2D5F3F;
}

.section-header h2 {
    font-size: 22px;
    font-weight: 900;
    color: #1B4B7A;
    margin: 0;
    letter-spacing: -0.02em;
    text-transform: uppercase;
}

.section-desc, .section-intro {
    font-size: 16px;
    color: #1B2621;
    line-height: 1.6;
    margin: 0 0 1.2rem;
    max-width: 850px;
    font-weight: 700;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CHART CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
div[class*="st-key-cc"] {
    position: relative;
    min-width: 0;
    width: 100%;
    box-sizing: border-box;
    background: #FFFFFF;
    border: 2px solid #D4CFC4;
    border-radius: 16px;
    padding: 1.2rem 1.1rem 0.6rem;
    margin: 0.8rem 0 1.5rem;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.08), 0 2px 8px rgba(27, 75, 122, 0.04);
    overflow: visible;
    transition: all 0.25s ease;
}

div[class*="st-key-cc"]:hover {
    border-color: #1B4B7A;
    box-shadow: 0 12px 32px rgba(27, 75, 122, 0.14), 0 4px 12px rgba(27, 75, 122, 0.08);
    transform: translateY(-2px);
}

div[class*="st-key-cc"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #1B4B7A 0%, #2D5F3F 100%);
    border-radius: 16px 16px 0 0;
}

div[class*="st-key-cc"] [data-testid="stPlotlyChart"] {
    background: transparent;
    border: 0;
    width: 100% !important;
    min-width: 0 !important;
    overflow: hidden;
}

div[class*="st-key-cc"] [data-testid="stVerticalBlock"] {
    gap: 0.25rem;
}

.chart-card-head {
    padding: 0.2rem 0.3rem 0.4rem;
    border-bottom: 1px solid #E8E4DA;
    margin-bottom: 0.8rem;
}

.chart-card-title {
    font-size: 18px;
    font-weight: 900;
    color: #1B4B7A;
    display: flex;
    align-items: center;
    gap: 10px;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}

.chart-card-desc {
    font-size: 15px;
    color: #1B2621;
    line-height: 1.5;
    margin: 0.4rem 0 0;
    font-weight: 700;
}

.info-tip-btn {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 24px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #1B4B7A;
    color: #FFFFFF;
    border: 2px solid #FFFFFF;
    font-size: 14px;
    font-weight: 900;
    cursor: help;
    z-index: 20;
    box-shadow: 0 2px 6px rgba(27, 75, 122, 0.3);
}

.info-tip-box {
    display: none;
    position: absolute;
    top: calc(100% + 9px);
    left: 0;
    width: 320px;
    max-width: min(320px, calc(100vw - 48px));
    padding: 0.9rem 1rem;
    background: #1B4B7A;
    color: #fff;
    border: 2px solid #4A90C8;
    border-radius: 12px;
    font-size: 15px;
    line-height: 1.5;
    white-space: normal;
    overflow-wrap: anywhere;
    box-shadow: 0 12px 32px rgba(27, 75, 122, 0.35);
    z-index: 99999;
    font-weight: 700;
}

.info-tip-btn:hover .info-tip-box,
.info-tip-btn:focus .info-tip-box,
.info-tip-btn:focus-within .info-tip-box {
    display: block;
}

.chart-card-head, .chart-card-title {
    position: relative;
    overflow: visible;
}

/* ═══════════════════════════════════════════════════════════════════════════
   METRIC CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
.metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.2rem;
    margin: 1rem 0 1.8rem;
}

.metric-card {
    background: #FFFFFF;
    border: 2px solid #D4CFC4;
    border-top: 5px solid var(--color-primary-green);
    border-radius: 14px;
    padding: 1.4rem;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.08), 0 2px 8px rgba(27, 75, 122, 0.04);
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(27, 75, 122, 0.14), 0 4px 12px rgba(27, 75, 122, 0.08);
    border-color: #1B4B7A;
}

.metric-card::before {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 60px;
    height: 60px;
    background: radial-gradient(circle, rgba(27, 75, 122, 0.06) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.metric-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 2px solid #E8E4DA;
}

.metric-card-model {
    font-size: 20px;
    font-weight: 900;
    letter-spacing: -0.02em;
}

.metric-card-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

.metric-card-stat {
    display: flex;
    flex-direction: column;
}

.metric-card-stat-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #527080;
    margin-bottom: 0.3rem;
}

.metric-card-stat-value {
    font-size: 22px;
    font-weight: 900;
    color: #1B2D38;
    line-height: 1.1;
}

.metric-card-stat-pct {
    font-size: 14px;
    font-weight: 700;
    color: #2D5F3F;
    margin-top: 0.2rem;
}

.metric-card-track {
    background: #E8E4DA;
    border-radius: 999px;
    height: 10px;
    margin-top: 0.8rem;
    overflow: hidden;
}

.metric-card-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.3s ease;
}

.metric-card-name-wrap {
    position: relative;
    display: inline-flex;
    max-width: 100%;
    cursor: help;
}

.metric-card-tooltip {
    display: none;
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    width: 300px;
    max-width: calc(100vw - 48px);
    padding: 0.9rem 1rem;
    background: #1B4B7A;
    color: #fff;
    border: 2px solid #4A90C8;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.5;
    white-space: normal;
    overflow-wrap: anywhere;
    box-shadow: 0 12px 32px rgba(27, 75, 122, 0.35);
    z-index: 99999;
    font-weight: 700;
}

.metric-card-name-wrap:hover .metric-card-tooltip,
.metric-card-name-wrap:focus .metric-card-tooltip {
    display: block;
}

/* ═══════════════════════════════════════════════════════════════════════════
   STATUS LEGEND
   ═══════════════════════════════════════════════════════════════════════════ */
.geo-legend-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0.6rem 0 1.4rem;
    padding: 1rem 1.2rem;
    background: #FFFFFF;
    border: 2px solid #1B4B7A;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.1), 0 2px 8px rgba(27, 75, 122, 0.06);
}

.geo-legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: #FAF8F3;
    border: 2px solid #D4CFC4;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 700;
    color: #1B2621;
    line-height: 1.2;
    transition: all 0.2s ease;
}

.geo-legend-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(27, 75, 122, 0.15);
    border-color: #1B4B7A;
}

.geo-legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.9), 0 2px 4px rgba(0, 0, 0, 0.1);
}

.geo-legend-label {
    font-weight: 800;
    color: #1B2D38;
}

.geo-legend-interval {
    color: #1B2D38;
    font-size: 13px;
    font-weight: 700;
}

.geo-legend-nc {
    color: #1B2D38;
}

/* ═══════════════════════════════════════════════════════════════════════════
   MODEL LEGEND
   ═══════════════════════════════════════════════════════════════════════════ */
.model-legend-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 0.4rem 0 1.4rem;
    padding: 0.8rem 1rem;
    background: #FFFFFF;
    border: 2px solid #1B4B7A;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.1), 0 2px 8px rgba(27, 75, 122, 0.06);
}

.model-legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: #FAF8F3;
    border: 2px solid #D4CFC4;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 800;
    color: #1B2621;
    box-shadow: 0 2px 6px rgba(27, 75, 122, 0.08);
    transition: all 0.2s ease;
}

.model-legend-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(27, 75, 122, 0.18);
    border-color: #1B4B7A;
}

.model-legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.9), 0 2px 4px rgba(0, 0, 0, 0.15);
}

/* ═══════════════════════════════════════════════════════════════════════════
   Tabs — nível 1: barra segmentada; nível 2 (dentro de painel): sublinhado
   ═══════════════════════════════════════════════════════════════════════════ */
.nav-caption {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #1B4B7A;
    margin: 0.25rem 0 0.65rem;
}

[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] { display: none !important; }

/* Nível 1: abas sem fundo, texto azul; a aba ativa ganha apenas o sublinhado verde */
[role="tablist"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 0.4rem !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    border-bottom: 2px solid #D4CFC4 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    margin-bottom: 0.8rem !important;
    overflow-x: auto !important;
}

[role="tablist"] button[role="tab"],
[role="tablist"] [role="tab"] {
    flex: 1 1 auto !important;
    min-width: max-content !important;
    white-space: nowrap !important;
    height: 46px !important;
    margin: 0 !important;
    padding: 0 1.1rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.4rem !important;
    border: 0 !important;
    border-radius: 8px 8px 0 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #1B4B7A !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    transition: background 0.18s ease, color 0.18s ease !important;
}

[role="tablist"] [role="tab"] p,
[role="tablist"] [role="tab"] span,
[role="tablist"] [role="tab"] div {
    color: inherit !important;
    font-size: 14px !important;
    font-weight: 900 !important;
    line-height: 1.1 !important;
}

[role="tablist"] [role="tab"]:hover {
    background: rgba(27, 75, 122, 0.08) !important;
    color: #0F2E4F !important;
}

[role="tablist"] [aria-selected="true"] {
    background: transparent !important;
    color: #0F2E4F !important;
    box-shadow: inset 0 -4px 0 #2D5F3F !important;
}

[role="tabpanel"] { padding-top: 1.2rem; }

/* Nível 2 (abas dentro de painel): sublinhado, mais discreto */
[role="tabpanel"] [role="tablist"] {
    gap: 0.9rem !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    border-top: 0 !important;
    border-bottom: 3px solid #D4CFC4 !important;
    margin-bottom: 0 !important;
}

[role="tabpanel"] [role="tablist"] button[role="tab"],
[role="tabpanel"] [role="tablist"] [role="tab"] {
    flex: 0 0 auto !important;
    height: 54px !important;
    padding: 0 1.5rem !important;
    border: 0 !important;
    border-radius: 12px 12px 0 0 !important;
    background: transparent !important;
    color: #1B2D38 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

[role="tabpanel"] [role="tablist"] [role="tab"] p,
[role="tabpanel"] [role="tablist"] [role="tab"] span,
[role="tabpanel"] [role="tablist"] [role="tab"] div {
    font-size: 17px !important;
    -webkit-text-stroke: 0;
}

[role="tabpanel"] [role="tablist"] [role="tab"]:hover {
    background: rgba(27, 75, 122, 0.09) !important;
    color: #1B4B7A !important;
}

[role="tabpanel"] [role="tablist"] [aria-selected="true"] {
    background: rgba(27, 75, 122, 0.08) !important;
    color: #1B4B7A !important;
    box-shadow: inset 0 -5px 0 #2D5F3F !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Estudo de seção: tiles, callout, prontuário
   ═══════════════════════════════════════════════════════════════════════════ */
.stat-tiles {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 1rem;
    margin: 0.6rem 0 1.2rem;
}
.stat-tile {
    background: #FFFFFF;
    border: 2px solid #D4CFC4;
    border-left: 6px solid var(--tile-color, #1B4B7A);
    border-radius: 14px;
    padding: 0.95rem 1.2rem;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.08);
}
.stat-tile-label { font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: #527080; }
.stat-tile-value { font-size: 26px; font-weight: 900; line-height: 1.15; color: #1B2D38; }
.stat-tile-sub { font-size: 13px; color: #527080; min-height: 1.2em; }

.callout {
    background: #EEF4F8;
    border-left: 5px solid #1B4B7A;
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.2rem;
    margin: 0.4rem 0 1.2rem;
    font-size: 15px;
    line-height: 1.55;
    color: #1B2D38;
}

.case-head {
    background: #FFFFFF;
    border: 2px solid #D4CFC4;
    border-left: 8px solid var(--case-color, #1B4B7A);
    border-radius: 14px;
    padding: 1rem 1.3rem;
    margin: 0.8rem 0 0.4rem;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.08);
}
.case-head-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
.case-head-kicker { font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #527080; }
.case-head-title { margin: 0.1rem 0 0; font-size: 22px; font-weight: 900; color: #1B2D38; }
.status-pill {
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 800;
    white-space: nowrap;
}
.case-head-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.7rem; }
.case-chip {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    background: #F1EEE6;
    border: 1px solid #D4CFC4;
    font-size: 13px;
    color: #1B2D38;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Geo Panel
   ═══════════════════════════════════════════════════════════════════════════ */
.geo-panel, .geo-legend-wrap {
    background: #FFFFFF;
    border: 2px solid #1B4B7A;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(27, 75, 122, 0.1), 0 2px 8px rgba(27, 75, 122, 0.06);
}

.geo-panel-title {
    color: #1B4B7A;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 15px;
    font-weight: 900;
    border-bottom: 2px solid #1B4B7A;
    padding-bottom: 0.5rem;
    margin-bottom: 0.8rem;
}

.status-badge {
    border-radius: 999px;
    padding: 0.3rem 0.8rem;
    font-size: 14px;
    font-weight: 800;
    border: 2px solid currentColor;
}

.footer {
    border-top: 2px solid #1B4B7A;
    margin-top: 3rem;
    padding-top: 1.2rem;
    color: #1B2621;
    font-size: 14px;
    line-height: 1.6;
    font-weight: 700;
}

.stAlert {
    border-radius: 12px;
    border-width: 2px;
}

[data-testid="stPlotlyChart"] {
    width: 100% !important;
    min-width: 0 !important;
    max-width: 100%;
    overflow: hidden;
}

[data-testid="stHorizontalBlock"] {
    align-items: stretch;
    gap: 1.2rem;
}

[data-testid="stColumn"] {
    min-width: 0 !important;
    max-width: 100%;
}

[data-testid="stVerticalBlock"] {
    min-width: 0;
}

[data-testid="stPlotlyChart"] iframe {
    max-width: 100% !important;
}

.stApp [data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 2px solid #1B4B7A !important;
    color: #1B2621 !important;
    border-radius: 10px;
    font-weight: 700;
}

.stApp [data-baseweb="select"] input,
.stApp [data-baseweb="select"] span {
    color: #1B2621 !important;
    -webkit-text-fill-color: #1B2621 !important;
}

[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"] {
    background: #FFFFFF !important;
    color: #1B2621 !important;
}

[data-baseweb="popover"] [role="option"] * {
    color: #1B2621 !important;
    -webkit-text-fill-color: #1B2621 !important;
}

[data-baseweb="popover"] [role="option"]:hover {
    background: #FAF8F3 !important;
}

.stTabs [data-baseweb="tab-panel"] [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 1.2rem !important;
}

.stTabs [data-baseweb="tab-panel"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
    flex: 1 1 100% !important;
}

.stTabs [data-baseweb="tab-panel"] [data-testid="stPlotlyChart"] {
    min-height: 480px !important;
}

/* Aba Território: mapa à esquerda, controles e resumo à direita (exceção à regra de empilhar colunas) */
@media (min-width: 901px) {
    [role="tabpanel"] .st-key-geo_layout [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: flex-start !important;
    }
    [role="tabpanel"] .st-key-geo_layout [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    [role="tabpanel"] .st-key-geo_layout [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
        max-width: none !important;
        width: auto !important;
        flex: 1 1 0 !important;
    }
    [role="tabpanel"] .st-key-geo_layout [data-testid="stHorizontalBlock"] > :last-child {
        flex: 0 0 340px !important;
    }
}

/* Responsive */
@media (max-width: 1100px) {
    .kpi-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 900px) {
    .app-kpis {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 100% !important;
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    
    .kpi-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    
    .kpi-cell {
        padding: 1rem;
    }
}

@media (max-width: 700px) {
    .block-container {
        padding: 1rem 0.8rem 2rem;
    }
    
    .app-header {
        padding: 1.2rem 1.1rem;
        border-radius: 16px;
    }
    
    .app-kpis {
        grid-template-columns: 1fr;
    }
    
    
    .kpi-strip {
        grid-template-columns: 1fr;
        gap: 0.8rem;
    }
    
    .kpi-cell {
        padding: 1rem;
    }
    
    .kpi-value {
        font-size: 1.4rem;
    }
    
    [role="tablist"] [role="tab"] {
        padding: 0 0.7rem !important;
        height: 38px !important;
    }
    [role="tablist"] [role="tab"] p,
    [role="tablist"] [role="tab"] span {
        font-size: 12px !important;
    }
    [role="tablist"] { gap: 4px !important; }
}
# /* ═══════════════════════════════════════════════════════════════════════════
#    TESTE: fundo da página igual ao do cabeçalho (para reverter, apague este bloco)
#    ═══════════════════════════════════════════════════════════════════════════ */
# .stApp, [data-testid="stAppViewContainer"] {
#     background:
#         repeating-linear-gradient(135deg, rgba(255,255,255,0.035) 0 2px, transparent 2px 26px),
#         linear-gradient(120deg, #0F2E4F 0%, #1B4B7A 62%, #24604A 100%) !important;
#     background-attachment: fixed !important;
# }

# /* Texto que fica direto sobre o fundo escuro */
# [role="tablist"] { border-bottom-color: rgba(255,255,255,0.28) !important; }
# [role="tablist"] button[role="tab"], [role="tablist"] [role="tab"] { color: #D4E4F0 !important; }
# [role="tablist"] [role="tab"]:hover { background: rgba(255,255,255,0.12) !important; color: #FFFFFF !important; }
# [role="tablist"] [aria-selected="true"] { color: #FFFFFF !important; box-shadow: inset 0 -4px 0 #5A8F6B !important; }
# [role="tabpanel"] [role="tablist"] { border-bottom-color: rgba(255,255,255,0.28) !important; }
# [role="tabpanel"] [role="tablist"] button[role="tab"],
# [role="tabpanel"] [role="tablist"] [role="tab"] { color: #D4E4F0 !important; }
# [role="tabpanel"] [role="tablist"] [role="tab"]:hover { background: rgba(255,255,255,0.12) !important; color: #FFFFFF !important; }
# [role="tabpanel"] [role="tablist"] [aria-selected="true"] { background: rgba(255,255,255,0.12) !important; color: #FFFFFF !important; box-shadow: inset 0 -5px 0 #5A8F6B !important; }

# .section-header { border-bottom-color: rgba(255,255,255,0.55); }
# .section-header h2 { color: #FFFFFF; }
# .section-header::after { background: #5A8F6B; }
# .section-desc, .section-intro { color: #E3EEF7; }
# .geo-panel-title { color: #FFFFFF; border-bottom-color: rgba(255,255,255,0.55); }
# .nav-caption { color: #CFE3F5; }
# .footer { color: #D4E4F0; border-top-color: rgba(255,255,255,0.45); }
# .footer a { color: #FFFFFF; }
# [data-testid="stHeader"] { background: transparent; }
</style>
"""

def aplicar_tema():
    st.markdown(_CSS, unsafe_allow_html=True)