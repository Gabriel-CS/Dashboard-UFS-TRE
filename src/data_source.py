"""Acesso a dados: configuração de caminhos, download do Drive e leitores com cache."""
from __future__ import annotations

import os
import time

import gdown
import pandas as pd
import streamlit as st

from src.analysis import FILTER_COM_ATRASO, FILTER_SOMENTE_CRITICAS

def nivel_key(status_filter):
    return FILTER_SOMENTE_CRITICAS if status_filter is None else status_filter


_ANOS = ("2018", "2022", "2026")

_NIVEIS_TPL = {
    FILTER_SOMENTE_CRITICAS: "urnas_criticas_{a}_1t.csv",
    FILTER_COM_ATRASO:       "urnas_com_atraso_{a}_1t.csv",
    **{n: f"urnas_status_{n}_{{a}}_1t.csv" for n in range(5)},
}
_MODELOS_TPL = {
    FILTER_SOMENTE_CRITICAS: "df_somente_criticas_{a}.zip",
    FILTER_COM_ATRASO:       "df_com_atraso_{a}.zip",
    **{n: f"df_completas_n{n}_{{a}}.zip" for n in range(5)},
}


def _build_config(ano: str) -> dict:
    p = lambda grupo, tpl: f"data/output/{ano}/{grupo}/{tpl.format(a=ano)}"
    return {
        "niveis":        {k: p("por_status", t) for k, t in _NIVEIS_TPL.items()},
        "modelos_urnas": {k: p("modelos_urnas", t) for k, t in _MODELOS_TPL.items()},
        "contingencia":  p("por_status", "urnas_contingencia_{a}.csv"),
    }


DATA_CONFIG = {a: _build_config(a) for a in _ANOS}


