#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/dscr5n3jps
# DOI: 10.17632/dscr5n3jps (data)
#   Calluso C, Devetag MG (2024). The impact of Leadership Preferences and Personality Traits on Employees' Motivation
#   [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: "Dataset - Mendeley.xlsx", sheet Data: 150 Italian employees, interns and middle managers, the deposit's own
#   ID. Three Italian questionnaires, all observed on 1-5 (five-point agreement), headers = the Italian statements
#   (UTF-8 read as cp1252 in the file; kept as stored in RENAME):
# Tables:
#   _personality: 24 numbered statements ("1-Mi annoierei se visitassi una galleria d'arte" ...), which read as an
#     Italian Brief HEXACO Inventory (24 items); item = h1..h24 from the leading number. Stored raw: the reverse-worded
#     items are not reversed (e.g. item 4 "A nessuno piace parlare con me" correlates -0.31 with item 16 "Mi piace
#     parlare con gli altri").
#   _leadership: 30 numbered statements about what a leader should do; item = l1..l30 from the leading number.
#   _motivation: 30 unnumbered work-motivation statements, which read as an Italian Motivation Sources Inventory (five
#     sources x 6); item = m1..m30 in header order.
#   The instruments are IRW's identification from the stems; the deposit does not name them, so neither is split into
#   facets here.
# Covariates: cov_age (Età, years), cov_gender (Sesso), cov_occupation (Occupazione).
# PII: none (two short categorical text columns).
# Item text: not shipped -- the stems are the headers, but no anchors are given and the instruments are third-party
#   (an Italian BHI and MSI, by reading) with no register rows.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://data.mendeley.com/public-files/datasets/dscr5n3jps/files/f791fd01-183f-47ac-a877-9b9a16aea297/file_downloaded'
N_ROWS = 150
ID_COL = 'ID'
COVS = {'Età': 'cov_age', 'Sesso': 'cov_gender', 'Occupazione': 'cov_occupation'}
COV_MAPS = {'cov_gender': {'F': 'female', 'M': 'male'},
 'cov_occupation': {'Employee': 'employee', 'Intern': 'intern', 'Middle-Manager': 'middle_manager'}}
