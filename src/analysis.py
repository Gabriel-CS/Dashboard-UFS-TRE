from __future__ import annotations
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# Constantes de Filtro Operacional (Single Source of Truth)
# ──────────────────────────────────────────────────────────────────────────────
FILTER_SOMENTE_CRITICAS = "Somente criticas"
FILTER_COM_ATRASO = "Com atraso"
FILTER_CONTINGENCIA = "Urnas em contingencia"

# ──────────────────────────────────────────────────────────────────────────────
# Paleta de Cores Principal (Single Source of Truth)
# ──────────────────────────────────────────────────────────────────────────────
# Cores primárias: azul marinho, verde mata, branco leite
COLOR_PRIMARY_BLUE = "#1B4B7A"
COLOR_PRIMARY_BLUE_LIGHT = "#4A90C8"
COLOR_PRIMARY_GREEN = "#2D5F3F"
COLOR_PRIMARY_GREEN_LIGHT = "#5A8F6B"
COLOR_NEUTRAL_GRAY = "#527080"
COLOR_NEUTRAL_GRAY_LIGHT = "#8794AA"
COLOR_MILK_WHITE = "#FAF8F3"

# Modelos de urna - paleta vibrante e distinta
URN_MODELS: list[str] = ["UE2009", "UE2010", "UE2011", "UE2013", "UE2015", "UE2020", "UE2022"]

MODEL_PALETTE: list[str] = [
    "#D32F2F",  # UE2009 - vermelho vibrante
    "#F57C00",  # UE2010 - laranja forte
    "#FBC02D",  # UE2011 - amarelo dourado
    "#388E3C",  # UE2013 - verde intenso
    "#00796B",  # UE2015 - verde-azulado (teal)
    "#1976D2",  # UE2020 - azul royal
    "#7B1FA2",  # UE2022 - roxo profundo
]

MODEL_COLOR: dict[str, str] = dict(zip(URN_MODELS, MODEL_PALETTE))

# Rampa ordinal (claro → escuro) para variáveis ordenadas
_RAMP_AZUL = [
    "#DCEAF2", "#B9D5E5", "#8DBBD4", "#65A4C8",
    "#438BAE", "#287B91", COLOR_PRIMARY_GREEN, "#116746"
]

def ramp(n: int) -> list[str]:
    """n tons da rampa azul, igualmente espaçados."""
    if n <= 1:
        return _RAMP_AZUL[-2:-1]
    step = (len(_RAMP_AZUL) - 1) / (n - 1)
    return [_RAMP_AZUL[round(i * step)] for i in range(n)]

# Status palette (cores semânticas para níveis de criticidade)
STATUS_LABELS: dict[int, str] = {
    0: "Sem atraso",
    1: "Normal",
    2: "Atraso leve",
    3: "Atraso moderado",
    4: "Atraso elevado",
}

# Nomes de exibição dos filtros agrupados (as constantes FILTER_* continuam sendo as chaves internas)
FILTER_LABELS: dict[str, str] = {
    FILTER_SOMENTE_CRITICAS: "Somente críticas",
    FILTER_COM_ATRASO: "Com atraso",
    FILTER_CONTINGENCIA: "Urnas em contingência",
}

# Opções do seletor global: rótulo exibido → valor interno
STATUS_OPCOES: dict[str, str | int] = {
    **{rotulo: chave for chave, rotulo in FILTER_LABELS.items()},
    **{f"Nível {n} — {rotulo}": n for n, rotulo in STATUS_LABELS.items()},
}

STATUS_PALETTE: dict[int, str] = {
    0: "#4F8FBF",  # aço
    1: "#F2C14E",  # âmbar
    2: "#EE8A32",  # laranja
    3: "#D1453B",  # vermelhão
    4: "#6B1030",  # vinho
}

# Tipos de evento operacional (abas de criticidade): matizes fora da escala de calor
EVENT_COLOR: dict[str, str] = {
    "Timeout de biometria": "#7B5EA7",
    "Inatividade do eleitor": "#2A9D8F",
    "Teclas indevidas": "#A47148",
}
COLOR_SECAO = "#1B4B7A"
COLOR_MEDIA = "#B7C0C7"