# ── IDs do Google Drive: nome do arquivo → file_id, por ano ────────────────────
# O caminho local NÃO é repetido aqui: sai de DATA_CONFIG (fonte única).
_DRIVE_IDS: dict[str, dict[str, str]] = {
    "2018": {
        "urnas_criticas_2018_1t.csv":   "1BA9-Or_bpb1LyF9aEqMaZ6r0pLbRlhm7",
        "urnas_com_atraso_2018_1t.csv": "1vOz3M5yOuXpgfwi49PiI_5LO7DdGQxws",
        "urnas_status_0_2018_1t.csv":   "1K6KuMoKG9-1z2ndzwebpYILoPEW5ClG8",
        "urnas_status_1_2018_1t.csv":   "1R5rsrCY5WO2dbNytjEaLCvYOLZUXhN6f",
        "urnas_status_2_2018_1t.csv":   "1D70Qr5ACoVo-Wmo_MbRStv7iCASTjshd",
        "urnas_status_3_2018_1t.csv":   "1usp4G9yY1R3uIfZ5tbiH3IO90QA03LQ2",
        "urnas_status_4_2018_1t.csv":   "1DbTNQjYFHEVjIcCQP0anDswDtLhAgTZH",
        "urnas_contingencia_2018.csv":  "1Cjlujls9MuJFoqbZ36NYrxoyoB7nAa_R",
        "df_somente_criticas_2018.zip": "1pJH33pfId2DOSKPAR6Psvf7NFIa_Pu9t",
        "df_com_atraso_2018.zip":       "1sTPFowwBcnZ6mZeIS1NRufriCblwRxlk",
        "df_completas_n0_2018.zip":     "1Wy8X1lcDwYBLLNArd2NaomRCJiMa-BGJ",
        "df_completas_n1_2018.zip":     "1cptbA6bQQhhiQfLLRwN0f0kL9dIjaAx0",
        "df_completas_n2_2018.zip":     "1qdkUrv2gAsl6anICVsuUj6dpXLLGYLye",
        "df_completas_n3_2018.zip":     "1A5_4O_Lv3VXrcvxrLqTUxu0AhJwtUIAT",
        "df_completas_n4_2018.zip":     "1kFg3mBXgLfJizfnAr1fKaU0sfgy9n4pS",
    },
    "2022": {
        "urnas_criticas_2022_1t.csv":   "1Jj6wloqWoT1Kmvvqy5IVr5etl3W07Zix",
        "urnas_com_atraso_2022_1t.csv": "1fcUiEMZjsY6sT5Xb_OUEUX1yUS26JmdT",
        "urnas_status_0_2022_1t.csv":   "1fdZ3-aldWOaYquEDByeETRzncddK6YFv",
        "urnas_status_1_2022_1t.csv":   "1M5qi99ozcIiH-b6dYEY8aW0QFSNXZL_G",
        "urnas_status_2_2022_1t.csv":   "1g3PB6_w3IcSO5d-NBWsvHwmwcFP4hT5l",
        "urnas_status_3_2022_1t.csv":   "1gfrMr0NRWujToXc1n9_EqJscgPjuuyNT",
        "urnas_status_4_2022_1t.csv":   "1AvFF0tV0Ews5WFMijn6ECZ8af-iaSSJV",
        "urnas_contingencia_2022.csv":  "1zKfiVOtn-CKdPp1Yq_S8w34oeGyDIKTC",
        "df_somente_criticas_2022.zip": "1LRMPFX5dXX80Bwfq5Tfv_ohcVYi-4Y6r",
        "df_com_atraso_2022.zip":       "1kn3a9JpHcQwq31V0L6ja-iesh_qXmOOb",
        "df_completas_n0_2022.zip":     "1zaos2fFT2znQ_Jx8YWQBQDaEpWlua1bU",
        "df_completas_n1_2022.zip":     "1Uqf64CWc_C1ztNMYMu615UMKokTa3__I",
        "df_completas_n2_2022.zip":     "156RJ6iHyDPMloWY1ksQOLNUct8v307LO",
        "df_completas_n3_2022.zip":     "1z7GyYvf_3FZXjrwIT8O8Mnn0YWxeL-q9",
        "df_completas_n4_2022.zip":     "1ze4KpuChipazFTC0YvqHRfnXqbVLNa5I",
    },
    "2026": {
        "urnas_criticas_2026_1t.csv":   "1_qkrn5Y_pMmRF271dbYwUvJ2Jct4AOF-",
        "urnas_com_atraso_2026_1t.csv": "14uQjx9HCJK_IpOBhkPEVVfz8uP_aWAPC",
        "urnas_status_0_2026_1t.csv":   "1fNRQmBmS8XraSjh4UymcUQcWdCuo0uJe",
        "urnas_status_1_2026_1t.csv":   "1ZPNSgjDbCydZEl-3Tpt4FVo_KXdBm15b",
        "urnas_status_2_2026_1t.csv":   "1mFVIbTROo4ibttwIQkThkSY6XK1zqXqT",
        "urnas_status_3_2026_1t.csv":   "1GoPRNtBcBj5YdpM-t5dBCwOmaTf0SX_a",
        "urnas_status_4_2026_1t.csv":   "1_NE5Wa_CPCtY2XqQSvqDGSn8FjUcTHck",
        "urnas_contingencia_2026.csv":  "1JsHXMU-ckQKU3nIecUKMRUcBhMpus-1w",
        "df_somente_criticas_2026.zip": "1owUx9Qgwc5PRx7kb9NYR1JqviOOvf82M",
        "df_com_atraso_2026.zip":       "1EmtWGhIlCLVoXb84y2p4dfSXGSCjky-x",
        "df_completas_n0_2026.zip":     "1hYBkn58zL1_ti1WwF-v8JbY09iQ3j6Xb",
        "df_completas_n1_2026.zip":     "1PdIx-aoYSMzzo57Fc-3N5u6lBAeM3hzV",
        "df_completas_n2_2026.zip":     "1vmA71Bxj4b2uZj_r_kiPfVYT6hGKOmuf",
        "df_completas_n3_2026.zip":     "1QRG8Jqi5yjROd-o3pXLnyH0UR_rg-Lox",
        "df_completas_n4_2026.zip":     "1yDlLD5i863pEkg9yNrtnwoiIG-txmTS3",
    },
}

