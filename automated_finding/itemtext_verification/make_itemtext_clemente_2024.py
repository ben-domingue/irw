#!/usr/bin/env python3
"""Item text for the four clemente_2024 tables (10.1016/j.heliyon.2024.e36260).

Source: the article's own SI, mmc1.pdf (Europe PMC supplementaryFiles zip for
PMC11378926), which prints (a) the authors' English translation of the
attitude block and (b) the full Spanish questionnaire as administered in Spain
and Peru, including the SD4 and PMD blocks (the English part omits those two:
"The standardized questionnaires SD-4, PMD ... can be consulted in Spanish").

Administered language: Spanish. Base fields hold the Spanish wording verbatim
(typos kept: SD4 item 6 "Hacer halagos en una buena manera"). _translated:
  * attitude_father / attitude_mother: the authors' own English translation
    from the same PDF, verbatim (including "He Psychologically abuses",
    "She doesn't know how to educate his children").
  * sd4 / pmd: the SI has no English. The _translated fields are IRW's own
    rendering of the Spanish (not the published English SD4/PMD wording),
    disclosed in provenance and public_note.

Code-to-text tie (data/clemente_2024_divorced_parents.py keeps the .sav column
names as `item`):
  * FATHERk / MOTHERk = item k of the "Preguntas sobre el padre/la madre"
    block. The .sav variable labels agree with the printed item at the same
    position for k != 9; FATHER9/MOTHER9 are labelled "Does not see child",
    which matches no printed item, and are tied to printed item 9 by position.
  * SD4_k = item k of the SD4 block (positional; verify_clemente_2024_sd4.R).
  * PMD columns are named by mechanism (Moral_justification ...
    Attribution_of_blame), in the order of Moore et al.'s (2012) 8-item PMD,
    which is the printed order of items 1-8 here; item 9 is the attention check.
Every Spanish string below is asserted to occur, in block order, in the PDF.
"""
import csv
import io
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11378926/supplementaryFiles"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

PARENT_ES = [
    "Sus hijos no le quieren", "No sabe educarles", "Es posible que les agreda físicamente",
    "Les maltrata psicológicamente", "No les cuida adecuadamente",
    "No aporta dinero para su cuidado, si es su obligación", "Es raro que les haga regalos",
    "Es raro que les llame telefónicamente cuando no está con ellos",
    "Creo que no quiere a sus hijos",
    "Creo que utiliza a sus hijos para ir contra el otro progenitor"]
FATHER_EN = [
    "The children do not love this parent", "He doesn't know how to educate his children",
    "He may physically attack his children", "He Psychologically abuses his children",
    "He does not take proper care of his children",
    "He does not contribute money for the care of his children, if it is his obligation",
    "It is rare that he gives gifts to his children",
    "It is rare that he calls his children when he is not with them.",
    "I believe that he/she does not love his/her children.",
    "I think he uses his children to go against the other parent"]
MOTHER_EN = [
    "The children do not love this parent", "She doesn't know how to educate his children",
    "She may physically attack his children", "She Psychologically abuses his children",
    "She does not take proper care of his children",
    "She does not contribute money for the care of his children, if it is his obligation",
    "It is rare that She gives gifts to his children",
    "It is rare that She calls his children when She is not with them.",
    "I believe that he/she does not love his/her children.",
    "I think She uses his children to go against the other parent"]
PARENT_INSTR_ES = ("A continuación le vamos a efectuar unas preguntas referentes a los padres "
                   "de los niños, a las madres, a los niños y a usted. Responda según la escala "
                   "desde “muy de acuerdo” a “muy en desacuerdo”.")
PARENT_INSTR_EN = ("Next we are going to ask you some questions regarding the children's fathers, "
                   "the mothers, the children and you. Respond according to the scale from "
                   "“strongly agree” to “strongly disagree.”")
OPT5_ES = ["Completamente en desacuerdo", "En desacuerdo", "Ni de acuerdo ni en desacuerdo",
           "De acuerdo", "Completamente de acuerdo"]
OPT5_PARENT_EN = ["Completely disagree", "Disagreement", "Neither agree nor disagree",
                  "Agree", "Completely agree"]
OPT5_IRW_EN = ["Completely disagree", "Disagree", "Neither agree nor disagree", "Agree",
               "Completely agree"]

