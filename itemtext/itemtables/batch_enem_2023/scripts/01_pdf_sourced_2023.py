#!/usr/bin/env python3
"""
ENEM 2023 item text -- the PDF-sourced supplement.

The LARANJA (Braille / Adaptada Ledor) accessibility booklet is the primary source
for 2023 item text, because INEP wrote verbal descriptions of the figures into it.
But that booklet substitutes 4 of the 185 main-application items, and for 1 further
item INEP declined to describe the figure. This script supplies those gaps from the
standard day-2 AZUL booklet PDF (ENEM_2023_P1_CAD_07_DIA_2_AZUL.pdf), read page by
page as rendered images.

Two outputs:
  pdf_sourced_items_2023.csv      -- complete item text + options for the 4 items
                                     absent from the accessibility booklet
  figure_desc_patches_2023.csv    -- replacement figure descriptions for items whose
                                     accessibility-booklet text declines to describe
                                     a figure ("não foi descrita")

PROVENANCE. Text transcribed from the AZUL PDF is INEP's own wording. Figure and
option descriptions marked "(gerada por IA)" are NOT INEP's -- INEP wrote no
description for these, so they were generated from the rendered page image. The
marker is inline (so it travels with the text) and also recorded in the
`desc_provenance` column and in PROVENANCE.md.

Style follows INEP's own conventions in the DOSVOX files:
  "Descrição da figura: ... (Fim da descrição)"
  "Descrição das alternativas: <shared framing>" followed by per-option specifics
Formulas are written flat (Hg2(NO3)2, C12H8Cl6) as the DOSVOX files do.
"""
import csv, os

OUT = os.path.dirname(os.path.abspath(__file__))
SRC_BOOKLET = "ENEM_2023_P1_CAD_07_DIA_2_AZUL.pdf"

# ---------------------------------------------------------------- item 78578
# CN, AZUL question 110 (page 6). Key B -- confirmed by stoichiometry:
# 5,25 g / 525 g mol-1 = 0,01 mol Hg2(NO3)2 needs 0,02 mol NaCl = 1,16 g, and
# yields 0,01 mol x 472 = 4,72 g Hg2Cl2. Plateau at ~1,15 g / ~4,7 g => B.
i78578_text = """Um assistente de laboratório precisou descartar sete frascos contendo solução de nitrato de mercúrio(I) que não foram utilizados em uma aula prática. Cada frasco continha 5,25 g de Hg2(NO3)2 dissolvidos em água. Temendo a toxidez do mercúrio e sabendo que o Hg2Cl2 tem solubilidade muito baixa, o assistente optou por retirar o mercúrio da solução por precipitação com cloreto de sódio (NaCl), conforme a equação química:

Descrição da equação química (gerada por IA): Os reagentes Hg2(NO3)2 em solução aquosa e 2 NaCl em solução aquosa formam os produtos Hg2Cl2 sólido e 2 NaNO3 em solução aquosa. (Fim da descrição)

Na dúvida sobre a massa de NaCl a ser utilizada, o assistente aumentou gradativamente a quantidade adicionada em cada frasco, como apresentado no quadro.

Descrição do quadro (gerada por IA): O quadro tem duas linhas e oito colunas. A primeira linha, intitulada Frasco, identifica os frascos I, II, III, IV, V, VI e VII. A segunda linha, intitulada Massa de NaCl em grama (g), apresenta, respectivamente, os valores 0,2; 0,4; 0,6; 0,8; 1,0; 1,2 e 1,4. (Fim da descrição)

O produto obtido em cada experimento foi filtrado, seco e teve sua massa aferida. O assistente organizou os resultados na forma de um gráfico que correlaciona a massa de NaCl adicionada com a massa de Hg2Cl2 obtida em cada frasco. A massa molar do Hg2(NO3)2 é 525 g mol-1, a do NaCl é 58 g mol-1 e a do Hg2Cl2 é 472 g mol-1.

Qual foi o gráfico obtido pelo assistente de laboratório?

Descrição das alternativas (gerada por IA): Em cada alternativa há a representação de um gráfico cartesiano, em que o eixo horizontal representa a massa de NaCl, em grama, com marcas de 0,0 a 1,4; e o eixo vertical representa a massa de Hg2Cl2, em grama, com marcas de 0 a 7."""

