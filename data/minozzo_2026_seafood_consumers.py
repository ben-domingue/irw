#!/usr/bin/env python3
# Source: https://zenodo.org/records/22284893
# DOI: 10.5281/zenodo.22284893 (data)
#   Minozzo Giordani M (2026). Data and Code for: "Psychographic Segmentation of Seafood Consumers: Purchase Intention, Stated Willingness to Pay, and the Health-Sustainability Divide" [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22284893
# License: CC BY 4.0 (record metadata)
# Data: amostra_calibracao.xlsx (309) + amostra_validacao.xlsx (314), 623 Brazilian adults (Google Forms). Supplementary Table S1
#   gives each item's code, construct, Portuguese wording, English translation and retention status. Items 1-7.
# Tables: one per Table S1 construct, keeping items the authors later dropped in the construct they were written for; the three
#   "n/a (dropped)" items go to sustainability, involvement and purchase intention by wording; plus the 7 unlisted barrier items.
# Covariates: sample, age band, sex, education, income band, seafood frequency, coastal municipality, purchase-decision role, main form.
# Dropped: consent text, eligibility screens, region/state/municipality (geographic), multi-select place/species lists.
# PII: none.
# Item text: Portuguese wording + English translation for 48 items in Supplementary Table S1 (cheap later build).
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/22284893/files/amostra_calibracao.xlsx/content'
N_ROWS = 623
ID_COL = None
COVS = {'Qual sua idade?': 'cov_age_band',
 'Qual seu sexo?': 'cov_sex',
 'Qual seu maior nível de escolaridade?': 'cov_education',
 'Qual sua renda familiar mensal aproximada?': 'cov_income_band',
 'Com que frequência você consome pescado': 'cov_seafood_freq',
 'Você reside em município litorâneo?': 'cov_coastal_municipality',
 'Você participa das decisões de compra de alimentos no seu domicílio?': 'cov_food_purchase_decisions',
 'Qual forma de pescado você mais consome?': 'cov_main_form',
 'sample': 'cov_sample'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'minozzo_2026_sensory_cues': ['frescor', 'aparencia', 'odor'],
 'minozzo_2026_perceived_risk': ['dif_frescor', 'receio_contam', 'receio_especie', 'dif_especie'],
 'minozzo_2026_channel_trust': ['confia_super', 'confia_peixaria', 'confia_feira', 'acredita_temp'],
 'minozzo_2026_certification_trust': ['selo', 'origem_intencao_qual', 'confia_rotulo'],
 'minozzo_2026_perceived_health_benefit': ['saude_proteica', 'omega3', 'saude_regular', 'info_suficiente'],
 'minozzo_2026_sustainability': ['aquicultura_sustentavel',
                                 'origem_sustent',
                                 'impacto_ambiental',
                                 'disposto_impacto'],
 'minozzo_2026_convenience': ['pronto_preparo', 'sem_espinhas', 'facilidade_preparo', 'evita_demorado'],
 'minozzo_2026_involvement': ['conhecer_alimentos',
                              'participar_preparo',
                              'interesse_experimentar_novos',
                              'busca_info'],
 'minozzo_2026_processed_acceptance': ['aceita_hamburguer',
                                       'aceita_linguica',
                                       'aceita_pate',
                                       'aceita_nuggets',
                                       'aceita_snacks',
                                       'aceita_congelados'],
 'minozzo_2026_processing_skepticism': ['tech_positivo', 'tech_receio', 'tech_ingredientes', 'tech_prefere_fresco'],
 'minozzo_2026_purchase_intention': ['intencao_30dias',
                                     'intencao_aumentar',
                                     'intencao_recomendaria',
                                     'intencao_experimentar'],
 'minozzo_2026_wtp': ['paga_rastreavel', 'paga_selo', 'paga_sem_espinhas', 'paga_sustentavel'],
 'minozzo_2026_barriers': ['barreira_1',
                           'barreira_2',
                           'barreira_3',
                           'barreira_4',
                           'barreira_5',
                           'barreira_6',
                           'barreira_7']}
