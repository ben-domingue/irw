#!/usr/bin/env python3
"""Move figure descriptions that INEP printed under the wrong item.

WHY THIS EXISTS. The accessibility ("LEDOR") editions render a figure as a
prose description. Most are set inline, where the figure would be. Some are
collected at the FOOT OF THE PAGE, after the last item's options -- and those
describe an item printed earlier on the page, or on the next one. The parser
attaches trailing text to the item it physically follows, so the description
lands on the wrong item.

This is invisible to every content gate. The stem is longer than it should be,
not shorter; no character is wrong; item_set_match stays TRUE. It surfaced
only when a model tried to ANSWER the items: 2018 CN 59858 is a question about
the energy released by oxidising glucose, and its stem ends with a description
of an electrical circuit.

A description on the wrong item is worse than no description -- it actively
misleads -- so nothing here is left in place on a hunch. Each operation is
hand-verified against the printed page and recorded below with the evidence.

THE AUDIT RULE (replicable, and the reason this file also runs on new years):
flag any stem whose LAST `Descrição ...:` block starts in its final 45% AND is
preceded by a question closer ("?", "e mais proxima de", "e igual a", ...).
A well-formed item describes its figure BEFORE asking about it.

Three kinds of thing trip that rule, and only the first is a defect:

  1. MISPLACED  -- the description belongs to another item.  Listed in OPS.
  2. OPTION SET -- "Descricao das alternativas": it describes the five OPTIONS,
                   so it correctly follows the question.  Listed in KEEP.
  3. OWN FIGURE -- printed after the options but genuinely this item's.
                   Listed in KEEP with the evidence.

--apply refuses to run if the audit finds anything in none of those lists,
rather than guessing at a new case.

=============================================================================
WHAT THE 2026-10-02 REVIEW CHANGED, AND WHY THE TABLE HAS THE SHAPE IT DOES
=============================================================================

A full read of 2013-2025 (Santiago, #2462) found 27 further misplaced blocks
on top of the three already here. Fixing them broke three assumptions that
the original three cases never exercised.

1. THE BLOCK TO MOVE IS NOT ALWAYS THE LAST ONE. This pass used to cut
   `ms[-1]`. 10 of the 27 donors carry TWO description blocks -- one their
   own, one misplaced -- and in 7 of those the misplaced block is NOT the
   last. 2018 MT 111725 is the trap: its page-foot blocks are the frequency
   quadro of QUESTAO 156 followed by 157's OWN cartesian-mesh figure, so
   cutting the last block would have moved the wrong one and corrupted both
   items. Each operation therefore names its block by a verbatim opening
   anchor, `cut_from`.

2. A CUT THAT RUNS TO THE END OF THE STEM CAN SWALLOW THE DONOR'S QUESTION.
   2022 CH 44230 prints its description BEFORE its own question, so cutting
   from the mark to the end of the stem carried off "Nas sociedades
   contemporaneas, consiste em violacao do principio basico enunciado no
   texto:". `cut_to` names the text that FOLLOWS the block; None means the
   block genuinely runs to the end.

3. APPENDING TO THE RECIPIENT REPRODUCES THE DEFECT THE AUDIT LOOKS FOR.
   The old code did `rbefore.rstrip() + " " + cut`, which puts the relocated
   description AFTER the recipient's question -- exactly the shape rule R13
   calls malformed. That is why KEEP used to carry 89518: the fix created a
   new audit hit that had to be suppressed. Worse, 2018 MT 15884's surviving
   description opens "A mesma figura anterior" -- a back-reference that
   appending leaves pointing at nothing.

   So insert position is now explicit and never guessed: `where` is one of
   "start", "before", "after" or "replace", against a verbatim `at` anchor in
   the recipient. The three original moves were re-seated the same way.

   The LC placeholders decide themselves: four recipients ship with EMPTY
   "TEXTO I"/"TEXTO II" slots (112150 is literally "TEXTO I\\nTEXTO II\\nAs
   duas imagens ..."), and the blocks drop straight into them.

4. SOMETIMES THE CONTENT IS ALREADY THERE BY ANOTHER ROUTE, so the block must
   be removed from the donor without being re-homed -- op="drop". All three
   cases are 2018 items whose quadro 55_recover_tables already recovered from
   the STANDARD booklet (std_d2), which is the edition the candidates in the
   response tables actually sat (R15's first condition). Re-homing the
   accessibility prose as well would make the recipient state the same figures
   twice. The block still has to leave the wrong item.

   Note the ordering dependency: 55_recover_tables runs AFTER this pass in
   42_rebuild.py, so at the moment a "drop" is applied the recipient does not
   yet carry the table. The justification is the finished state of the year,
   not the state mid-pipeline.

5. ONE RECIPIENT ALREADY HELD A CORRUPT RENDERING of the block being moved.
   2022 CH 97262's TEXTO 2 is a scrambled dump of the same infographic, with
   the percentages in one order and the labels in another; read in document
   order it pairs single mothers with 30,4 per cent where the printed figure
   is 56,9. The prose block replaces it rather than joining it. This is the
   one operation here that DELETES shipped text, and it is flagged in the PR
   for an explicit ruling.

OPS is applied in list order. Two recipients receive two blocks each
(2018 LC 112150, 2018 MT 111535) and the second insert's anchor is only
unambiguous after the first has been applied.

Usage:
  python3 54_relocate_descriptions.py --tables DIR [--apply]
"""
import argparse, csv, glob, os, re, sys
from _rawedit import rewrite_field