i78578_opts = [
    ("A", "O gráfico é formado por dois trechos: um segmento de reta crescente que parte da origem e vai até o ponto de abscissa aproximadamente 0,6 e ordenada aproximadamente 4,7; e, a partir desse ponto, um trecho horizontal que permanece na ordenada 4,7 até a abscissa 1,4."),
    ("B", "O gráfico é formado por dois trechos: um segmento de reta crescente que parte da origem e vai até o ponto de abscissa aproximadamente 1,15 e ordenada aproximadamente 4,7; e, a partir desse ponto, um trecho horizontal que permanece na ordenada 4,7 até a abscissa 1,4."),
    ("C", "O gráfico é um único segmento de reta crescente, que parte da origem e atinge, na abscissa 1,4, a ordenada aproximadamente 5,6, sem apresentar trecho horizontal."),
    ("D", "O gráfico é formado por dois trechos: um segmento de reta crescente que parte do ponto de abscissa 0,0 e ordenada aproximadamente 2,6 e vai até o ponto de abscissa aproximadamente 1,15 e ordenada aproximadamente 4,6; e, a partir desse ponto, um trecho horizontal até a abscissa 1,4."),
    ("E", "O gráfico é um único segmento de reta crescente, de inclinação pequena, que parte do ponto de abscissa 0,0 e ordenada aproximadamente 5,2 e atinge, na abscissa 1,4, a ordenada aproximadamente 6,5."),
]

# ---------------------------------------------------------------- item 54804
# CN, AZUL question 123 (page 11). Key E -- butilbrometo de escopolamina is the
# only one of the five drawn with stereobonds, i.e. the only chiral one.
i54804_text = """Entre os medicamentos mais comuns consumidos para o alívio da dor está o ibuprofeno, um composto quiral com ação anti-inflamatória e efeito analgésico, que é comercializado como fármaco opticamente puro, ou seja, sem a mistura com outro isômero óptico. A fórmula estrutural plana do ibuprofeno é:

Descrição da figura (gerada por IA): Fórmula estrutural plana do ibuprofeno. Um anel benzênico apresenta dois substituintes em posições opostas do anel. De um lado, um grupo isobutila, formado por um carbono ligado a outro carbono que se ramifica em dois grupos metila. Do outro lado, um carbono ligado a um grupo metila e a um grupo carboxila, sendo o grupo carboxila formado por um carbono com ligação dupla a um oxigênio e ligação simples a um grupo OH. Legenda: Ibuprofeno. (Fim da descrição)

Além do ibuprofeno, destacam-se também os princípios ativos a seguir, presentes em outros medicamentos para o alívio da dor:

Descrição das figuras (gerada por IA): São apresentadas as fórmulas estruturais planas de cinco princípios ativos. Fenacetina: um anel benzênico com dois substituintes em posições opostas; de um lado, um oxigênio ligado a uma cadeia de dois carbonos; do outro, um grupo NH ligado a um carbono que apresenta ligação dupla a um oxigênio e ligação simples a um grupo metila. Paracetamol: estrutura semelhante à da fenacetina, com um grupo OH no lugar do substituinte com oxigênio e cadeia de dois carbonos. Dipirona sódica: um anel de cinco membros contendo dois átomos de nitrogênio, ao qual estão ligados grupos metila, um anel benzênico, um oxigênio por ligação dupla e um átomo de nitrogênio que se liga a um grupo contendo enxofre e oxigênios, com carga negativa, associado a um íon sódio. Diclofenaco sódico: dois anéis benzênicos unidos por um grupo NH; um dos anéis apresenta dois átomos de cloro e o outro apresenta uma cadeia de um carbono ligada a um grupo com dois oxigênios e carga negativa, associado a um íon sódio. Butilbrometo de escopolamina: estrutura policíclica que contém um átomo de nitrogênio com carga positiva, ligado a um grupo de quatro carbonos e a um grupo metila, associado a um íon brometo; a estrutura apresenta ainda um anel de três membros com oxigênio, um grupo com dois oxigênios ligado a um carbono que se liga a um anel benzênico e a um grupo com OH. Das cinco fórmulas, apenas a do butilbrometo de escopolamina é desenhada com ligações em cunha e com átomos de hidrogênio explícitos, notação usada para indicar a configuração espacial em torno de um carbono. (Fim da descrição)

O princípio ativo que apresenta o mesmo tipo de isomeria espacial que o ibuprofeno é o(a)"""