# (lo, hi) response range per table
RANGES = {'minozzo_2026_sensory_cues': (1, 7),
 'minozzo_2026_perceived_risk': (1, 7),
 'minozzo_2026_channel_trust': (1, 7),
 'minozzo_2026_certification_trust': (1, 7),
 'minozzo_2026_perceived_health_benefit': (1, 7),
 'minozzo_2026_sustainability': (1, 7),
 'minozzo_2026_convenience': (1, 7),
 'minozzo_2026_involvement': (1, 7),
 'minozzo_2026_processed_acceptance': (1, 7),
 'minozzo_2026_processing_skepticism': (1, 7),
 'minozzo_2026_purchase_intention': (1, 7),
 'minozzo_2026_wtp': (1, 7),
 'minozzo_2026_barriers': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'TERMO DE CONSENTIMENTO LIVRE E ESCLARECIDO (TCLE)_x000D_\n_x000D_\nTítulo da pesquisa:_x000D_\nPerfil e comportamento do consumidor brasileiro de pescado_x000D_\n_x000D_\nVocê está sendo convidado(a) a participar de uma pesquisa científica desenvolvida por pesquisadores do Grupo de Estudos em Processamento de Pescado (GEPP), vinculado ao Instituto Federal do Espírito Santo (IFES) – Campus Piúma._x000D_\n_x000D_\nO objetivo desta pesquisa é compreender o perfil e o comportamento do consumidor brasileiro de pescado, incluindo hábitos de consumo, percepção de qualidade, confiança sanitária e aceitação de produtos processados à base de pescado._x000D_\n_x000D_\nA participação ocorrerá por meio do preenchimento de um questionário on-line, disponibilizado pela plataforma Google Forms®, com duração aproximada de 5 a 8 minutos._x000D_\n_x000D_\nA participação é voluntária e não haverá qualquer pagamento ou benefício financeiro pela participação._x000D_\n_x000D_\nNão serão solicitadas informações que permitam identificação pessoal direta dos participantes. Os dados obtidos serão utilizados exclusivamente para fins científicos e acadêmicos, sendo analisados de forma agrupada e confidencial._x000D_\n_x000D_\nOs riscos da pesquisa são mínimos e podem incluir eventual desconforto ao responder perguntas relacionadas a hábitos alimentares e percepções pessoais. O participante poderá interromper o preenchimento do questionário a qualquer momento, sem qualquer prejuízo._x000D_\n_x000D_\nOs resultados da pesquisa poderão contribuir para o desenvolvimento científico e tecnológico da área de pescado, além de auxiliar no desenvolvimento de estratégias voltadas ao aumento do consumo de pescado e ao aprimoramento de produtos destinados ao consumidor brasileiro._x000D_\n_x000D_\nEm caso de dúvidas sobre a pesquisa, os participantes poderão entrar em contato com os pesquisadores responsáveis por meio dos canais institucionais informados no projeto._x000D_\n_x000D_\nAo selecionar a opção “Sim, aceito participar”, o participante manifesta livremente seu consentimento para participação na pesquisa.': 'consent '
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                'text '
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                '(constant)',
 'Você possui 18 anos ou mais?': 'eligibility (constant yes)',
 'Você reside atualmente no Brasil?': 'eligibility (constant yes)',
 'Em qual região do Brasil você reside?': 'region (geographic)',
 'Em qual estado você reside?': 'state (geographic)',
 'Informe o município onde reside.': 'municipality (geographic)',
 'Onde você costuma comprar pescado?': 'multi-select purchase places',
 'Onde você costuma consumir pescado?': 'multi-select consumption places',
 'Quais espécies você consome com maior frequência?': 'multi-select species'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """calibration (this URL) + validation sample (amostra_validacao.xlsx), same Google Form; item = Table S1 code (barreira_k for
    the seven barrier statements Table S1 does not list), matched on the bracketed Portuguese wording of each header"""
    r = requests.get('https://zenodo.org/api/records/22284893/files/amostra_validacao.xlsx/content', timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    e = pd.read_excel(io.BytesIO(r.content))
    e.columns = [str(c).strip() for c in e.columns]
    assert list(e.columns) == list(d.columns)
    d["sample"] = "calibration"
    e["sample"] = "validation"
    d = pd.concat([d, e], ignore_index=True).rename(columns={'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [O frescor é o principal critério que utilizo para decidir comprar pescado.]': 'frescor', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [A aparência do pescado influencia minha decisão de compra.]': 'aparencia', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [O odor do pescado é decisivo para minha percepção de qualidade.]': 'odor', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Tenho dificuldade para avaliar se um pescado está realmente fresco.]': 'dif_frescor', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Confio na qualidade sanitária do pescado vendido em supermercados.]': 'confia_super', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Confio na qualidade sanitária do pescado vendido em peixarias.]': 'confia_peixaria', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Confio na qualidade sanitária do pescado vendido em feiras livres.]': 'confia_feira', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [A presença de selo de inspeção aumenta minha confiança no pescado.]': 'selo', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Acredito que o pescado vendido no comércio mantém temperatura adequada até a venda.]': 'acredita_temp', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Tenho receio de comprar pescado por medo de contaminação microbiológica.]': 'receio_contam', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Tenho receio de comprar uma espécie diferente da informada no rótulo ou pelo vendedor.]': 'receio_especie', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Considero difícil saber se o pescado corresponde realmente à espécie anunciada.]': 'dif_especie', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [A informação sobre origem do pescado aumenta minha intenção de compra.]': 'origem_intencao_qual', 'Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado. [Confio nas informações presentes no rótulo de pescado embalado.]': 'confia_rotulo', 'Quais barreiras de consumo [O preço elevado reduz minha frequência de consumo de pescado.]': 'barreira_1', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Considero o pescado uma opção proteica saudável.]': 'saude_proteica', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Associo o consumo de pescado à presença de gorduras benéficas, como ômega-3.]': 'omega3', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Acredito que consumir pescado regularmente contribui para minha saúde.]': 'saude_regular', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Sinto que tenho informação suficiente sobre os benefícios nutricionais do pescado.]': 'info_suficiente', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Considero o pescado de aquicultura uma alternativa sustentável.]': 'aquicultura_sustentavel', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [A origem sustentável do pescado aumenta minha intenção de compra.]': 'origem_sustent', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Preocupo-me com o impacto ambiental da produção e captura de pescado.]': 'impacto_ambiental', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Estou disposto(a) a escolher pescado com menor impacto ambiental, mesmo que custe mais.]': 'disposto_impacto', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Tenho interesse em comprar pescado pronto para preparo.]': 'pronto_preparo', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Produtos sem espinhas aumentariam meu consumo.]': 'sem_espinhas', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [A facilidade de preparo influencia minha decisão de comprar pescado.]': 'facilidade_preparo', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Evito comprar pescado quando acho que o preparo será demorado.]': 'evita_demorado', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Tenho interesse em conhecer melhor os alimentos que consumo.]': 'conhecer_alimentos', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Gosto de participar do preparo dos alimentos em casa.]': 'participar_preparo', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Tenho interesse em experimentar novos alimentos.]': 'interesse_experimentar_novos', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Costumo buscar informações antes de comprar alimentos que não conheço bem.]': 'busca_info', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [A presença de espinhas reduz meu interesse em consumir pescado.]': 'barreira_2', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [O odor característico do pescado dificulta meu consumo.]': 'barreira_3', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Tenho dificuldade em preparar pescado em casa.]': 'barreira_4', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [Tenho dificuldade em encontrar pescado de boa qualidade onde moro.]': 'barreira_5', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [O pescado não faz parte da rotina alimentar da minha família.]': 'barreira_6', 'Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado. [A desconfiança sobre a origem reduz minha intenção de comprar pescado.]': 'barreira_7', 'Indique seu nível de concordância sobre a possibilidade de comprar os seguintes produtos à base de pescado. [Eu compraria hambúrguer elaborado com pescado.]': 'aceita_hamburguer', 'Indique seu nível de concordância sobre a possibilidade de comprar os seguintes produtos à base de pescado. [Eu compraria linguiça frescal elaborada com pescado.]': 'aceita_linguica', 'Indique seu nível de concordância sobre a possibilidade de comprar os seguintes produtos à base de pescado. [Eu compraria patê elaborado com pescado.]': 'aceita_pate', 'Indique seu nível de concordância sobre a possibilidade de comprar os seguintes produtos à base de pescado. [Eu compraria nuggets elaborados com pescado.]': 'aceita_nuggets', 'Indique seu nível de concordância sobre a possibilidade de comprar os seguintes produtos à base de pescado. [Eu compraria snacks proteicos elaborados com pescado.]': 'aceita_snacks', 'Indique seu nível de concordância sobre a possibilidade de comprar os seguintes produtos à base de pescado. [Eu compraria produtos congelados de pescado se fossem práticos e seguros.]': 'aceita_congelados', 'Indique seu nível de concordância com as afirmações abaixo sobre tecnologia, processamento e industrialização do pescado. [Considero positivo o uso de tecnologia para tornar o pescado mais prático e seguro.]': 'tech_positivo', 'Indique seu nível de concordância com as afirmações abaixo sobre tecnologia, processamento e industrialização do pescado. [Tenho receio de consumir produtos de pescado muito processados.]': 'tech_receio', 'Indique seu nível de concordância com as afirmações abaixo sobre tecnologia, processamento e industrialização do pescado. [A lista de ingredientes influencia minha aceitação de produtos processados de pescado.]': 'tech_ingredientes', 'Indique seu nível de concordância com as afirmações abaixo sobre tecnologia, processamento e industrialização do pescado. [Prefiro pescado fresco a produtos industrializados de pescado.]': 'tech_prefere_fresco', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Tenho intenção de comprar pescado nos próximos 30 dias.]': 'intencao_30dias', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Gostaria de aumentar meu consumo de pescado.]': 'intencao_aumentar', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Eu recomendaria o consumo de pescado para familiares ou amigos.]': 'intencao_recomendaria', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Tenho intenção de experimentar novos produtos à base de pescado.]': 'intencao_experimentar', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Pagaria mais por pescado com origem rastreável.]': 'paga_rastreavel', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Pagaria mais por pescado com selo de inspeção.]': 'paga_selo', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Pagaria mais por pescado sem espinhas.]': 'paga_sem_espinhas', 'Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala [Pagaria mais por pescado produzido de forma sustentável.]': 'paga_sustentavel'})
    for c in ['Qual sua idade?', 'Qual seu sexo?', 'Qual seu maior nível de escolaridade?', 'Qual sua renda familiar mensal aproximada?', 'Com que frequência você consome pescado', 'Você reside em município litorâneo?', 'Você participa das decisões de compra de alimentos no seu domicílio?', 'Qual forma de pescado você mais consome?']:
        d[c] = d[c].map(lambda v: v if pd.isna(v) else str(v).strip().lower())
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