MARK = re.compile(r"Descri[çc][ãa]o\s+d(?:o|a|e|os|as)\b[^:]{0,90}:")
CLOSER = re.compile(r"(\?|é mais pr[óo]xim[ao] de|corresponde a|deve ser|ser[áa] de|"
                    r"[ée] igual a|em que|classificado como|da seguinte maneira|"
                    r"respectivamente|[ée],? aproximadamente,?)\s*$", re.I)

# Each entry is ONE description block and what to do with it.
#   op       "move" cut it out of `donor` and place it in `recip`
#            "drop" cut it out of `donor` and do not re-home it; `why` names
#                   the route by which `recip` already has the content
#   cut_from verbatim opening of the block, in the donor's stem (must be unique)
#   cut_to   verbatim text that FOLLOWS the block; absent means run to the end
#   where    "start"   at the head of the recipient's stem
#            "before"  immediately before verbatim `at`
#            "after"   immediately after verbatim `at`
#            "replace" substitute `template` for verbatim `at`, {cut} standing
#                      for the relocated block
#   why      the printed page, what the block depicts, which item it belongs to
#            and how that was established
OPS = [
    dict(
        year='2018',
        csv='enem_2018_1mil_ch__items.csv',
        op='move',
        donor='111972',
        recip='111805',
        cut_from='Descrição da Figura 1:\nFotografia composta por um ônibu',
        where='start',
        why="acc_d1 p21 foot. 'Figura 1 ... onibus antigo exposto em um museu' and 'Figura 2 ... Rosa Parks esta ao lado de Martin Luther King' are the two photographs of QUESTAO 50 (= 111805), whose stem reads 'Esse onibus relaciona-se ao ato praticado, em 1955, por Rosa Parks, apresentada em fotografia ao lado de Martin Luther King'. The donor, QUESTAO 53 (= 111972), is about globalisation as reterritorialisation and has no photograph. 111805 carries no description and its stem opens with a back-reference, so the block goes at the head.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_ch__items.csv',
        op='move',
        donor='86195',
        recip='112110',
        cut_from='Descrição de imagem:\nIlustração apresenta, no primeiro ',
        where='start',
        why="acc_d1 p27 foot. 'Ilustracao ... Getulio Vargas ... segura afetuosamente o queixo de uma menina uniformizada', with the quoted address 'Criancas! Aprendendo, no lar e nas escolas, o culto da Patria', is the schoolbook page of QUESTAO 74 (= 112110), 'Essa imagem foi impressa em cartilha escolar durante a vigencia do Estado Novo'. The donor, QUESTAO 76 (= 86195), quotes the 1890 Codigo Penal; its own question PRECEDES the block and survives the cut. The quoted Vargas text is inside the illustration, so the block runs to the end of the stem.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_ch__items.csv',
        op='move',
        donor='88500',
        recip='89461',
        cut_from='Descrição de imagem:\nMapa-múndi intitulado Trajetória d',
        where='start',
        why="acc_d1 p24 foot. 'Mapa-mundi intitulado Trajetoria de ciclones tropicais' is the entire stimulus of QUESTAO 63 (= 89461), which ships as nothing but its question, 'Qual caracteristica do meio fisico e condicao necessaria para a distribuicao espacial do fenomeno representado?'. The donor, QUESTAO 64 (= 88500), is about bolsas de mandinga.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_cn__items.csv',
        op='move',
        donor='17449',
        recip='40203',
        cut_from='Descrição da estrutura do grafeno:\nA estrutura apresent',
        where='before',
        at='Nesse arranjo, os átomos de carbono',
        why="acc_d2 p3 foot. 'Descricao da estrutura do grafeno ... rede plana formada por varios hexagonos' is the figure of QUESTAO 97 (= 40203), 'Sua estrutura e hexagonal, conforme a figura'. The donor, QUESTAO 98 (= 17449), is a spring-launcher item and keeps its OWN figure, the first block in its stem.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_cn__items.csv',
        op='move',
        donor='39342',
        recip='111395',
        cut_from='Descrição das figuras:\nAs figuras apresentam dois esque',
        cut_to='Descrição da imagem:\nUm vaso de barro bojudo,',
        where='before',
        at='O que ocorre com os alto-falantes E e D',
        why="acc_d2 p12 foot. 'Descricao das figuras ... dois esquemas de ligacao de um equipamento de som ... alto-falante esquerdo (E) ... direito (D)' is the schematic pair of QUESTAO 124 (= 111395), 'As figuras ilustram o esquema de conexao das caixas de som'. The donor, QUESTAO 125 (= 39342), is the Baghdad-battery item and keeps its own 'vaso de barro' block -- hence the explicit end anchor.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_cn__items.csv',
        op='drop',
        donor='46621',
        recip='87205',
        cut_from='Descrição do quadro:\nQuadro com dois combustíveis e seu',
        where=None,
        why="acc_d2 p4 foot. 'Quadro com dois combustiveis e seus valores de densidade ... Etanol ... Gasolina' is the quadro of QUESTAO 100 (= 87205). NOT re-homed: 55_recover_tables already supplies that quadro to 87205 from std_d2 QUESTAO 92, the edition the candidates in the response tables actually sat (R15). Re-homing the accessibility prose as well would state the same figures twice. The block still has to leave 46621, a bee-pheromone item.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='111970',
        recip='111948',
        cut_from='Descrição da fotografia:\nFoto, em preto e branco, que m',
        where='start',
        why="acc_d1 p10 foot. 'Foto ... fachada de um estabelecimento, em que a palavra supermercado esta escrita em varios idiomas' is the photograph of QUESTAO 22 (= 111948), 'A fotografia exibe a fachada de um supermercado em Foz do Iguacu'. Donor QUESTAO 24 (= 111970) is an academic-abstract item. The recipient stem opens with a back-reference, so the block goes at the head.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='112051',
        recip='111931',
        cut_from='Descrição do cartaz:\nO cartaz é composto por textos e f',
        where='start',
        why="acc_d1 p5 foot. 'Descricao do cartaz ... uma colher de acucar sendo colocada em uma xicara de cafe' is the poster of QUESTAO 7 (= 111931), whose question asks about the 'variedades linguisticas' of that very text. Donor QUESTAO 9 (= 112051) is about racism in social networks.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='112066',
        recip='23744',
        cut_from='Descrição do fotograma:\nO fotograma, em preto e branco,',
        where='after',
        at='TEXTO II',
        why="acc_d1 p13 foot. 'Descricao do fotograma ... silhueta da cabeca de duas pessoas beijando-se' is the Man Ray photogram of QUESTAO 29 (= 23744), whose TEXTO II slot is EMPTY and whose question reads 'No fotograma de Man Ray ...'. Donor QUESTAO 31 (= 112066) is the Galeano football text.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='112092',
        recip='89487',
        cut_from='Descrição da tirinha:\nTirinha intitulada “Ideologia e i',
        where='start',
        why="acc_d1 p9 foot. 'Tirinha intitulada Ideologia e internet' is the strip of QUESTAO 19 (= 89487), 'A principal consequencia criticada na tirinha sobre esse processo'. Donor QUESTAO 21 (= 112092) is the Hino Nacional item.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='13652',
        recip='87507',
        cut_from='Descrição do cartum:\nO cartum apresenta dois adolescent',
        where='start',
        why="acc_d1 p2, Ingles block, foot. 'Descricao do cartum ... dois adolescentes caminhando lado a lado' is the cartoon of QUESTAO 2 (= 87507), which ships as nothing but 'No cartum, a critica esta no fato de a sociedade exigir do adolescente que'. Donor QUESTAO 4 (= 13652) is the Khan Academy text. Both sit in the Ingles block on p2; the Espanhol block repeats positions 1-5 on p3-p4.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='24528',
        recip='9065',
        cut_from='Descrição do cartaz:\nO cartaz mostra a fotografia de um',
        where='replace',
        at='TEXTO I\nt\nTEXTO II',
        template='TEXTO I\n{cut}\nTEXTO II',
        why="acc_d1 p7 foot. 'Descricao do cartaz ... uma senhora sorridente usando um top de ginastica ... Aqueles que pensam que nao tem tempo para fazer exercicio' is TEXTO I of QUESTAO 13 (= 9065), whose TEXTO I slot holds only a stray 't'. Donor QUESTAO 15 (= 24528) is the Torquato Neto text. The substitution also clears that residue.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='25943',
        recip='23230',
        cut_from='Descrição da imagem:\nPágina de uma adaptação em quadrin',
        where='start',
        why="acc_d1 p11 foot. 'Pagina de uma adaptacao em quadrinhos de Rodrigo Rosa da obra Grande sertao: veredas' is the image of QUESTAO 25 (= 23230), 'A imagem integra uma adaptacao em quadrinhos da obra Grande sertao: veredas'. Donor QUESTAO 26 (= 25943) is the Coubertin text.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='76800',
        recip='23615',
        cut_from='Descrição da fotografia:\nA foto, em preto e branco, mos',
        where='start',
        why="acc_d1 p14 foot. 'A foto ... mostra um homem cantando e tocando violao em um palco' is the photograph of QUESTAO 32 (= 23615), about the group O Teatro Magico. Donor QUESTAO 33 (= 76800) is the Book Thief review.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='78076',
        recip='112018',
        cut_from='Descrição da fotografia:\nA foto, em preto e branco, mos',
        where='replace',
        at='TEXTO I\nTEXTO II',
        template='TEXTO I\n{cut}\nTEXTO II',
        why="acc_d1 p6 foot. 'A foto ... as pernas de uma pessoa deitada de lado ... espelho retangular colado na sola de cada um dos pes' is TEXTO I of QUESTAO 11 (= 112018), whose TEXTO I slot is EMPTY and whose question reads 'Nos textos, a concepcao de body art'. Donor QUESTAO 12 (= 78076) is the Whatscine text.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='82889',
        recip='112150',
        cut_from='Descrição da imagem:\nA obra Estrutura vertical dupla , ',
        cut_to='Descrição da imagem:\nA urna cerimonial marajo',
        where='replace',
        at='TEXTO I\nTEXTO II',
        template='TEXTO I\n{cut}\nTEXTO II',
        why="acc_d1 p15 foot, first of two blocks. 'A obra Estrutura vertical dupla, de Norma Grimberg' is TEXTO I of QUESTAO 34 (= 112150), whose TEXTO I and TEXTO II slots are BOTH empty and whose question contrasts exactly these two works. Donor QUESTAO 36 (= 82889) is the Manoel de Barros poem.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='82889',
        recip='112150',
        cut_from='Descrição da imagem:\nA urna cerimonial marajoara é um v',
        where='after',
        at='TEXTO II',
        template='TEXTO I\n{cut}\nTEXTO II',
        why="acc_d1 p15 foot, second of two blocks. 'A urna cerimonial marajoara' is TEXTO II of the same QUESTAO 34 (= 112150). Applied after the TEXTO I substitution, which is what leaves the bare 'TEXTO II' anchor unambiguous.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_lc__items.csv',
        op='move',
        donor='89028',
        recip='112041',
        cut_from='Descrição do cartaz:\nO cartaz é composto por foto e tex',
        where='start',
        why="acc_d1 p17 foot. 'Descricao do cartaz ... tres mulheres ... Telefone Lilas' is the poster of QUESTAO 41 (= 112041), 'Nesse texto, busca-se convencer o leitor a mudar seu comportamento'. Donor QUESTAO 42 (= 89028) is A Casa de Vidro.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_mt__items.csv',
        op='move',
        donor='111434',
        recip='15884',
        cut_from='Descrição da figura:\nDois círculos concêntricos, sendo ',
        where='before',
        at='Descrição da figura: \nA mesma figura anterior, destacando o ',
        why="acc_d2 p31 foot. 'Dois circulos concentricos, sendo o menor denominado chafariz e o maior, praca' is the OVERVIEW figure of QUESTAO 179 (= 15884). 15884 already carries the DETAIL figure, which opens 'A mesma figura anterior' -- a back-reference with no antecedent until this block lands BEFORE it. Donor QUESTAO 180 (= 111434) keeps its own 8-by-8 board figure. The anchor spans the existing block's LABEL as well as its first words: anchoring on the body alone inserted the relocated block between that label and the text it introduces, leaving two 'Descricao da figura:' lines and an orphaned body.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_mt__items.csv',
        op='move',
        donor='111468',
        recip='66805',
        cut_from='Descrição da figura: \nDois eixos perpendiculares interc',
        cut_to='Descrição da figura:\nFigura com cinco retângu',
        where='before',
        at='Com base nas posições relativas',
        why="acc_d2 p20 foot, first of two blocks. 'Dois eixos perpendiculares ... o eixo horizontal indica a massa m e o eixo vertical indica o raio r ... pontos A e B' is the graph of QUESTAO 151 (= 66805), the Lei Universal da Gravitacao item that compares satellites A, B and C on an (m;r) plot. Donor QUESTAO 153 (= 111468) keeps the SECOND block, its own five-X-ray-machine figure: here the LAST block is the one to keep, not the one to move.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_mt__items.csv',
        op='drop',
        donor='111692',
        recip='32905',
        cut_from='Descrição do quadro: \nQuadro com as seguintes informaçõ',
        cut_to='Descrição da figura: \nFigura formada por dois',
        where=None,
        why="acc_d2 p21 foot. 'Quadro ... Numero de acidentes sofridos: 0; numero de trabalhadores: 50 ...' is the quadro of QUESTAO 154 (= 32905). NOT re-homed: 55_recover_tables supplies it from std_d2 QUESTAO 145. The block still has to leave QUESTAO 155 (= 111692), which keeps its own rosa-dos-ventos figure.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_mt__items.csv',
        op='move',
        donor='111718',
        recip='111535',
        cut_from='Descrição da figura:\nA figura mostra um triângulo retân',
        cut_to='Descrição da figura:\nA figura mostra do lado ',
        where='after',
        at='como no exemplo da figura:',
        why="acc_d2 p29 foot, first of two blocks. 'Um triangulo retangulo com o lado horizontal medindo 1 metro, o lado vertical medindo 20 centimetros ... Inclinacao e igual a vinte por cento' is the EXAMPLE figure of QUESTAO 175 (= 111535), cited by its stem as 'como no exemplo da figura:'. Donor QUESTAO 176 (= 111718) draws balls from urns and has no figure at all, so BOTH of its blocks are misplaced.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_mt__items.csv',
        op='move',
        donor='111718',
        recip='111535',
        cut_from='Descrição da figura:\nA figura mostra do lado esquerdo u',
        where='after',
        at='tem 8 metros de comprimento.',
        why="acc_d2 p29 foot, second of two blocks. 'Um portao no nivel da rua ... A distancia desse segmento ate a base da garagem mede 8 metros' is the PROBLEM figure of the same QUESTAO 175 (= 111535), and lands after the sentence describing that ramp.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_mt__items.csv',
        op='drop',
        donor='111725',
        recip='98294',
        cut_from='Descrição do quadro: \nQuadro com as seguintes informaçõ',
        cut_to='Descrição da figura: \nNo plano cartesiano est',
        where=None,
        why="acc_d2 p22 foot, first of two blocks. 'Quadro ... Ranking: I; Frequencia: 4 ...' is the SECOND quadro of QUESTAO 156 (= 98294), whose stem says 'nos quadros', plural. NOT re-homed: 55_recover_tables supplies it from std_d2 QUESTAO 172 -- that pass had already diagnosed this same gap. Donor QUESTAO 157 (= 111725) keeps the LAST block, its own cartesian-mesh figure.",
    ),
    dict(
        year='2020',
        csv='enem_2020_1mil_ch__items.csv',
        op='move',
        donor='111815',
        recip='97979',
        cut_from='Descrição da imagem: Representação cartográfica \nmostra',
        where='start',
        why="CAD_09_DIA_1_LARANJA_LEDOR p23 foot. 'Representacao cartografica mostrando o Vale da Grande Fenda' is the entire stimulus of QUESTAO 58 (= 97979), which ships as nothing but 'Os aspectos fisicos apresentados originam-se da atuacao da forca natural de'. Donor QUESTAO 59 (= 111815) is about biographical history.",
    ),
    dict(
        year='2020',
        csv='enem_2020_1mil_ch__items.csv',
        op='move',
        donor='88307',
        recip='111792',
        cut_from='Descrição do mapa: Mapa do Brasil com destaque para a R',
        where='start',
        why="CAD_09_DIA_1_LARANJA_LEDOR p30 foot. 'Mapa do Brasil com destaque para a Regiao Centro-Oeste marcada por tres rodovias longitudinais' is the map of QUESTAO 89 (= 111792), 'O mapa e o texto se complementam indicando que a expansao das rodovias'. Donor QUESTAO 90 (= 88307) is the quadrilha dance item.",
    ),
    dict(
        year='2020',
        csv='enem_2020_1mil_lc__items.csv',
        op='move',
        donor='64056',
        recip='15001',
        cut_from='Descrição da obra: A obra One and Three Chairs \né compo',
        where='start',
        why="CAD_09_DIA_1_LARANJA_LEDOR p13 foot. 'A obra One and Three Chairs e composta de tres pecas' is the work of QUESTAO 30 (= 15001), 'A obra de Joseph Kosuth ... se constitui por uma fotografia de cadeira, uma cadeira exposta e um quadro'. Donor QUESTAO 31 (= 64056) keeps the FIRST block, its own virtual-reality image.",
    ),
    dict(
        year='2020',
        csv='enem_2020_1mil_lc__items.csv',
        op='move',
        donor='96814',
        recip='111838',
        cut_from='Descrição do anúncio publicitário: O anúncio \nintitulad',
        where='start',
        why="CAD_09_DIA_1_LARANJA_LEDOR p8 foot. 'O anuncio intitulado Respeita as torcedoras!' is the advertisement of QUESTAO 15 (= 111838), which ships as nothing but 'Esse anuncio publicitario propoe solucoes para um problema social recorrente, ao'. Donor QUESTAO 16 (= 96814) is the martial-arts teaching text.",
    ),
    dict(
        year='2022',
        csv='enem_2022_1mil_ch__items.csv',
        op='move',
        donor='44230',
        recip='97262',
        cut_from='Descrição da imagem: Infográfico intitulado \nProporção ',
        cut_to='Nas sociedades contemporâneas, consiste em vi',
        where='replace',
        at='30,4%\n21,0%\n11,6%\n10,0%\nProporção de pessoas abaixo da linha de pobreza\nPor arranjo domiciliar no Brasil — 2017\nMulher sem cônjuge e com filho(s) até 14 anos\nMulher preta ou parda sem cônjuge e com filho(s) até 14 anos\nMulher branca sem cônjuge e com filho(s) até 14 anos\nCasal com filho(s)\nOutros\nUnipessoal\nCasal sem filho\n56,9%\n64,4%\n41,5%',
        template='{cut}',
        why="CAD_09_DIA_1_LARANJA_LEDOR p25 foot. 'Infografico intitulado Proporcao de pessoas abaixo da linha de pobreza' belongs to QUESTAO 63 (= 97262). 97262 ALREADY holds that infographic, but as a scrambled dump: TEXTO 2 lists '30,4% 21,0% 11,6% 10,0%', then the seven labels, then '56,9% 64,4% 41,5%'. Read in document order that pairs 'Mulher sem conjuge e com filho(s)' with 30,4 per cent when the printed figure is 56,9, and 'Mulher preta ou parda sem conjuge' with 21,0 instead of 64,4 -- and the item asks which factors INTENSIFY discrimination, so the scramble inverts the answer. The prose block carries the correct pairings, so it REPLACES the dump rather than joining it. Donor QUESTAO 64 (= 44230) is the Estado de direito item and its own question FOLLOWS the block, hence the explicit end anchor.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_cn__items.csv',
        op='move',
        donor='59858',
        recip='89518',
        cut_from='Descrição da imagem:\nCircuito elétrico composto por doi',
        where='before',
        at='Qual é a resistência equivalente',
        why="acc_d2 p6 foot. 'Circuito eletrico ... dois ramos ligados em paralelo ... chave A ... chave B' describes the RESISTIVE TOUCHSCREEN item, QUESTAO 106 (= 89518), printed earlier on the same page. The donor, QUESTAO 108 (= 59858), asks about the energy from oxidising glucose and has no circuit. Re-seated 2026-10-02: the block now lands before 89518's question instead of being appended after it, which is why 89518 no longer needs a KEEP entry.",
    ),
    dict(
        year='2018',
        csv='enem_2018_1mil_cn__items.csv',
        op='move',
        donor='111612',
        recip='111637',
        cut_from='Descrição do fluxograma:\nFluxograma cíclico composto po',
        where='before',
        at='Nesse ciclo, a formação de combustíveis',
        why="acc_d2 p15 foot. 'Fluxograma ciclico ... Processo 1 -> Combustiveis reduzidos e O2 -> Processo 2 -> CO2 e H2O' is the figure of QUESTAO 134 (= 111637), 'oxidacao de combustiveis, gerados no ciclo do carbono, por meio de processos capazes de interconverter ...'. The donor, QUESTAO 135 (= 111612), is about petroleum cracking. Re-seated 2026-10-02 to land before the question.",
    ),
    dict(
        year='2020',
        csv='enem_2020_1mil_mt__items.csv',
        op='move',
        donor='15897',
        recip='41676',
        cut_from='Descrição da imagem: O recipiente com indicação \nde águ',
        where='before',
        at='O número mínimo de bolinhas necessárias',
        why="CAD_11_DIA_2_LARANJA_LEDOR p18 foot. 'O recipiente com indicacao de agua a altura de 8 centimetros tem altura de 17 ... 4 ... 3' matches 41676, 'Num recipiente com a forma de paralelepipedo reto-retangulo, colocou-se agua ate a altura de 8 centimetros'. The donor, 15897, is a blood-type item. Re-seated 2026-10-02 to land before the question.",
    ),
]