# Arquivos fora de DATA_CONFIG (consumidos por src/tab_geo e afins): caminho local → file_id
_EXTRA_FILES: dict[str, str] = {
    "data/datasets/Tabela_Configuracoes.csv": "1uOjGX6_R1_K-4CAzpUOpPLOCAXsPNeyi",
    "data/data_map/locais_criticos_2018.csv": "1iF7z5XdT9z87KyBBjgWFgMCJme5Wxy_Y",
    "data/data_map/locais_criticos_2022.csv": "1Wgplr9uaoWvnTu0hOAuQHOcYT_a4NxqL",
    "data/data_map/locais_criticos_2026.csv": "1TOG8kCKn6wWDSStmy7Yy5pIKDUEt5qKr",
    "data/data_map/locais_votacao_consolidado_sc_2018.csv": "1UWOp94666A6Em0nmIVE8friHIt5a7TVs",
    "data/data_map/locais_votacao_consolidado_sc_2022.csv": "1Ct58xa2usohCRJT915tRYhS5ShyyKwM0",
    "data/data_map/locais_votacao_consolidado_sc_2026.csv": "1XV924an6Q4O-Wt4EYpTwzLGTa_FgGm-9",
    "data/data_map/df_locais_somente_criticos_2018.csv": "1VF39OJon8xW0O5sQlbbNUPN4Iezpw6In",
    "data/data_map/df_locais_somente_criticos_2022.csv": "1X6MND3vNeyEWxdqcCW_HjYSPRWjjotwx",
    "data/data_map/df_locais_com_atraso_2018.csv": "1Gclxcm5tQWypMBvwZvvs-8QvGziUXB4U",
    "data/data_map/df_locais_com_atraso_2022.csv": "19n5Q8zhjvyTHSZM0Y2cZ6t-pvrXZNuIR",
    "data/data_map/df_locais_votacao_consolidado_somente_criticos_2018.csv": "1b1injUtqPhX2_wlKXer_RpBrydY2guP-",
    "data/data_map/df_locais_votacao_consolidado_somente_criticos_2022.csv": "1B1-g9b_Dr5adrL-9_JndmPKLUroHuCHu",
    "data/data_map/df_locais_votacao_consolidado_com_atraso_2018.csv": "1BNGFKgNIRI5w9Vxb9BU2-3bShKX3n3We",
    "data/data_map/df_locais_votacao_consolidado_com_atraso_2022.csv": "1Alj1AInoY021eUgthx1_z2rYiO21OmWj",
}


def _config_paths(cfg: dict):
    yield from cfg["niveis"].values()
    yield from cfg["modelos_urnas"].values()
    yield cfg["contingencia"]


# Falha no import (e não no meio de uma sessão) se algum caminho de DATA_CONFIG não tiver ID.
_DRIVE_FILES: dict[str, str] = {
    **{
        p: _DRIVE_IDS[ano][os.path.basename(p)]
        for ano, cfg in DATA_CONFIG.items()
        for p in _config_paths(cfg)
    },
    **_EXTRA_FILES,
}


def _is_valid_download(local_path: str) -> bool:
    """
    Confirma que o arquivo baixado é real e não uma página de erro/aviso do
    Drive (quota excedida, permissão negada, tela de vírus não reconhecida
    etc.) salva por engano com extensão .csv/.zip. Verifica tamanho mínimo e,
    para não-zip, que o conteúdo não começa com marcação HTML.
    """
    if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
        return False
    if local_path.endswith(".zip"):
        import zipfile
        return zipfile.is_zipfile(local_path)
    with open(local_path, "rb") as f:
        head = f.read(512).lstrip().lower()
    return not head.startswith(b"<!doctype") and not head.startswith(b"<html")


