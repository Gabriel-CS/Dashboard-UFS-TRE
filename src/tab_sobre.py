"""Aba informativa: o que o painel mostra, de onde vêm os dados e como ler cada análise."""
from __future__ import annotations
import streamlit as st
from src.analysis import FILTRO_DETALHES, STATUS_DETALHES, URN_MODELS
from src.ui_components import callout, legenda_filtros, legenda_status, section_header


def _titulo(texto: str, descricao: str = "") -> None:
    st.markdown(section_header(texto, descricao), unsafe_allow_html=True)


def _visao_geral() -> None:
    _titulo(
        "O que é este painel",
        "Uma leitura das urnas eletrônicas de Sergipe: onde a votação atrasou, o que aconteceu nessas seções e quais equipamentos e eleitores estavam envolvidos.",
    )
    st.markdown(
        """
**Pergunta que o painel responde.** Em quais seções eleitorais a votação atrasou, quanto atrasou, que tipo de ocorrência
consumiu tempo (biometria, inatividade, teclas indevidas, troca de urna) e se há relação com o modelo de urna ou com o perfil do eleitorado da seção.

**Eleições cobertas.** 2018, 2022 e 2026, 1º turno. Os arquivos de cada ano são baixados do Google Drive na primeira execução.

**Fonte dos dados.** Tribunal Superior Eleitoral (TSE), logs das urnas eletrônicas.

**Unidades de análise**
- **Seção eleitoral:** o grupo de eleitores que vota em uma mesma urna. É a unidade de todas as estatísticas.
- **Local de votação:** o endereço (escola, ginásio etc.) que abriga uma ou mais seções. É a unidade dos pontos no mapa.
- **Município:** usado para filtrar o mapa e para escolher a seção no estudo de caso.

**De onde vêm os números**
- Registros de funcionamento das urnas (logs), do Tribunal Superior Eleitoral: tempos de fila, habilitação, inatividade, falhas de biometria e teclas inválidas, ligados ao modelo da urna de cada seção.
- Tabelas por seção com o nível de atraso, as ocorrências, o perfil do eleitorado (faixa etária, escolaridade, eleitores com deficiência) e as coordenadas do local de votação.
- Ficha técnica de cada modelo de urna, exibida ao passar o mouse sobre os cartões da aba Modelos de urna.
        """
    )
    _titulo("Como usar")
    st.markdown(
        """
1. Na **barra de filtros**, logo abaixo do cabeçalho, escolha a **eleição** e o **nível de atraso**. A escolha vale para todas as abas de análise.
2. O **cabeçalho** resume o recorte: número de seções (e a fatia que representam no total do estado), votantes nessas seções,
   municípios envolvidos, o maior atraso registrado e os modelos de urna presentes.
3. Percorra as abas **Território**, **Criticidade** e **Modelos de urna**. Sob o título de cada gráfico há uma frase curta dizendo o que ele mostra.
4. Na aba Território, o painel **Recorte do mapa** tem um seletor de nível próprio. Ele começa igual ao da barra de filtros,
   mas pode ser alterado só para o mapa.
        """
    )
    st.markdown(
        callout(
            "<b>Cuidado ao interpretar.</b> O painel mostra <b>associações</b> entre atraso, modelo de urna e perfil do eleitorado. "
            "Ele não prova causa. O perfil do eleitorado é agregado por seção, então não é possível afirmar nada sobre indivíduos."
        ),
        unsafe_allow_html=True,
    )


def _niveis() -> None:
    _titulo(
        "Níveis de atraso e filtros",
        "Cada seção recebe um nível de 0 a 4 conforme o atraso registrado. Os filtros agrupados juntam vários níveis ou isolam um tipo de ocorrência.",
    )
    st.markdown(legenda_status(STATUS_DETALHES) + legenda_filtros(FILTRO_DETALHES), unsafe_allow_html=True)
    st.markdown(
        """
**Como ler.** O nível é a faixa de atraso da seção, em minutos, conforme a tabela acima. O nível 0 indica operação sem atraso
e o nível 1 indica atraso dentro da tolerância esperada. A partir do nível 2 a seção entra no recorte "Com atraso", e a partir do nível 3 em "Somente críticas".

**Cores.** Cada nível tem uma cor fixa, usada no mapa, nos gráficos e nos cartões: do azul (sem atraso) ao âmbar, laranja, vermelho e vinho (atraso extremo).
A urna de contingência usa roxo.
        """
    )