# audit hits that are correct as printed -- item -> why
KEEP = {
    "78578": "2023: 'Descricao das alternativas' -- describes the five OPTIONS.",
    "141775": "2024: 'Descricao das alternativas' -- describes the five OPTIONS.",
    "87450": "2025: 'Descricao das alternativas' -- describes the five OPTIONS.",
    # a donor whose REMAINING block is legitimately its own. Listed here as
    # well as in OPS: being a donor already satisfies apply_ops, but that is
    # an accident of the refusal check, not a classification, and this pass
    # has to stay meaningful when re-run on its own output.
    "39342": "2018: after the schematics move to 111395, the block left on "
             "this item is its OWN artefact -- 'Um vaso de barro bojudo ... "
             "tubo de cobre ... barra de ferro' is the Baghdad battery the "
             "stem is about, printed after the question on acc_d2 p12.",
    "59546": "2020: the column-graph description IS this item's own data "
             "('Dia 1: 800 pecas ... Dia 1: 4 horas'), merely printed after the "
             "options. Verified on CAD_11_DIA_2_LARANJA_LEDOR p20.",
}


def _files(tables, items_dir):
    return (sorted(glob.glob(f"{items_dir}/*__items.csv")) if items_dir
            else sorted(glob.glob(f"{tables}/batch_enem_*/*__items.csv")))