RENAME = {'1-Mi annoierei se visitassi una galleria dâ€™arte': 'h1',
 '2-Pianifico in anticipo per evitare di fare le cose allâ€™ultimo minuto': 'h2',
 '3-Raramente mantengo rancore, anche verso qualcuno che si Ã¨ comportato molto male con me': 'h3',
 '4-A nessuno piace parlare con me.': 'h4',
 '5-Ho molto paura di situazioni di pericolo fisico': 'h5',
 '6-Trovo difficile mentire': 'h6',
 '7-Penso che la scienza sia noiosa.': 'h7',
 '8-Rimando i compiti complicati il piÃ¹ a lungo possibile.': 'h8',
 '9-Le persone a volte mi dicono che critico troppo gli altri': 'h9',
 '10-Di solito sono il primo che si faâ€™ avanti in situazioni di tipo sociale': 'h10',
 '11-Penso di preoccuparmi meno della maggior parte delle persone': 'h11',
 '12-Non avrei problemi a rubare un milione di euro se sapessi per certo di non essere scoperto': 'h12',
 '13-La gente mi dice spesso che ho una immaginazione molto buona': 'h13',
 '14-Non pongo molta attenzione ai piccoli dettagli quando lavoro su qualcosa': 'h14',
 "15-Tendo ad essere subito d'accordo con gli altri.": 'h15',
 '16-Mi piace parlare con gli altri.': 'h16',
 '17-Riesco facilmente a superare le difficoltÃ\xa0 da solo.': 'h17',
 '18-Voglio essere famoso.': 'h18',
 '19-Mi piacciono le persone che hanno delle opinioni non conformiste': 'h19',
 '20-Mi piace fare la prima cosa che mi viene in mente piuttosto che seguire dei piani': 'h20',
 '21-Quando qualcuno che mi dice che ho torto, la mia prima reazione Ã¨ di controbattere': 'h21',
 '22-Raramente sono allegro.': 'h22',
 '23-Non mi emoziono neanche in situazioni dove la maggior parte delle persone diventa sentimentale': 'h23',
 '24-Penso di aver diritto ad un trattamento speciale.': 'h24',
 '1-Un leader cordiale con i membri del team Ã¨ molto influente': 'l1',
 '2-Un buon leader non esita ad accettare il suo errore in presenza dei membri': 'l2',
 "3- Un leader dovrebbe sempre gestire il suo gruppo tenendo conto dell'opinione dei membri.": 'l3',
 '4-Il leader Ã¨ onnipotente, puÃ² punire o premiare chiunque': 'l4',
 '5- Il leader dovrebbe decidere in quale modo  raggiungere gli obiettivi del gruppo, tenendo in considerazione il parere dei membri.': 'l5',
 '6-Il leader abile Ã¨ colui che decide tutte le politiche da solo.': 'l6',
 '7-Un leader dovrebbe sempre stare attento  che non ci sia tensione tra i membri': 'l7',
 "8-Un buon leader decide le politiche del gruppo solo in base all'opinione dei membri": 'l8',
 "9-Un leader dovrebbe prendere l'iniziativa nel momento del bisogno invece di chiedere il consenso degli altri": 'l9',
 '10-Un buon leader Ã¨ colui che guida i membri sulla politica e il modo che vuole e nessun membro si puÃ² opporre.': 'l10',
 '11-Un leader dovrebbe essere duro con i suoi critici.': 'l11',
 "12-Un leader dovrebbe agire secondo l'opinione della maggioranza dei membri": 'l12',
 '13-Un leader dovrebbe fornire i dettagli delle sue azioni e tenere allineati i membri': 'l13',
 '14-Un leader dovrebbe mantenere i membri divisi in molti gruppi.': 'l14',
 '15-Un leader non dovrebbe confessare i suoi errori in presenza dei membri': 'l15',
 "16-Un buon leader pianifica le linee del futuro programma del gruppo secondo l'opinione dei membri.": 'l16',
 '17-Un buon leader non puÃ² dire che un suo ordine possa essere disobbedito.': 'l17',
 "18-La leadership di un leader dipende dall'accordo reciproco dei membri.": 'l18',
 '19-Qualunque cosa dica il leader Ã¨ legge per i membri.': 'l19',
 "20-La divisione di un lavoro in tanti piccoli gruppi dovrebbe essere fatta dal leader secondo l'opinione dei membri.": 'l20',
 '21-Un leader dovrebbe stare attento che nessun altro membro del gruppo cerchi di diventare un leader.': 'l21',
 '22-In bisogno di un esperto il leader dovrebbe proporre nomi diversi in modo che i membri possano sceglierne uno.': 'l22',
 "23-Un leader dovrebbe onorare l'opinione dei suoi critici.": 'l23',
 "24-Un leader dovrebbe decidere secondo l'opinione dei membri quali persone scegliere per un lavoro.": 'l24',
 "25-Un leader dovrebbe mantenere la sua leadership approfittando della discordia e dell'inimicizia reciproca dei membri.": 'l25',
 "26-Un leader che lavora secondo l'opinione dei membri Ã¨ preda della corruzione.": 'l26',
 '27-Un leader dovrebbe fornire i dettagli dei futuri programmi del gruppo a tutti i membri.': 'l27',
 '28-Un leader che non considera i membri dovrebbe essere ugualmente un leader buono e di successo.': 'l28',
 '29-Un leader dovrebbe mantenere riservate ai membri la pianificazione e le politiche dei lavori.': 'l29',
 '30-Un leader dovrebbe lavorare secondo le sue opinioni, non dovrebbe chiedere frequentemente il parere dei suoi collaboratori.': 'l30',
 'Mi piace solo fare cose divertenti.': 'm1',
 'Se non mi piacesse il mio lavoro, mi licenzierei.': 'm2',
 "Spesso rimando il lavoro in modo da poter fare qualcos'altro che sia piÃ¹ divertente.": 'm3',
 'Quando scelgo il lavoro, di solito scelgo quello che sembra il piÃ¹ divertente.': 'm4',
 'Le persone con cui scelgo di trascorrere il mio tempo sono le piÃ¹ divertenti con cui stare.': 'm5',
 'Se si sceglie tra due lavori, il criterio piÃ¹ importante Ã¨ "quale Ã¨ il piÃ¹ divertente"?': 'm6',
 'I requisiti del lavoro determinano lo sforzo che esercito durante il lavoro.': 'm7',
 'Un giorno di lavoro per un giorno di paga.': 'm8',
 'Lavorerei di piÃ¹ se sapessi che i miei sforzi porterebbero a una paga piÃ¹ alta.': 'm9',
 'Quando scelgo i lavori di solito scelgo quello che paga di piÃ¹.': 'm10',
 'Al lavoro, il mio giorno preferito del mese Ã¨ "giorno di paga".': 'm11',
 'Le persone dovrebbero sempre tenere occhi e orecchie aperti per migliori opportunitÃ\xa0 di lavoro.': 'm12',
 'Per me Ã¨ importante che gli altri approvino il mio comportamento.': 'm13',
 'Spesso prendo decisioni in base a ciÃ² che pensano gli altri.': 'm14',
 'Lavoro di piÃ¹ su un progetto se ad esso Ã¨ associato un riconoscimento pubblico.': 'm15',
 'Se scelgo un lavoro ne voglio uno che mi permetta di essere riconosciuto per i successi.': 'm16',
 'Quelle persone che fanno piÃ¹ amicizie hanno vissuto la vita piÃ¹ piena.': 'm17',
 "Faccio del mio meglio quando so che sarÃ\xa0 visto dalle persone piÃ¹ influenti di un'organizzazione.": 'm18',
 'Le decisioni che prendo rifletteranno gli standard elevati che mi sono prefissato.': 'm19',
 "Ãˆ importante che io lavori per un'azienda che mi permetta di utilizzare le mie capacitÃ\xa0 e i miei talenti.": 'm20',
 'Cerco di assicurarmi che le mie decisioni siano coerenti con i miei standard di comportamento personali.': 'm21',
 'Mi reputo una persona auto-motivata.': 'm22',
 'Mi piace fare cose che mi danno un senso di realizzazione personale.': 'm23',
 "Ho bisogno di sapere che le mie capacitÃ\xa0 ei miei valori influiscono sul successo dell'organizzazione.": 'm24',
 "Non lavorerei per un'azienda se non fossi d'accordo con la sua mission.": 'm25',
 'Devo credere in una causa prima di lavorare sodo per raggiungere i suoi fini.': 'm26',
 'Se non credo nella causa, non lavoro duro.': 'm27',
 'Quando scelgo le aziende per cui lavorare, ne cerco una che supporti le mie convinzioni e i miei valori.': 'm28',
 'La mission aziendale deve essere in accordo con i miei valori per lavorare sodo.': 'm29',
 "Se un'organizzazione sta realizzando obbiettivi con cui sono d'accordo, non importa se sono stato responsabile del suo successo.": 'm30'}