def _territorio() -> None:
    _titulo("Aba Território", "Onde estão os locais de votação afetados.")
    st.markdown(
        """
**O que o mapa mostra**
- Cada **ponto** é um local de votação. A **cor** é o maior nível de atraso entre as seções daquele local, e o **tamanho** cresce com o nível.
- Ao clicar em um ponto, abre-se a lista de seções do local, com zona, número da seção, nível, modelo da urna, atraso na fila,
  tempo de votação (do primeiro ao último voto) e indicação de urna de contingência.
- Ao clicar em um **município**, o mapa aproxima nele. Clicar de novo, ou no botão "Sergipe inteiro", volta à visão do estado.

**Controles do painel à direita**
- **Nível de atraso:** recorte do mapa (pode diferir do filtro lateral).
- **Municípios:** mostra só os municípios escolhidos.
- **Base do mapa:** fundo cinza (Esri) ou OpenStreetMap.
- **Agrupar locais próximos:** junta pontos vizinhos em círculos numerados. Vem desativado.
- **Tesselação de Voronoi:** divide o estado em células, uma por local, coloridas pelo nível. É uma aproximação geométrica da "área de influência"
  de cada ponto, recortada pelo contorno de Sergipe. Não representa áreas reais de atendimento. Exige ao menos 4 pontos.

**Resumo da seleção.** Mostra quantas seções e quantos locais há na seleção e a contagem por nível. Clicar em um nível filtra o mapa por ele, e é possível combinar vários.

**Limite.** Locais sem coordenadas válidas não aparecem no mapa, mas continuam nas demais abas.
        """
    )


def _criticidade() -> None:
    _titulo("Aba Criticidade", "O que aconteceu nas seções atrasadas.")
    st.markdown(
        """
Há um filtro opcional **Mostrar apenas urnas de contingência**, que isola as seções com troca de equipamento. A aba tem duas partes.

**1. Análise por nível de atraso**
- Com um **filtro agrupado** (Somente críticas, Com atraso, Contingência), compara os níveis entre si:
  média de **timeouts de biometria** (com o tempo médio perdido), média de **inatividade do eleitor**, média de **teclas indevidas**
  e a distribuição de **eleitores com deficiência (PCD)** entre os níveis.
- Com um **nível específico**, faz um diagnóstico: inatividade, timeout de biometria e teclas indevidas por seção, comparados com a **média estadual**.
  A variação percentual é calculada como (média do nível ÷ média estadual − 1). Acima da média aparece em vermelho.
  Abaixo estão o perfil por **faixa etária** e **escolaridade** dos eleitores e a proporção de PCD.
  A média estadual de referência é a das seções críticas do ano escolhido.

**2. Estudo de seção.** Escolha um município e uma seção (ordenadas da mais para a menos atrasada). O painel mostra:
- **Prontuário:** modelo da urna, posição no ranking de atraso, atraso na fila (contra a média do filtro), duração da votação,
  número de eleitores e de eleitores PCD.
- **Resumo:** qual evento mais consumiu tempo e quantas vezes a média do filtro isso representa.
- **Contingência:** se houve troca de urna, os modelos envolvidos, horários, duração do procedimento, tempo total de troca e alerta de pareamento suspeito.
- **Onde o tempo foi perdido:** tempo acumulado em timeout de biometria, inatividade e teclas indevidas, comparado com a média do filtro.
- **Perfil dos eleitores:** percentual por faixa etária e escolaridade, na seção e na média do filtro.
        """
    )