def audit(tables, items_dir=None):
    out = []
    for f in _files(tables, items_dir):
        seen = set()
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r["item"] in seen:
                continue
            seen.add(r["item"])
            st = re.sub(r"\s+", " ", r.get("item_text") or "")
            ms = list(MARK.finditer(st))
            if not ms or ms[-1].start() < len(st) * 0.55:
                continue
            if CLOSER.search(st[:ms[-1].start()].rstrip()):
                out.append((f, r["item"], st[ms[-1].start():ms[-1].start() + 60]))
    return out


def _cut(dtxt, op):
    """Locate the block in the donor's stem. Both anchors must be unambiguous."""
    cf = op["cut_from"]
    if dtxt.count(cf) != 1:
        raise AssertionError(
            f"{op['donor']}: cut_from occurs {dtxt.count(cf)} times, need 1")
    lo = dtxt.index(cf)
    ct = op.get("cut_to")
    if ct is None:
        hi = len(dtxt)
    else:
        if dtxt.count(ct) != 1:
            raise AssertionError(
                f"{op['donor']}: cut_to occurs {dtxt.count(ct)} times, need 1")
        hi = dtxt.index(ct, lo + len(cf))
        if hi <= lo:
            raise AssertionError(f"{op['donor']}: cut_to precedes cut_from")
    rest = dtxt[hi:].lstrip()
    keep = dtxt[:lo].rstrip()
    if rest:
        keep = (keep + "\n" + rest) if keep else rest
    if not keep.strip():
        raise AssertionError(f"{op['donor']}: cut would empty the stem")
    return dtxt[lo:hi].strip(), keep