SD4_ES = [
    "No es prudente/inteligente dejar que la gente conozca tus secretos.",
    "Debes tener a gente importante de tu parte, cueste lo que cueste.",
    "Evita los conflictos directos con los demás porque pueden serte útiles en el futuro.",
    "Mantén un perfil bajo si quieres salirte con la tuya.",
    "Manipular la situación requiere planificación.",
    "Hacer halagos en una buena manera de conseguir que la gente se ponga de tu lado.",
    "Me encanta cuando un plan tramposo tiene éxito.",
    "La gente me ve como un líder natural.",
    "Tengo un talento único para persuadir a la gente.",
    "Las actividades grupales suelen ser aburridas sin mí.",
    "Sé que soy especial porque la gente me lo dice continuamente.",
    "Tengo algunas cualidades excepcionales.",
    "Es probable que acabe siendo una estrella en algún ámbito.",
    "Me gusta lucirme de vez en cuando.",
    "La gente suele decir que estoy fuera de control.",
    "Tiendo a ir en contra de las autoridades y sus reglas.",
    "He estado en más peleas que la mayoría de la gente de mi edad y sexo.",
    "Tiendo a lanzarme primero y hacer preguntas después.",
    "He tenido problemas con la ley.",
    "A veces me meto en situaciones peligrosas.",
    "La gente que se mete conmigo siempre se arrepiente.",
    "Ver una pelea a puñetazos me emociona/excita.",
    "Realmente disfruto con películas y videojuegos violentos.",
    "Es divertido cuando gente idiota se cae de bruces.",
    "Disfruto viendo deportes violentos.",
    "Algunas personas merecen sufrir.",
    "He dicho cosas malas en las redes sociales solo por diversión.",
    "Sé cómo herir a alguien sólo con palabras."]
SD4_EN = [  # IRW's rendering of the Spanish, not the published English SD4
    "It is not prudent/smart to let people know your secrets.",
    "You should have important people on your side, whatever it costs.",
    "Avoid direct conflict with others because they may be useful to you in the future.",
    "Keep a low profile if you want to get your way.",
    "Manipulating the situation takes planning.",
    "Flattery is a good way to get people on your side.",
    "I love it when a tricky plan succeeds.",
    "People see me as a natural leader.",
    "I have a unique talent for persuading people.",
    "Group activities tend to be boring without me.",
    "I know that I am special because people keep telling me so.",
    "I have some exceptional qualities.",
    "I am likely to end up being a star in some area.",
    "I like to show off now and then.",
    "People often say I am out of control.",
    "I tend to go against authorities and their rules.",
    "I have been in more fights than most people of my age and sex.",
    "I tend to dive in first and ask questions later.",
    "I have had problems with the law.",
    "I sometimes get into dangerous situations.",
    "People who mess with me always regret it.",
    "Watching a fistfight thrills/excites me.",
    "I really enjoy violent films and video games.",
    "It is funny when idiots fall flat on their face.",
    "I enjoy watching violent sports.",
    "Some people deserve to suffer.",
    "I have said mean things on social media just for fun.",
    "I know how to hurt someone with words alone."]
SD4_INSTR_ES = ("Indique su grado de acuerdo con cada una de las siguientes afirmaciones. "
                "Para ello tenga en cuenta la siguiente valoración:")
SD4_INSTR_EN = ("Indicate how much you agree with each of the following statements, "
                "using the following rating:")

PMD_COLS = ["Moral_justification", "Euphemistic_labelling", "Advantageous_comparison",
            "Displacement_of_responsability", "Difussion_of_responsability",
            "Distortion_of_consequences", "Dehumanization", "Attribution_of_blame"]
PMD_ES = [
    "Está justificado contar chismes de otros si eso protege a las personas que te importan.",
    "Coger algo sin el permiso del dueño no está mal mientras solamente lo hayas cogido prestado.",
    "Teniendo en cuenta como la gente exagera sobre ellos mismos, no es ningún pecado “inflar” "
    "un poco nuestro currículo.",
    "Las personas no deberían considerarse responsables de hacer cosas incorrectas cuando "
    "simplemente hacen lo que les dice una autoridad.",
    "No se puede culpar a la gente de cosas que están técnicamente mal si todos sus amigos "
    "hacen lo mismo.",
    "Decir que se te han ocurrido a ti ideas que son de otros no es para tanto.",
    "Algunas personas tienen que ser tratadas duramente porque no tienen sentimientos que "
    "puedan ser heridos.",
    "La gente que es maltratada normalmente hace cosas para merecérselo."]
PMD_EN = [  # IRW's rendering of the Spanish, not the published English PMD
    "It is justified to gossip about others if that protects the people you care about.",
    "Taking something without the owner's permission is not wrong as long as you have only "
    "borrowed it.",
    "Considering how people exaggerate about themselves, it is no sin to \"inflate\" our "
    "résumé a little.",
    "People should not be considered responsible for doing wrong things when they are simply "
    "doing what an authority tells them.",
    "People cannot be blamed for doing things that are technically wrong if all their friends "
    "do the same.",
    "Saying that ideas that are other people's came to you is no big deal.",
    "Some people have to be treated harshly because they have no feelings that can be hurt.",
    "People who are mistreated usually do things to deserve it."]
PMD_INSTR_ES = ("Nos gustaría saber el grado de acuerdo o desacuerdo en el que se encuentra "
                "con respecto a las siguientes afirmaciones. Por favor, indique la puntuación "
                "correspondiente en la escala que se presenta a continuación:")
PMD_INSTR_EN = ("We would like to know how much you agree or disagree with the following "
                "statements. Please indicate the corresponding score on the scale below:")