def _modelos() -> None:
    _titulo("Aba Modelos de urna", "Como cada modelo se comporta nas seções do recorte.")
    st.markdown(
        f"""
Modelos considerados: **{", ".join(URN_MODELS)}**. Cada um tem uma cor fixa. Os cartões do topo mostram seções e votantes por modelo,
e a ficha técnica aparece ao passar o mouse.

**Composição dos modelos**
- Quantidade de seções atendidas por cada modelo e seu percentual no total.

**Desempenho operacional**
- **Composição do tempo médio por eleitor:** soma das médias de fila, autenticação (habilitação) e inatividade, em segundos.
  As médias consideram apenas valores maiores que zero.
- **Representatividade do tempo (%):** fatia de cada modelo no tempo operacional total.
- **Taxa de falha biométrica:** votantes com ao menos uma falha, entre os que tiveram biometria solicitada. A linha tracejada é a média dos modelos.
- **Concentração das falhas:** quanto de todas as falhas cada modelo concentra.
- **Inatividade (média ± desvio padrão):** o desvio padrão indica o quanto os tempos variam em torno da média.
- **Teclas indevidas:** quantidade de teclas inválidas por modelo e a fatia que cada um concentra do total.

**Perfil do eleitorado**
- **Escolaridade e faixa etária (%):** cada barra soma 100% e mostra como os eleitores de cada modelo se distribuem.
  Nesses gráficos cada categoria tem cor fixa e o valor aparece ao passar o mouse.
- **Baixa escolaridade:** analfabetos, quem lê e escreve e quem tem fundamental incompleto, sobre o total do modelo.
- **Idosos (60 anos ou mais):** faixas de 60 a 74 e de 75 em diante, sobre o total do modelo.
- **PCD:** total de eleitores com deficiência por modelo e a taxa, dividida pelo total de eleitores do perfil da seção.

**Para comparar modelos.** Modelos com poucas seções têm médias instáveis. Olhe o número de seções antes de concluir qualquer coisa.
        """
    )


def _glossario() -> None:
    _titulo("Glossário e limites")
    st.markdown(
        """
**Glossário**
- **Seção eleitoral:** conjunto de eleitores que votam na mesma urna.
- **Zona eleitoral:** divisão da Justiça Eleitoral que agrupa seções. A seção é identificada pela zona e pelo número.
- **Urna de contingência:** urna reserva que substitui a original quando ela falha, ou que opera desde o início da votação.
- **Atraso na fila:** atraso registrado na seção, em minutos. Define o nível.
- **Timeout de biometria:** a leitura biométrica excedeu o tempo previsto.
- **Inatividade:** tempo em que o eleitor fica parado na urna.
- **Tecla indevida:** tecla inválida digitada na urna.
- **PCD:** pessoa com deficiência.
- **UE2009 … UE2022:** modelos de urna eletrônica, identificados pelo ano.
- **Desvio padrão (DP):** medida de dispersão dos valores em torno da média.

**Limites e cuidados**
- Os gráficos por modelo só incluem seções com modelo identificado.
- As médias de tempo de fila, autenticação e inatividade excluem valores iguais a zero.
- A média estadual do diagnóstico por nível usa as seções críticas, não todas as seções do estado.
- A tesselação de Voronoi é um recurso visual, não uma área oficial de atendimento.
- Associação não é causa. Uma diferença entre modelos pode refletir onde cada modelo foi usado (por exemplo, municípios ou locais diferentes), e não o equipamento em si.
- O perfil do eleitorado é da seção inteira, não de quem teve atraso.
        """
    )


def render_tab_sobre() -> None:
    (t_visao, t_niveis, t_terr, t_crit, t_mod, t_gloss) = st.tabs([
        "Visão geral", "Níveis e filtros", "Território", "Criticidade", "Modelos de urna", "Glossário e limites",
    ])
    with t_visao:
        _visao_geral()
    with t_niveis:
        _niveis()
    with t_terr:
        _territorio()
    with t_crit:
        _criticidade()
    with t_mod:
        _modelos()
    with t_gloss:
        _glossario()