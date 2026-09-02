#!/usr/bin/env python3
"""Rebuild three published itemtext tables under the administered-language schema (irw#1777).

Reads the currently published curation (staging/<table>__published.csv, pulled with
irw::irw_itemtext) and writes staging/<table>__items.csv with the administered wording in
the base text fields, the English in the _translated twins, and `language` naming the
administered language. `item` and `resp` are never touched.
"""
import csv, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE_IN = os.path.join(HERE, "published")
STAGE = os.path.join(HERE, "staging")
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

def read_published(t):
    with open(os.path.join(STAGE_IN, f"{t}__published.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write(t, rows):
    with open(os.path.join(STAGE, f"{t}__items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "NA") for c in COLS})

# --------------------------------------------------------------------------------------
# baaziz_2023_sms2 -- Arabic. PLOS ONE 10.1371/journal.pone.0295262 Table 7 prints every
# item in Arabic with the authors' own English underneath; item numbers 1-18 are the
# table's Item1..Item18. Arabic taken verbatim from the article XML, not OCR.
# --------------------------------------------------------------------------------------
SMS2_AR = {
 1: "لأنه يسعدني معرفة المزيد عن رياضتي",
 2: "لأنه من المثير للاهتمام معرفة كيف يمكنني التحسين",
 3: "لأنني أجد أنه من الممتع اكتشاف استراتيجيات جديدة للأداء",
 4: "لأن ممارسة الرياضة تعكس جوهر من أنا",
 5: "لأنني من خلال الرياضة، أعيش وفقاً لمبادئي العميقة",
 6: "لأن المشاركة في الرياضة جزء لا يتجزأ من حياتي",
 7: "لأنني اخترت هذه الرياضة كوسيلة لتطوير نفسي",
 8: "لأنها من أفضل الطرق التي اخترتها لتطوير جوانب أخرى من نفسي",
 9: "لأنني وجدت أنها طريقة جيدة لتطوير جوانب من نفسي التي أقدرها",
 10: "لأنني سأشعر بالضيق تجاه نفسي إذا لم آخذ الوقت الكافي للقيام بذلك",
 11: "لأنني أشعر بتحسن تجاه نفسي عندما أفعل ذلك",
 12: "لأنني لن أشعر بأي قيمة إذا لم أفعل ذلك",
 13: "لأن الناس من حولي يكافئونني عندما أفعل ذلك",
 14: "لأنني أعتقد أن الآخرين سوف يرفضونني إذا لم أفعل ذلك",
 15: "لأن الأشخاص الذين أهتم بهم سينزعجون مني إذا لم أفعل ذلك",
 16: "حتى يمدحني الآخرون لما أقوم به",
 17: "لم يعد واضحًا بالنسبة إلي، لا أعتقد حقا أن مكاني هو الرياضة",
 18: "كان لدي أسباب وجيهة لممارسة الرياضة، لكنني الآن أسأل نفسي إذا كان ينبغي علي الاستمرار",
}

def build_baaziz():
    t = "baaziz_2023_sms2"
    rows = read_published(t)
    out = []
    for r in rows:
        n = int(re.match(r"Item(\d+)$", r["item"]).group(1))
        r = dict(r)
        r["language"] = "Arabic"
        r["item_text_translated"] = r["item_text"]   # the paper's own English back-translation
        r["item_text"] = SMS2_AR[n]
        # The paper gives the 1-7 anchors only in English ("Not at all true" / "Very true");
        # no Arabic anchors appear in the article or its supplements, so option_text keeps the
        # English and its _translated twin stays empty -- the documented signal that those
        # words are not what respondents read.
        r["option_text_translated"] = "NA"
        r["instructions_translated"] = "NA"
        r["section_prompt_translated"] = "NA"
        out.append(r)
    write(t, out)
    return t, len(out)

# --------------------------------------------------------------------------------------
# brederecke_2020_sis -- German. PLOS ONE 10.1371/journal.pone.0230331 Table 3 is headed
# "Original item (German version)" and prints each item as English followed by the
# administered German in parentheses. The published table shipped that whole string in
# item_text; this splits it.
# --------------------------------------------------------------------------------------
def build_brederecke():
    t = "brederecke_2020_sis"
    rows = read_published(t)
    out = []
    for r in rows:
        r = dict(r)
        m = re.match(r"^(.*?)\s*\((.*)\)\s*$", r["item_text"], re.S)
        if not m:
            raise SystemExit(f"{t}: could not split {r['item']}: {r['item_text']!r}")
        eng, ger = m.group(1).strip(), m.group(2).strip()
        r["language"] = "German"
        r["item_text"] = ger
        r["item_text_translated"] = eng
        # The paper states the five-point anchors only in English ("strongly disagree" /
        # "strongly agree"), and the study's own .sav labels its values "1".."5" with no
        # anchor text, so the German anchors are not recoverable in-source.
        r["option_text_translated"] = "NA"
        r["instructions_translated"] = "NA"
        r["section_prompt_translated"] = "NA"
        out.append(r)
    write(t, out)
    return t, len(out)

# --------------------------------------------------------------------------------------
# arzamoncunill_2023_epq_clinical -- Spanish. PeerJ 10.7717/peerj.16246 Appendix S3 is the
# final administered questionnaire in Spanish. The IRW table holds all 22 clinical-care
# items of the 43-item pretest pool; only the 12 that survived into the final questionnaire
# have published Spanish wording. The remaining 10 keep the English category descriptor from
# Appendix S5, with an empty _translated twin.
#
# The E-code <-> Spanish tie: Appendix S5 maps each pool item NUMBER to its English category
# descriptor (E1 = "Editable agenda", E25 = "Videoconference", ...), and each S3 Spanish item
# matches exactly one of those descriptors by content. Two of the twelve are corroborated
# outright by Appendix S1, which prints the pre-pretest and final wording side by side in
# both languages.
# --------------------------------------------------------------------------------------
EPQ_ES = {
 "E15": ("Acceder a plantillas de mapas corporales (u otras herramientas similares) que puedan usarse al explorar a un paciente",
         "Access body-chart templates (or other similar tools) that can be used when examining a patient", "own"),
 "E14": ("Acceder a cuestionarios (p.ej. EVA, NDI, DASH, SF-36) que puedan usarse para medir la funcionalidad de un paciente",
         "Access questionnaires (e.g., VAS, NDI, DASH, SF-36) that can be used to measure a patient's functionality", "authors"),
 "E18": ("Acceder a plantillas editables para emitir informes (p.ej. clínico-legales, mutuas) a empresas/clientes que lo solicitan",
         "Access editable templates for issuing reports (e.g. medico-legal, insurers) to companies/clients that request them", "own"),
 "E16": ("Acceder a plantillas que definen la anamnesis y exploración a pacientes con patologías concretas",
         "Access templates that define the history-taking and examination for patients with particular conditions", "own"),
 "E17": ("Acceder a plantillas de ejercicios terapéuticos (o pautas) para seleccionar y personalizar un programa a su paciente",
         "Access therapeutic exercise templates (or guidelines) to select and personalise a programme for your patient", "own"),
 "E23": ("Generar periódicamente informes de la calidad asistencial prestada en el centro (p.ej. resultados de encuestas de satisfacción)",
         "Periodically generate reports on the quality of care provided at the centre (e.g. satisfaction survey results)", "own"),
 "E22": ("Generar periódicamente informes de la actividad asistencial prestada en el centro (p.ej. número de pacientes por patologías, nº de sesiones)",
         "Periodically generate reports on the healthcare activity provided at the centre (e.g. number of patients by condition, number of sessions)", "own"),
 "E24": ("Generar periódicamente informes de la seguridad de los pacientes en el centro (p.ej. incidencia de efectos adversos, caídas)",
         "Periodically generate reports on patient safety at the centre (e.g. incidence of adverse events, falls)", "own"),
 "E25": ("Realizar videollamadas con pacientes u otros profesionales",
         "Hold video calls with patients or other professionals", "own"),
 "E26": ("Chatear con uno o más pacientes en tiempo real",
         "Chat with one or more patients in real time", "own"),
 "E31": ("Que sus pacientes puedan reservar online una cita",
         "For your patients to book an appointment online", "authors"),
 "E32": ("Que sus pacientes puedan consultar online las fechas de las visitas pendientes o realizadas",
         "For your patients to check online the dates of pending or completed visits", "own"),
}
EPQ_INSTR_ES = "EL SOFTWARE DESEABLE PARA SU CENTRO DEBERÍA PERMITIR...."

def build_arza():
    t = "arzamoncunill_2023_epq_clinical"
    rows = read_published(t)
    out = []
    for r in rows:
        r = dict(r)
        r["language"] = "Spanish"
        # Appendix S3 carries the administered Spanish stem; Appendix S1 supplies the
        # authors' own English for it.
        r["instructions"] = EPQ_INSTR_ES
        r["instructions_translated"] = "The desirable software for your center should allow..."
        r["section_prompt_translated"] = "NA"
        r["option_text_translated"] = "NA"   # anchors published in English only
        if r["item"] in EPQ_ES:
            es, en, _ = EPQ_ES[r["item"]]
            r["item_text"] = es
            r["item_text_translated"] = en
        else:
            # No published wording in any language; the English category descriptor stands,
            # and the empty twin marks it as not the administered wording.
            r["item_text_translated"] = "NA"
        out.append(r)
    write(t, out)
    return t, len(out)

if __name__ == "__main__":
    for fn in (build_baaziz, build_brederecke, build_arza):
        t, n = fn()
        print(f"wrote staging/{t}__items.csv  ({n} rows)")