BLOCKS = {'calluso_2024_personality': ['h1',
                              'h2',
                              'h3',
                              'h4',
                              'h5',
                              'h6',
                              'h7',
                              'h8',
                              'h9',
                              'h10',
                              'h11',
                              'h12',
                              'h13',
                              'h14',
                              'h15',
                              'h16',
                              'h17',
                              'h18',
                              'h19',
                              'h20',
                              'h21',
                              'h22',
                              'h23',
                              'h24'],
 'calluso_2024_leadership': ['l1',
                             'l2',
                             'l3',
                             'l4',
                             'l5',
                             'l6',
                             'l7',
                             'l8',
                             'l9',
                             'l10',
                             'l11',
                             'l12',
                             'l13',
                             'l14',
                             'l15',
                             'l16',
                             'l17',
                             'l18',
                             'l19',
                             'l20',
                             'l21',
                             'l22',
                             'l23',
                             'l24',
                             'l25',
                             'l26',
                             'l27',
                             'l28',
                             'l29',
                             'l30'],
 'calluso_2024_motivation': ['m1',
                             'm2',
                             'm3',
                             'm4',
                             'm5',
                             'm6',
                             'm7',
                             'm8',
                             'm9',
                             'm10',
                             'm11',
                             'm12',
                             'm13',
                             'm14',
                             'm15',
                             'm16',
                             'm17',
                             'm18',
                             'm19',
                             'm20',
                             'm21',
                             'm22',
                             'm23',
                             'm24',
                             'm25',
                             'm26',
                             'm27',
                             'm28',
                             'm29',
                             'm30']}
# (lo, hi) response range per table
RANGES = {'calluso_2024_personality': (1, 5), 'calluso_2024_leadership': (1, 5), 'calluso_2024_motivation': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name="Data")


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
    if ID_COL:
        assert d[ID_COL].is_unique, "duplicate ids"
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
    covs = list(COVS.values())
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