def _insert(rtxt, cut, op):
    """Place the block in the recipient at the verified anchor."""
    where = op["where"]
    if where == "start":
        return cut + "\n" + rtxt.lstrip()
    at = op["at"]
    if rtxt.count(at) != 1:
        raise AssertionError(
            f"{op['recip']}: anchor occurs {rtxt.count(at)} times, need 1")
    if where == "replace":
        return rtxt.replace(at, op["template"].format(cut=cut))
    i = rtxt.index(at)
    if where == "before":
        head = rtxt[:i].rstrip()
        return (head + "\n" + cut + "\n" + rtxt[i:]) if head else cut + "\n" + rtxt[i:]
    if where == "after":
        j = i + len(at)
        return rtxt[:j] + "\n" + cut + ("\n" + rtxt[j:].lstrip() if rtxt[j:].strip() else "")
    raise AssertionError(f"{op['recip']}: unknown where={where!r}")


def apply_ops(tables, items_dir=None, only_year=None):
    known = {o["donor"] for o in OPS} | set(KEEP)
    unknown = [(f, it, s) for f, it, s in audit(tables, items_dir) if it not in known]
    if unknown:
        print("REFUSING TO APPLY -- audit found cases not in OPS or KEEP:")
        for f, it, s in unknown:
            print(f"   {os.path.basename(f)} item {it}: {s}")
        print("\nVerify each against the printed page and add it to one of the "
              "two lists. Do not let this pass run on an unclassified case.")
        return 1
    n = skipped = 0
    for op in OPS:
        if items_dir and op["year"] != only_year:
            continue
        f = (f"{items_dir}/{op['csv']}" if items_dir
             else f"{tables}/batch_enem_{op['year']}/{op['csv']}")
        if not os.path.exists(f):
            continue
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        dtxt = next((r["item_text"] for r in rows if r["item"] == op["donor"]), None)
        if dtxt is None:
            print(f"   {op['year']} {op['donor']}: not found, skipped")
            skipped += 1
            continue
        if op["cut_from"] not in dtxt:
            print(f"   {op['year']} {op['donor']}: block already relocated, skipped")
            skipped += 1
            continue
        cut, keep = _cut(dtxt, op)
        ndon = sum(1 for r in rows if r["item"] == op["donor"])
        if op["op"] == "move":
            rtxt = next((r["item_text"] for r in rows if r["item"] == op["recip"]), None)
            if rtxt is None:
                print(f"   {op['year']} {op['recip']}: recipient not found -- NOT applied")
                skipped += 1
                continue
            nrec = sum(1 for r in rows if r["item"] == op["recip"])
            rewrite_field(f, rtxt, _insert(rtxt, cut, op), expect=nrec)
            rewrite_field(f, dtxt, keep, expect=ndon)
            print(f"   {op['year']} {op['donor']} -> {op['recip']}: "
                  f"moved {len(cut)} chars ({op['where']})")
        elif op["op"] == "drop":
            rewrite_field(f, dtxt, keep, expect=ndon)
            print(f"   {op['year']} {op['donor']}: dropped {len(cut)} chars "
                  f"(already in {op['recip']})")
        else:
            raise AssertionError(f"unknown op={op['op']!r}")
        n += 1
    print(f"\n{n} operation(s) applied, {skipped} skipped")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables")
    ap.add_argument("--items-dir", help="one year's out dir, as used by 42_rebuild.py")
    ap.add_argument("--year")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not (a.items_dir or a.tables):
        ap.error("give --tables or --items-dir")
    if a.items_dir and not a.year:
        ap.error("--items-dir needs --year")
    if a.apply:
        sys.exit(apply_ops(a.tables, a.items_dir, a.year))
    donors = {o["donor"] for o in OPS}
    for f, it, s in audit(a.tables, a.items_dir):
        tag = "OP" if it in donors else ("keep" if it in KEEP else "UNCLASSIFIED")
        print(f"  {os.path.basename(f):32} {it:>7} [{tag}] {s}")