OPT7_ES = ["Totalmente en desacuerdo", "Bastante en desacuerdo", "En desacuerdo",
           "Ni de acuerdo ni en desacuerdo", "De acuerdo", "Bastante de acuerdo",
           "Totalmente de acuerdo"]
OPT7_EN = ["Totally disagree", "Quite disagree", "Disagree", "Neither agree nor disagree",
           "Agree", "Quite agree", "Totally agree"]


def norm(s: str) -> str:
    s = re.sub(r"(?<!\S)[1-7](?!\S)", " ", s)      # strip the printed 1..7 answer grid
    return re.sub(r"\s+", " ", s).strip()


def pdf_text() -> str:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    blob = zipfile.ZipFile(io.BytesIO(r.content)).read("mmc1.pdf")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(blob)
        f.flush()
        return norm(subprocess.run(["pdftotext", f.name, "-"], check=True,
                                   capture_output=True, text=True).stdout)


def in_order(txt: str, start: int, strings: list) -> int:
    pos = start
    for s in strings:
        i = txt.find(norm(s), pos)
        assert i >= 0, ("not found in order", s, pos)
        pos = i + len(norm(s))
    return pos


def main() -> None:
    txt = pdf_text()
    es = txt.index("Preguntas sobre el padre de los niños:")
    assert norm(PARENT_INSTR_ES) in txt[:es]
    in_order(txt, es, PARENT_ES)
    ma = txt.index("Preguntas sobre la madre de los niños:")
    in_order(txt, ma, PARENT_ES)
    en = txt.index("Questions about the children's father:")
    assert norm(PARENT_INSTR_EN) in txt[:en]
    p = in_order(txt, en, FATHER_EN)
    in_order(txt, p, MOTHER_EN)
    sd = txt.index("SD4. Indique")
    in_order(txt, sd, [SD4_INSTR_ES] + OPT5_ES + SD4_ES)
    pm = txt.index("PMD. Nos")
    in_order(txt, pm, [PMD_INSTR_ES] + OPT7_ES + PMD_ES)

    specs = {
        "clemente_2024_attitude_father": dict(
            instrument="Attitudes toward the children's father after divorce (Clemente et al., 10 items)",
            items=[f"FATHER{i}" for i in range(1, 11)], es=PARENT_ES, en=FATHER_EN,
            instr=(PARENT_INSTR_ES, PARENT_INSTR_EN),
            prompt=("Preguntas sobre el padre de los niños:", "Questions about the children's father:"),
            opts=(OPT5_ES, OPT5_PARENT_EN)),
        "clemente_2024_attitude_mother": dict(
            instrument="Attitudes toward the children's mother after divorce (Clemente et al., 10 items)",
            items=[f"MOTHER{i}" for i in range(1, 11)], es=PARENT_ES, en=MOTHER_EN,
            instr=(PARENT_INSTR_ES, PARENT_INSTR_EN),
            prompt=("Preguntas sobre la madre de los niños:", "Questions about the children’s mother:"),
            opts=(OPT5_ES, OPT5_PARENT_EN)),
        "clemente_2024_sd4": dict(
            instrument="Short Dark Tetrad (SD4; Paulhus et al., 2021), Spanish version",
            items=[f"SD4_{i}" for i in range(1, 29)], es=SD4_ES, en=SD4_EN,
            instr=(SD4_INSTR_ES, SD4_INSTR_EN), prompt=(None, None),
            opts=(OPT5_ES, OPT5_IRW_EN)),
        "clemente_2024_pmd": dict(
            instrument="Propensity to Morally Disengage scale (PMD-8; Moore et al., 2012), Spanish version",
            items=PMD_COLS, es=PMD_ES, en=PMD_EN,
            instr=(PMD_INSTR_ES, PMD_INSTR_EN), prompt=(None, None),
            opts=(OPT7_ES, OPT7_EN)),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, s in specs.items():
        resp = pd.read_csv(HERE / "irw_output" / f"{table}.csv")
        assert set(resp["item"]) == set(s["items"]), table
        ok_es, ok_en = s["opts"]
        assert set(resp["resp"]) <= set(range(1, len(ok_es) + 1)), table
        rows = []
        for k, item in enumerate(s["items"]):
            for v, (o_es, o_en) in enumerate(zip(ok_es, ok_en), start=1):
                rows.append([table, f"{table}_1", item, s["instrument"], "Spanish",
                             s["instr"][0], s["prompt"][0], s["es"][k], None, o_es, v,
                             s["instr"][1], s["prompt"][1], s["en"][k], o_en])
        out = pd.DataFrame(rows, columns=COLS)
        out.to_csv(OUT_DIR / f"{table}__items.csv", index=False,
                   quoting=csv.QUOTE_NONNUMERIC, na_rep="NA")
        print(f"{table}__items.csv: {len(out)} rows, {out['item'].nunique()} items")


if __name__ == "__main__":
    main()