def _lerp_hex(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def tint(cor, t=0.6):
    """Clareia `cor` em direção ao branco (t=0 mantém; t=1 vira branco)."""
    return _lerp_hex(cor, "#FFFFFF", t)


def _rampa(n, ini, fim):
    return [ini] if n <= 1 else [_lerp_hex(ini, fim, i / (n - 1)) for i in range(n)]


def ramp_neutro(n):
    """Rampa cinza-azulada (claro -> escuro) para categorias ordenadas nos gráficos de modelo."""
    return _rampa(n, "#E4E9ED", "#34424B")


def ramp_perfil(n):
    """Rampa turquesa (claro -> escuro) para perfis ordenados (idade, escolaridade)."""
    return _rampa(n, "#CDE7E4", "#0B5550")


STATUS_DETALHES: dict[int, dict] = {
    0: {
        "label": "Sem Atraso", "cor": "#2F7BD9", "icon": "✔",
        "desc": "Operação fluida e contínua, sem atrasos registrados.",
        "intervalo": "< 6,48 min"
    },
    1: {
        "label": "Normal", "cor": COLOR_PRIMARY_GREEN, "icon": "↑",
        "desc": "Atraso leve, mantendo-se dentro da tolerância operacional esperada.",
        "intervalo": "≥ 6,48 min e < 32,15 min"
    },
    2: {
        "label": "Atenção", "cor": "#E2B400", "icon": "⚠",
        "desc": "Atraso moderado. O fluxo apresenta interrupções que requerem monitoramento.",
        "intervalo": "≥ 32,15 min e < 89,36 min"
    },
    3: {
        "label": "Crítico", "cor": "#E07B00", "icon": "✖",
        "desc": "Atraso elevado. Impacto sensível na formação de filas e retenção de eleitores.",
        "intervalo": "≥ 89,36 min e < 150 min"
    },
    4: {
        "label": "Super Crítica", "cor": "#C62828", "icon": "‼",
        "desc": "Atraso extremo. Risco iminente de não encerramento da votação no horário limite.",
        "intervalo": "≥ 150 min"
    },
}

for _n, _d in STATUS_DETALHES.items():
    _d["cor"] = STATUS_PALETTE[_n]
    _d["label"] = STATUS_LABELS[_n]

FILTRO_DETALHES: dict[str, dict] = {
    FILTER_SOMENTE_CRITICAS: {
        "label": FILTER_LABELS[FILTER_SOMENTE_CRITICAS], "cor": STATUS_PALETTE[3],
        "intervalo": "níveis 3 e 4",
        "desc": "Seções com atraso elevado ou extremo (a partir de 89,36 min). "
                "É o recorte mais restrito: só as seções onde a votação foi seriamente afetada.",
    },
    FILTER_COM_ATRASO: {
        "label": FILTER_LABELS[FILTER_COM_ATRASO], "cor": STATUS_PALETTE[2],
        "intervalo": "níveis 2, 3 e 4",
        "desc": "Todas as seções com atraso moderado, elevado ou extremo (a partir de 32,15 min). "
                "Não inclui as seções sem atraso nem as normais.",
    },
    FILTER_CONTINGENCIA: {
        "label": FILTER_LABELS[FILTER_CONTINGENCIA], "cor": "#7B5EA7",
        "intervalo": "troca de equipamento",
        "desc": "Seções em que houve urna de contingência: o equipamento original foi substituído "
                "durante a votação, ou a urna de contingência operou desde o início. "
                "É um recorte por ocorrência, não por faixa de tempo.",
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Colunas e constantes auxiliares
# ──────────────────────────────────────────────────────────────────────────────
COLS_LOG: list[str] = [
    "zona", "secao", "modelo", "t_intervalo_s", "n_tit_invalidos",
    "t_fila_s", "bio_solicitada", "n_tent_bio", "n_falhas_bio",
    "score_bio", "hab_cancelada", "hab_manual", "ts_titulo",
    "ts_habilitado", "ts_computado", "n_teclas_inv",
    "t_inatividade_s", "t_habilitacao_s", "completo",
    "ts_cod_encerramento", "ts_encerramento", "ts_gerando_resultado",
]

ESC_COLS: list[str] = [
    "ESC_ANALFABETO", "ESC_LÊ E ESCREVE",
    "ESC_ENSINO FUNDAMENTAL INCOMPLETO", "ESC_ENSINO FUNDAMENTAL COMPLETO",
    "ESC_ENSINO MÉDIO INCOMPLETO", "ESC_ENSINO MÉDIO COMPLETO",
    "ESC_SUPERIOR INCOMPLETO", "ESC_SUPERIOR COMPLETO",
]

ESC_LABELS: dict[str, str] = {
    "ESC_ANALFABETO": "Analfabeto",
    "ESC_LÊ E ESCREVE": "Lê/Escreve",
    "ESC_ENSINO FUNDAMENTAL INCOMPLETO": "Fund. Incomp.",
    "ESC_ENSINO FUNDAMENTAL COMPLETO": "Fund. Comp.",
    "ESC_ENSINO MÉDIO INCOMPLETO": "Médio Incomp.",
    "ESC_ENSINO MÉDIO COMPLETO": "Médio Comp.",
    "ESC_SUPERIOR INCOMPLETO": "Sup. Incomp.",
    "ESC_SUPERIOR COMPLETO": "Sup. Comp.",
}

# Cor fixa por categoria (gráficos empilhados por modelo, sem legenda: a cor identifica a categoria)
ESC_COLORS: dict[str, str] = {
    "Analfabeto": "#7A1F3D", "Lê/Escreve": "#B5485D", "Fund. Incomp.": "#D98A5F",
    "Fund. Comp.": "#E8C170", "Médio Incomp.": "#9CBF7B", "Médio Comp.": "#4E9F8D",
    "Sup. Incomp.": "#3C7DA6", "Sup. Comp.": "#2B4C7E",
}
AGE_COLORS: dict[str, str] = {
    "Jovem (16-24)": "#9AD1D4", "Adulto (25-44)": "#4F9DA6", "Meia-idade (45-59)": "#E9C46A",
    "Idoso (60-74)": "#E76F51", "Muito idoso (75+)": "#8C2F39",
}
ETAPA_COLORS: dict[str, str] = {
    "T. Fila": "#2B4C7E", "T. Autenticação": "#E9C46A", "T. Inatividade": "#B5485D",
}

BAIXA_ESC: list[str] = [
    "ESC_ANALFABETO", "ESC_LÊ E ESCREVE", "ESC_ENSINO FUNDAMENTAL INCOMPLETO",
]

GRUPOS_ETARIOS: dict[str, list[str]] = {
    "Jovem (16-24)": [
        "IDADE_16 anos", "IDADE_17 anos", "IDADE_18 anos",
        "IDADE_19 anos", "IDADE_20 anos", "IDADE_21 a 24 anos",
    ],
    "Adulto (25-44)": [
        "IDADE_25 a 29 anos", "IDADE_30 a 34 anos",
        "IDADE_35 a 39 anos", "IDADE_40 a 44 anos",
    ],
    "Meia-idade (45-59)": [
        "IDADE_45 a 49 anos", "IDADE_50 a 54 anos", "IDADE_55 a 59 anos",
    ],
    "Idoso (60-74)": [
        "IDADE_60 a 64 anos", "IDADE_65 a 69 anos", "IDADE_70 a 74 anos",
    ],
    "Muito idoso (75+)": [
        "IDADE_75 a 79 anos", "IDADE_80 a 84 anos", "IDADE_85 a 89 anos",
        "IDADE_90 a 94 anos", "IDADE_95 a 99 anos", "IDADE_100 anos ou mais",
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers de normalização de colunas
# ──────────────────────────────────────────────────────────────────────────────
def normalizar_colunas_zona_secao(df: pd.DataFrame) -> pd.DataFrame:
    cols_upper = {c.upper().strip().replace("  ", " "): c for c in df.columns}
    candidatos = {
        "NR_ZONA": ["NR_ZONA", "ZONA", "COD_ZONA", "CD_ZONA", "NUM_ZONA", "NR_ZONA_ELEITORAL", "ZONA_ELEITORAL"],
        "NR_SECAO": ["NR_SECAO", "SECAO", "COD_SECAO", "CD_SECAO", "NUM_SECAO", "SEÇÃO", "NR_SEÇÃO", "NR_SECAO_ELEITORAL", "SECAO_ELEITORAL", "SEÇÃO_ELEITORAL"],
    }
    renames = {}
    for padrao, alternativas in candidatos.items():
        if padrao in df.columns:
            continue
        for alt in alternativas:
            alt_norm = alt.upper().strip().replace("  ", "_")
            if alt_norm in cols_upper:
                renames[cols_upper[alt_norm]] = padrao
                break
    if renames:
        df = df.rename(columns=renames)
    
    if "NR_ZONA" not in df.columns:
        for c in df.columns:
            c_upper = c.upper().strip()
            if "ZON" in c_upper and ("NR" in c_upper or "NUM" in c_upper or "COD" in c_upper):
                df = df.rename(columns={c: "NR_ZONA"})
                break
            elif c_upper in ("ZONA", "ZONA_ELEITORAL"):
                df = df.rename(columns={c: "NR_ZONA"})
                break
    
    if "NR_SECAO" not in df.columns:
        for c in df.columns:
            c_upper = c.upper().strip()
            if "SEC" in c_upper and ("NR" in c_upper or "NUM" in c_upper or "COD" in c_upper):
                df = df.rename(columns={c: "NR_SECAO"})
                break
            elif c_upper in ("SECAO", "SEÇÃO", "SECAO_ELEITORAL", "SEÇÃO_ELEITORAL"):
                df = df.rename(columns={c: "NR_SECAO"})
                break
    
    if "NR_SECAO" not in df.columns:
        for c in df.columns:
            if "SEC" in c.upper():
                df = df.rename(columns={c: "NR_SECAO"})
                break
    
    if "NR_ZONA" not in df.columns:
        for c in df.columns:
            if "ZON" in c.upper():
                df = df.rename(columns={c: "NR_ZONA"})
                break
    
    return df

# ──────────────────────────────────────────────────────────────────────────────
# Classe principal
# ──────────────────────────────────────────────────────────────────────────────
class UrnasCriticasAnalysis:
    def __init__(
        self,
        path_consolidado: str,
        path_urnas_completas: str,
        status_filter: int | str | None = None,
        prefiltered: bool = False,
        total_secoes_override: int | None = None,
    ) -> None:
        df_2022 = pd.read_csv(path_consolidado, sep=",", encoding="utf-8", compression="zip")
        df_completas = pd.read_csv(path_urnas_completas, sep=";", encoding="utf-8", compression="zip")
        self.status_filter = status_filter
        self._total_secoes_override = total_secoes_override
        self._prepare(df_2022, df_completas, prefiltered=prefiltered)

    @classmethod
    def from_dataframes(
        cls,
        df_2022: pd.DataFrame,
        df_completas: pd.DataFrame,
        status_filter: int | str | None = None,
        prefiltered: bool = False,
        total_secoes_override: int | None = None,
    ) -> "UrnasCriticasAnalysis":
        obj = object.__new__(cls)
        obj.status_filter = status_filter
        obj._total_secoes_override = total_secoes_override
        obj._prepare(df_2022, df_completas, prefiltered=prefiltered)
        return obj

    def _prepare(
        self,
        df_2022: pd.DataFrame,
        df_completas: pd.DataFrame,
        prefiltered: bool = False,
    ) -> None:
        df_completas = normalizar_colunas_zona_secao(df_completas)
        df_2022 = normalizar_colunas_zona_secao(df_2022)
        
        if "NR_SECAO" not in df_completas.columns and "NR_ZONA" in df_completas.columns:
            df_completas["NR_SECAO"] = df_completas["NR_ZONA"].astype(str) + "_sec"
        
        if "NR_ZONA" in df_2022.columns and "zona" not in df_2022.columns:
            df_2022 = df_2022.rename(columns={"NR_ZONA": "zona", "NR_SECAO": "secao"})
        
        if "modelo" not in df_2022.columns and "MODELO_URNA" in df_2022.columns:
            df_2022 = df_2022.rename(columns={"MODELO_URNA": "modelo"})
        
        if prefiltered:
            df_criticas = df_completas.copy()
        else:
            if self.status_filter == FILTER_CONTINGENCIA:
                if "EH_URNA_CONTINGENCIA" in df_completas.columns:
                    df_criticas = df_completas[df_completas["EH_URNA_CONTINGENCIA"] == True].copy()
                else:
                    df_criticas = df_completas[df_completas["STATUS"] > 0].copy()
            elif isinstance(self.status_filter, str) or self.status_filter is None:
                df_criticas = df_completas[df_completas["STATUS"] > 0].copy()
            else:
                df_criticas = df_completas[df_completas["STATUS"] == self.status_filter].copy()
        
        idade_raw = [c for c in df_criticas.columns if c.startswith("IDADE_")]
        df_criticas = df_criticas.rename(columns={c: c.strip() for c in idade_raw})
        
        if "zona" not in df_2022.columns or "secao" not in df_2022.columns:
            raise KeyError("Colunas 'zona' ou 'secao' não encontradas em df_2022.")
        
        if "NR_ZONA" not in df_criticas.columns or "NR_SECAO" not in df_criticas.columns:
            raise KeyError("Colunas 'NR_ZONA' ou 'NR_SECAO' não encontradas em df_criticas.")
        
        def _priorizar_modelo_valido(df: pd.DataFrame) -> pd.DataFrame:
            modelo_valido = df["modelo"].notna() & (df["modelo"].astype(str).str.strip() != "")
            return (
                df.assign(_modelo_valido=modelo_valido)
                .sort_values("_modelo_valido", ascending=False)
                .drop_duplicates(subset=["zona", "secao"])
                .drop(columns="_modelo_valido")
            )
        
        df_modelo_secao = (
            _priorizar_modelo_valido(df_2022[["zona", "secao", "modelo"]])
            .rename(columns={"zona": "NR_ZONA", "secao": "NR_SECAO"})
        )
        
        df_criticas = df_criticas.merge(df_modelo_secao, on=["NR_ZONA", "NR_SECAO"], how="left")
        
        cols_available = [c for c in COLS_LOG if c in df_2022.columns]
        zs = df_criticas[["NR_ZONA", "NR_SECAO"]].rename(columns={"NR_ZONA": "zona", "NR_SECAO": "secao"})
        df_log = df_2022[cols_available].merge(zs, on=["zona", "secao"], how="inner")
        
        df_criticas_urnas = (
            _priorizar_modelo_valido(df_log)[["zona", "secao", "modelo"]]
            .reset_index(drop=True)
        )
        
        self.df_criticas = df_criticas
        self.df_log = df_log
        self.df_completas = df_completas
        
        self.models: dict[str, pd.DataFrame] = {
            m: df_criticas_urnas[df_criticas_urnas["modelo"] == m].reset_index(drop=True)
            for m in URN_MODELS
        }
        
        self.voters: dict[str, pd.DataFrame] = {
            m: df_log[df_log["modelo"] == m].reset_index(drop=True)
            for m in URN_MODELS
        }
        
        self.secao: dict[str, pd.DataFrame] = {
            m: df_criticas[df_criticas["modelo"] == m].reset_index(drop=True)
            for m in URN_MODELS
        }

    def get_overview(self) -> dict:
        total_secoes = (
            self._total_secoes_override
            if self._total_secoes_override is not None
            else len(self.df_completas)
        )
        status_counts = (
            self.df_completas["STATUS"]
            .value_counts()
            .sort_index()
            .rename(STATUS_LABELS)
            .to_dict()
        )
        return {
            "total_secoes_criticas": len(self.df_criticas),
            "total_secoes": total_secoes,
            "total_votantes": len(self.df_log),
            "modelos_presentes": [m for m in URN_MODELS if len(self.models[m]) > 0],
            "status_counts": status_counts,
        }

    def get_model_distribution(self) -> dict:
        counts = [len(self.models[m]) for m in URN_MODELS]
        total = sum(counts) or 1
        return {
            "models": URN_MODELS,
            "counts": counts,
            "proportions": [c / total for c in counts],
        }

    def get_bio_failure_rates(self) -> dict:
        rates = []
        for m in URN_MODELS:
            vm = self.voters[m]
            if "bio_solicitada" not in vm.columns or "n_falhas_bio" not in vm.columns:
                rates.append(0.0)
                continue
            bio_m = vm[vm["bio_solicitada"] == True]
            taxa = (bio_m["n_falhas_bio"] > 0).sum() / len(bio_m) if len(bio_m) else 0
            rates.append(taxa)
        return {"models": URN_MODELS, "rates": rates}

    def _get_mean_std_by_model(self, col: str) -> dict:
        means, stds = [], []
        for m in URN_MODELS:
            vm = self.voters[m]
            if col not in vm.columns:
                means.append(0.0)
                stds.append(0.0)
                continue
            d = vm[vm[col] > 0][col]
            means.append(float(d.mean()) if len(d) else 0.0)
            stds.append(float(d.std()) if len(d) else 0.0)
        return {"models": URN_MODELS, "means": means, "stds": stds}

    def get_queue_times(self) -> dict:
        return self._get_mean_std_by_model("t_fila_s")

    def get_auth_duration(self) -> dict:
        return self._get_mean_std_by_model("t_habilitacao_s")

    def get_inactivity_times(self) -> dict:
        return self._get_mean_std_by_model("t_inatividade_s")

    def get_invalid_keys(self) -> dict:
        if "n_teclas_inv" not in self.df_log.columns:
            return {"models": URN_MODELS, "proportions": [0.0] * len(URN_MODELS)}
        total_kp = self.df_log["n_teclas_inv"].sum()
        props = [
            self.voters[m][self.voters[m]["n_teclas_inv"] > 0]["n_teclas_inv"].sum() / total_kp
            if total_kp > 0 else 0
            for m in URN_MODELS
        ]
        return {"models": URN_MODELS, "proportions": props}

    def get_education_distribution(self) -> dict:
        esc_cols_available = [c for c in ESC_COLS if c in self.df_criticas.columns]
        df_esc = pd.DataFrame({m: self.secao[m][esc_cols_available].sum() for m in URN_MODELS}).T
        df_esc.columns = [ESC_LABELS.get(c, c) for c in esc_cols_available]
        df_esc_pct = df_esc.div(df_esc.sum(axis=1), axis=0)
        return {
            "df_counts": df_esc,
            "df_proportions": df_esc_pct,
            "models": URN_MODELS,
            "labels": list(df_esc.columns),
        }

    def get_low_education(self) -> dict:
        baixa_available = [c for c in BAIXA_ESC if c in self.df_criticas.columns]
        esc_available = [c for c in ESC_COLS if c in self.df_criticas.columns]
        props = []
        for m in URN_MODELS:
            sm = self.secao[m]
            tot = sm[esc_available].sum().sum()
            props.append(sm[baixa_available].sum().sum() / tot if tot else 0)
        return {"models": URN_MODELS, "proportions": props}

    def get_age_distribution(self) -> dict:
        df_idade = pd.DataFrame({
            m: {
                g: self.secao[m][[c for c in cols if c in self.secao[m].columns]].sum().sum()
                for g, cols in GRUPOS_ETARIOS.items()
            }
            for m in URN_MODELS
        }).T
        df_idade_pct = df_idade.div(df_idade.sum(axis=1), axis=0)
        return {
            "df_counts": df_idade,
            "df_proportions": df_idade_pct,
            "models": URN_MODELS,
            "groups": list(GRUPOS_ETARIOS.keys()),
        }

    def get_elderly_proportion(self) -> dict:
        age = self.get_age_distribution()
        df = age["df_proportions"]
        idoso_pct = (
            df.get("Idoso (60-74)", 0) + df.get("Muito idoso (75+)", 0)
        ).values.tolist()
        return {"models": URN_MODELS, "proportions": idoso_pct}

    def get_pcd_stats(self) -> dict:
        totals, eleitores, taxas = [], [], []
        for m in URN_MODELS:
            sm = self.secao[m]
            p = sm["QTD_PCD"].sum() if "QTD_PCD" in sm.columns else 0
            t = sm["QTD_PERFIL_BIOMETRIA"].sum() if "QTD_PERFIL_BIOMETRIA" in sm.columns else 0
            totals.append(int(p))
            eleitores.append(int(t))
            taxas.append(p / t if t else 0.0)
        return {"models": URN_MODELS, "totals": totals, "eleitores": eleitores, "taxas": taxas}

    def get_operational_summary(self) -> pd.DataFrame:
        bio = self.get_bio_failure_rates()
        fila = self.get_queue_times()
        auth = self.get_auth_duration()
        inat = self.get_inactivity_times()
        rows = []
        for i, m in enumerate(URN_MODELS):
            vm = self.voters[m]
            rows.append({
                "Modelo": m,
                "Seções": len(self.models[m]),
                "Votantes": len(vm),
                "Falha Bio (%)": round(bio["rates"][i] * 100, 1),
                "T. Fila (s)": round(fila["means"][i], 1),
                "T. Auth (s)": round(auth["means"][i], 1),
                "T. Inatividade (s)": round(inat["means"][i], 1),
            })
        return pd.DataFrame(rows)

    def get_pcd_summary(self) -> pd.DataFrame:
        pcd = self.get_pcd_stats()
        rows = [
            {
                "Modelo": m,
                "PCD Total": pcd["totals"][i],
                "Eleitores": pcd["eleitores"][i],
                "Taxa PCD (%)": round(pcd["taxas"][i] * 100, 2),
            }
            for i, m in enumerate(URN_MODELS)
        ]
        return pd.DataFrame(rows)