def _download_file(local_path: str, file_id: str) -> None:
    """
    Baixa um único arquivo do Google Drive via gdown, que já lida
    corretamente com a tela de confirmação de vírus/tamanho do Drive
    (diferentes formatos, incluindo os mais recentes baseados em cookie),
    ao contrário de um scraping manual com regex fixo.
    """
    if os.path.exists(local_path) and _is_valid_download(local_path):
        return

    # Se existir um arquivo inválido (ex.: HTML de erro salvo em tentativa
    # anterior), remove antes de tentar de novo.
    if os.path.exists(local_path):
        os.remove(local_path)

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    ultima_excecao: Exception | None = None
    for tentativa in range(1, 4):  # até 3 tentativas — cobre falhas transitórias/rate limit
        try:
            try:
                gdown.download(id=file_id, output=local_path, quiet=True, fuzzy=True)
            except TypeError:
                # Versões mais antigas do gdown (<4.6) não têm o parâmetro
                # 'fuzzy'. 'fuzzy' só é necessário quando se passa uma URL
                # completa do Drive; como aqui já usamos 'id' diretamente,
                # é seguro cair para a chamada sem esse argumento.
                gdown.download(id=file_id, output=local_path, quiet=True)
            if _is_valid_download(local_path):
                return
            raise RuntimeError(
                "conteúdo baixado não parece ser o arquivo esperado "
                "(possível página de erro/quota do Google Drive)"
            )
        except Exception as exc:  # noqa: BLE001 — queremos tentar de novo e reportar no fim
            ultima_excecao = exc
            if os.path.exists(local_path):
                os.remove(local_path)
            time.sleep(2 * tentativa)  # backoff simples entre tentativas

    raise RuntimeError(f"falha após 3 tentativas ({ultima_excecao})") from ultima_excecao


@st.cache_resource(show_spinner=False)
def _download_and_extract_data() -> list[str]:
    """
    Baixa sob demanda apenas os arquivos ainda ausentes/inválidos.
    Cada arquivo é baixado diretamente ao seu caminho final — sem zip global.

    IMPORTANTE: esta função NUNCA chama st.stop() — funções decoradas com
    @st.cache_resource devem sempre completar e *retornar* um valor. Parar a
    execução no meio pode fazer o Streamlit tratar a chamada como concluída
    sem cachear um resultado consistente, mascarando falhas em reruns
    seguintes. Quem decide o que fazer com os erros é o chamador, fora do
    cache.
    """
    arquivos_faltando = [
        p for p in _DRIVE_FILES if not (os.path.exists(p) and _is_valid_download(p))
    ]
    if not arquivos_faltando:
        return []

    erros: list[str] = []
    with st.spinner("Preparando o sistema pela primeira vez. Isso pode levar alguns instantes…"):
        for local_path in arquivos_faltando:
            file_id = _DRIVE_FILES[local_path]
            nome    = os.path.basename(local_path)
            try:
                _download_file(local_path, file_id)
            except Exception as exc:
                erros.append(f"{nome}: {exc}")

    return erros


def baixar_dados_ausentes() -> list[str]:
    """Garante os arquivos locais; devolve a lista de erros (vazia se tudo certo)."""
    return _download_and_extract_data()


@st.cache_data(show_spinner=False, max_entries=2, ttl=300)
def load_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, sep=",", encoding="utf-8")
        if len(df.columns) <= 1:
            raise ValueError("Possivelmente separador incorreto")
    except Exception:
        df = pd.read_csv(path, sep=";", encoding="utf-8")
    df.columns = df.columns.str.strip()
    return df


@st.cache_data(show_spinner=False, max_entries=4, ttl=1800)
def count_rows(path: str) -> int:
    """
    Conta linhas de um CSV sem parsear o conteúdo — apenas itera bytes
    contando newlines. Bem mais rápido e barato em memória do que
    `pd.read_csv(usecols=[0])` para arquivos grandes (uso típico: 30 MB+).
    """
    try:
        # encoding fallback — a maioria dos CSVs do projeto é UTF-8,
        # mas alguns vêm com BOM ou Latin-1. Em caso de erro, recorre
        # ao pandas (lento mas robusto).
        with open(path, "rb") as f:
            # -1 porque a última linha pode ou não ter newline;
            # Somamos 1 se o arquivo não terminar em newline.
            count = sum(buf.count(b"\n") for buf in iter(lambda: f.read(1024 * 1024), b""))
        # Se o arquivo não termina em \n, há uma linha extra.
        # Verifica o último byte de forma barata.
        with open(path, "rb") as f:
            try:
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    count += 1
            except OSError:
                # Arquivo vazio ou muito pequeno — mantém count como está
                pass
        # Subtrai 1 do cabeçalho (primeira linha), garantindo >= 0.
        return max(count - 1, 0)
    except Exception:
        # Fallback: método anterior (lê a 1ª coluna com pandas).
        try:
            df = pd.read_csv(path, sep=",", encoding="utf-8", usecols=[0])
            return len(df)
        except Exception:
            return 0