i54804_opts = [
    ("A", "fenacetina."),
    ("B", "paracetamol."),
    ("C", "dipirona sódica."),
    ("D", "diclofenaco sódico."),
    ("E", "butilbrometo de escopolamina."),
]

# ---------------------------------------------------------------- item 125902
# MT, AZUL question 163 (page 24). Key A -- constant speed with distance rising
# linearly, holding constant, then falling linearly means: straight out from the
# base, an arc at constant radius, then straight back. That is a circular sector.
i125902_text = """Uma empresa de segurança domiciliar oferece o serviço de patrulha noturna, no qual vigilantes em motocicletas fazem o monitoramento periódico de residências. A empresa conta com uma base, de onde acompanha o trajeto realizado pelos vigilantes durante as patrulhas e orienta o deslocamento de equipes de reforço quando necessário. Numa patrulha rotineira, sem ocorrências, um vigilante conduziu sua motocicleta a uma velocidade constante durante todo o itinerário estabelecido, levando 30 minutos para conclusão. De acordo com os registros do GPS alocado na motocicleta, a distância da posição do vigilante à base, ao longo do tempo de realização do trajeto, é descrita pelo gráfico.

Descrição do gráfico (gerada por IA): Gráfico intitulado Distância do vigilante em relação à base em função do tempo. O eixo horizontal representa o tempo, em minuto, com marcas em 0, 10, 20 e 30; o eixo vertical representa a distância do vigilante à base, em quilômetro, com marcas de 1 a 4. O gráfico é formado por três segmentos de reta: o primeiro cresce do ponto de tempo 0 e distância 0 até o ponto de tempo 10 e distância 3; o segundo é horizontal, mantendo a distância 3 entre os tempos 10 e 20; o terceiro decresce do ponto de tempo 20 e distância 3 até o ponto de tempo 30 e distância 0. (Fim da descrição)

A vista superior da trajetória realizada pelo vigilante durante a patrulha registrada no gráfico é descrita pela representação

Descrição das alternativas (gerada por IA): Em cada alternativa há a representação da vista superior de um trajeto, com setas indicando o sentido do percurso."""

i125902_opts = [
    ("A", "A figura é um setor circular: dois segmentos de reta partem de um mesmo vértice, na parte inferior, e são unidos na parte superior por um arco de circunferência. As setas indicam o percurso saindo do vértice por um dos segmentos, seguindo ao longo do arco e retornando ao vértice pelo outro segmento."),
    ("B", "A figura é um triângulo com o vértice voltado para baixo, formado por dois segmentos de reta laterais unidos na parte superior por um segmento de reta horizontal. As setas indicam o percurso ao longo dos lados."),
    ("C", "A figura é formada por apenas dois segmentos de reta que se encontram em um vértice na parte superior, permanecendo aberta na parte inferior. As setas indicam o percurso subindo por um dos segmentos e descendo pelo outro."),
    ("D", "A figura é formada por um segmento de reta horizontal na parte superior e dois segmentos de reta inclinados que descem de suas extremidades, permanecendo aberta na parte inferior, com aspecto de trapézio sem a base menor. As setas indicam o percurso subindo por um lado, seguindo pelo trecho horizontal e descendo pelo outro lado."),
    ("E", "A figura é um semicírculo: um segmento de reta horizontal na parte inferior, com um ponto destacado em seu meio, é unido a um arco semicircular na parte superior. As setas indicam o percurso ao longo do arco e do segmento horizontal."),
]

# ---------------------------------------------------------------- item 81742
# MT, AZUL question 176 (page 30). Key E -- the n-th pentagonal number is
# n(3n-1)/2, so the 8th is 8 x 23 / 2 = 92.
i81742_text = """Os números figurados pentagonais provavelmente foram introduzidos pelos pitagóricos por volta do século V a.C. As figuras ilustram como obter os seis primeiros deles, sendo os demais obtidos seguindo o mesmo padrão geométrico.

Descrição das figuras (gerada por IA): São apresentadas seis figuras formadas por pontos, rotuladas com os números 1, 5, 12, 22, 35 e 51. A primeira figura é um único ponto, rotulada 1. A segunda é um pentágono regular com um ponto em cada vértice, totalizando 5 pontos, rotulada 5. Cada figura seguinte é obtida acrescentando, à figura anterior, um novo pentágono maior que compartilha um vértice e dois lados com o pentágono anterior, com pontos adicionais igualmente espaçados ao longo dos novos lados. As figuras têm, respectivamente, 1, 5, 12, 22, 35 e 51 pontos. (Fim da descrição)

O oitavo número pentagonal é"""

i81742_opts = [
    ("A", "59."),
    ("B", "83."),
    ("C", "86."),
    ("D", "89."),
    ("E", "92."),
]

ITEMS = [
    dict(table="enem_2023_1mil_cn", item="78578",  pos=110, key="B",
         text=i78578_text,  opts=i78578_opts,  page=6,  desc_ai=True),
    dict(table="enem_2023_1mil_cn", item="54804",  pos=123, key="E",
         text=i54804_text,  opts=i54804_opts,  page=11, desc_ai=True),
    dict(table="enem_2023_1mil_mt", item="125902", pos=163, key="A",
         text=i125902_text, opts=i125902_opts, page=24, desc_ai=True),
    dict(table="enem_2023_1mil_mt", item="81742",  pos=176, key="E",
         text=i81742_text,  opts=i81742_opts,  page=30, desc_ai=True),
]

# ------------------------------------------------- figure description patches
# Items whose accessibility-booklet text is complete EXCEPT that INEP declined to
# describe a figure. The patch replaces INEP's declining sentence.
PATCHES = [dict(
    table="enem_2023_1mil_cn", item="60332", laranja_pos=92, azul_pos=129, page=13,
    declined_text=("Descrição da ilustração: Estrutura química da molécula de Aldrin. "
                   "Essa ilustração não foi descrita, pois suas informações não foram "
                   "solicitadas para a resolução da questão. (Fim da descrição)"),
    replacement=("Descrição da ilustração (gerada por IA): Fórmula estrutural plana da molécula "
                 "de Aldrin, de fórmula C12H8Cl6, simétrica em relação a um eixo vertical. A "
                 "estrutura é formada por dois anéis de seis membros fundidos, que compartilham "
                 "uma ligação entre dois carbonos. No anel superior há uma ligação dupla entre os "
                 "dois carbonos do topo e, no interior do anel, um carbono ligado a dois átomos de "
                 "hidrogênio, um acima e um abaixo, unido ao anel por duas ligações representadas "
                 "por tracejado. No anel inferior há uma ligação dupla entre os dois carbonos da "
                 "base e, no interior do anel, um carbono ligado a dois átomos de cloro, um acima e "
                 "um abaixo, unido ao anel por duas ligações representadas em cunha cheia. Há ainda "
                 "quatro átomos de cloro ligados ao anel inferior: dois nos carbonos laterais e dois "
                 "nos carbonos da base. A molécula apresenta, ao todo, doze átomos de carbono, oito "
                 "de hidrogênio e seis de cloro. Legenda: Aldrin. (Fim da descrição)"),
)]


def main():
    p1 = os.path.join(OUT, "pdf_sourced_items_2023.csv")
    with open(p1, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "item", "correct_response", "item_text",
                    "option_letter", "option_text", "resp",
                    "text_source", "src_booklet", "src_position", "src_page",
                    "desc_provenance"])
        for it in ITEMS:
            for letter, otext in it["opts"]:
                w.writerow([
                    it["table"], it["item"], it["key"], it["text"],
                    letter, otext, 1 if letter == it["key"] else 0,
                    "standard_booklet_pdf", SRC_BOOKLET, it["pos"], it["page"],
                    "ai_generated" if it["desc_ai"] else "inep",
                ])

    p2 = os.path.join(OUT, "figure_desc_patches_2023.csv")
    with open(p2, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "item", "laranja_position", "azul_position",
                    "src_page", "declined_text", "replacement", "desc_provenance"])
        for p in PATCHES:
            w.writerow([p["table"], p["item"], p["laranja_pos"], p["azul_pos"],
                        p["page"], p["declined_text"], p["replacement"],
                        "ai_generated"])

    n_rows = sum(len(i["opts"]) for i in ITEMS)
    print(f"wrote {p1}  ({len(ITEMS)} items, {n_rows} option rows)")
    print(f"wrote {p2}  ({len(PATCHES)} patch)")


if __name__ == "__main__":
    main()