@st.cache_data(show_spinner=False, max_entries=2, ttl=600)
def load_estado_means(nivel_all_path: str) -> dict[str, float]:
    cols = ["TIMEOUT_BIOMETRIA", "INATIVIDADE", "TECLA_INDEVIDA"]
    try:
        df = pd.read_csv(nivel_all_path, sep=";", encoding="utf-8", usecols=cols)
        return {c: float(df[c].mean()) for c in cols}
    except Exception:
        return {}


_EVENTOS_COLS = {
    "TIMEOUT_BIOMETRIA": "TPBSEC",
    "INATIVIDADE": "TTPISEC",
    "TECLA_INDEVIDA": "TEMPO_TECLA_INDEVIDA_SEG",
}

def _ler_colunas(path: str, cols: list[str], prefixos: tuple = ()) -> pd.DataFrame:
    """Lê só `cols` (e colunas que comecem por `prefixos`), tentando "," e ";"."""
    alvo = set(cols)
    for sep in (",", ";"):
        try:
            df = pd.read_csv(
                path, sep=sep, encoding="utf-8",
                usecols=lambda c: c.strip() in alvo or c.strip().startswith(prefixos),
            )
        except Exception:
            continue
        if df.shape[1] > 0:
            df.columns = df.columns.str.strip()
            return df
    return pd.DataFrame()

@st.cache_data(show_spinner=False, max_entries=2, ttl=1800)
def load_estado_totais(paths: tuple) -> dict:
    """
    Totais do estado por evento: soma e média por seção de ocorrências e de tempo (s).
    `paths` deve ser o mesmo conjunto usado em total_secoes_global (app.py).
    Retorno: {"n_secoes": int, COL_OCORR: {"o_tot","o_med","t_tot","t_med"}}.
    """
    cols = list(_EVENTOS_COLS) + list(_EVENTOS_COLS.values())
    partes = [d for d in (_ler_colunas(p, cols) for p in paths) if not d.empty]
    if not partes:
        return {}
    df = pd.concat(partes, ignore_index=True)
    nan = float("nan")
    out: dict = {"n_secoes": int(len(df))}
    for c_o, c_t in _EVENTOS_COLS.items():
        o = pd.to_numeric(df[c_o], errors="coerce") if c_o in df.columns else None
        t = pd.to_numeric(df[c_t], errors="coerce") if c_t in df.columns else None
        out[c_o] = {
            "o_tot": float(o.sum()) if o is not None else nan,
            "o_med": float(o.mean()) if o is not None else nan,
            "t_tot": float(t.sum()) if t is not None else nan,
            "t_med": float(t.mean()) if t is not None else nan,
        }
    return out

_COLS_EXPORT = [
    "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "STATUS", "ATRASO_FILA_MINUTOS",
    "modelo", "MODELO_URNA_PRINCIPAL", "MODELO_URNA", "MODELO_URNA_PAR_CONTINGENCIA", "URNA_ID",
    "HOUVE_TROCA_POR_CONTINGENCIA", "EH_URNA_CONTINGENCIA",
    "TEMPO_SECAO_PRIMEIRO_ULTIMO_VOTO_SEG", "PRIMEIRO_VOTO", "ULTIMO_VOTO", "QTD_PCD",
    *_EVENTOS_COLS, *_EVENTOS_COLS.values(),
]


@st.cache_data(show_spinner=False, max_entries=2, ttl=1800)
def load_todas_secoes(paths: tuple) -> pd.DataFrame:
    """
    Todas as seções do ano (CSVs de urnas completas), só com as colunas da exportação.
    `paths` é o mesmo conjunto de total_secoes_global (app.py). Seções repetidas entre
    arquivos (mesma zona e seção) entram uma única vez.
    """
    partes = [d for d in (_ler_colunas(p, _COLS_EXPORT, prefixos=("IDADE_",)) for p in paths) if not d.empty]
    if not partes:
        return pd.DataFrame()
    df = pd.concat(partes, ignore_index=True)
    if {"NR_ZONA", "NR_SECAO"} <= set(df.columns):
        df = df.drop_duplicates(subset=["NR_ZONA", "NR_SECAO"], keep="first")
    return df.reset_index(drop=True)
