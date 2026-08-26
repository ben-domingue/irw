"""
irw_discover.py
===============
Discovery-only pipeline for finding candidate datasets to contribute to the
Item Response Warehouse (IRW). No scoring, no validation, no coercion — its one
job is to cast a wide net across open-data repositories and hand you a clean,
deduplicated list of candidates to review by hand.

Three things this does that a naive search doesn't:
  - SOURCES   : queries 5 repositories, not 1 (breadth = recall)
  - PAGINATION: walks every page per source, so you don't miss results
  - DEDUP     : merges by DOI across sources, falls back to title
  - EXCLUDE   : automatically skips datasets already in the IRW, or already
                logged as a genuinely-ambiguous human_review row in a past
                batch. The exclusion set is fetched live from the IRW
                dictionary Google Sheet plus every doi column found under
                human_review/*.csv on every run (_load_auto_exclusions()) —
                no local file to maintain. (The processing-queue "to be
                processed" sheet was dropped from this check 2026-07-14 --
                it's a manually maintained tab other contributors use, not
                something this pipeline's own good/worth_retrying candidates
                ever land in, so treating it as an exclusion source no
                longer made sense. The "human eye" tab of that same queue
                sheet was deprecated entirely 2026-08-12 in favor of
                human_review/*.csv, which is what's now used for exclusion
                instead.)

Run:
    python irw_discover_updated.py "self-efficacy scale" "reading assessment"
    python irw_discover_updated.py --all "questionnaire"   # disable relevance filter
    python irw_discover_updated.py --since 2026-07-01 "personality scale"  # only hits published/created on or after this date
"""

from __future__ import annotations

import os
import sys
import re
import csv
import glob
import time
import argparse
from dataclasses import dataclass, asdict

import requests

UA = {"User-Agent": "irw-discovery-scout/1.0 (research; contact itemresponsewarehouse@stanford.edu)"}

# Source connectors raise this to signal a hard block (e.g. an AWS WAF
# bot-challenge) rather than a transient error -- retrying within this run
# won't help. discover() catches it, stops calling that source for the rest
# of the run (across all remaining queries/terms), and logs it once instead
# of eating a wasted, silently-failing request per query. See dataverse
# 2026-08-14 WAF block (BATCH_LOG.md) for the incident that prompted this.
class SourceBlocked(Exception):
    pass


_blocked_sources: set[str] = set()


def blocked_sources() -> set[str]:
    """Short names (as in SOURCE_MAP / --sources) of every source that hit a
    hard block so far in this process.

    Callers that record what they searched MUST subtract this before writing
    that record down: a source that WAF-challenged every request was not
    actually searched, and any bookkeeping that treats it as searched (an
    incremental --since watermark, a seen-key ledger) will silently skip that
    window forever. See irw_discover_monthly.py's log rows for the consumer,
    and BATCH_LOG.md's 2026-08-17 entry for the run where this went wrong."""
    return {name.replace("from_", "", 1) for name in _blocked_sources}

# ---------------------------------------------------------------------------
# RELEVANCE FILTER (tiered)
# ---------------------------------------------------------------------------
# IRW membership is STRUCTURAL (person x item x ordinal response), not topical,
# and a title can't reveal structure — so this filter's job is RECALL: let real
# data through and only block the obvious noise. The triage stage does the
# precision work (content gate + format validator).
#
# How matching works:
#   * a title with ANY strong or construct term  -> PASS
#   * ambiguous terms ("test", "scale", "survey") do NOT pass on their own,
#     because alone they match geology surveys, stress tests, soil scales, etc.
#     They only add confidence alongside a strong/construct term.
#
# To tune: add the construct words for the domains you care about, or move a
# word between tiers. To turn the filter off entirely, run with --all.

STRONG_TERMS = [          # psychometric structure/method — rarely outside the field
    "item response", "item-level", "item response theory", "irt", "rasch",
    "psychometric", "questionnaire", "likert", "self-report", "factor analysis",
    "latent trait", "test battery", "item bank", "polytomous", "dichotomous",
    "construct validity", "measurement invariance", "response data",
    "reaction time", "response latency", "curriculum-based measurement",
]
CONSTRUCT_TERMS = [       # things the IRW actually measures (its construct_type tags)
    # education / ability
    "ability", "aptitude", "achievement", "proficiency", "numeracy", "literacy",
    "vocabulary", "reading comprehension", "grammar", "arithmetic", "spelling",
    "intelligence", "cognitive", "working memory", "knowledge test",
    "phonological awareness", "reading fluency", "mathematics achievement",
    "science achievement",
    # executive function / cognitive control
    "executive function", "inhibitory control", "cognitive flexibility",
    "task switching", "set shifting", "processing speed",
    # personality / clinical
    "personality", "big five", "depression", "anxiety", "well-being", "wellbeing",
    "self-esteem", "mood", "affect", "temperament", "psychopathology",
    "quality of life", "fear of missing out",
    # attitudes / other
    "attitude", "partisanship", "preference",
]
AMBIGUOUS_TERMS = [       # match too much alone; only count WITH a term above
    "test", "scale", "survey", "assessment", "rating", "inventory",
    "responses", "measure", "score", "battery",
]

# TRANSLATED STRONG/CONSTRUCT TERMS.
# Every discovery batch is supposed to run each English term in 8 more
# languages (see SKILL.md Step 1), but this filter reads the *title* of the
# hit, and a Spanish/German/Chinese repository record has a Spanish/German/
# Chinese title. With an English-only vocabulary the gate discarded almost
# every non-English hit before triage ever saw it -- the only ones that got
# through were titles carrying a Latin-script instrument name ("Rosenberg").
# That silently nullified ~1,200 non-English queries run in 2026-06/07.
# These are deliberately the same tier as STRONG/CONSTRUCT: translations of
# generic ambiguous words ("test", "escala", "問卷") are NOT here, for the
# same reason AMBIGUOUS_TERMS aren't.
TRANSLATED_TERMS_LATIN = [
    # es
    "respuesta al ítem", "psicométric", "cuestionario", "autoinforme",
    "análisis factorial", "rendimiento académico", "comprensión lectora",
    "vocabulario", "competencia lingüística", "razonamiento", "habilidad espacial",
    "autoestima", "depresión", "ansiedad", "bienestar", "personalidad",
    "motivación", "resiliencia", "calidad de vida", "soledad", "agotamiento",
    "inteligencia", "aptitud", "conocimientos previos", "alfabetización",
    # de
    "itemantwort", "psychometri", "fragebogen", "selbstbericht",
    "faktorenanalyse", "schulleistung", "leseverständnis", "wortschatz",
    "sprachkompetenz", "denkaufgaben", "räumliches vorstellungsvermögen",
    "selbstwertgefühl", "depressiv", "angst", "wohlbefinden", "persönlichkeit",
    "motivation", "resilienz", "lebensqualität", "einsamkeit", "burnout",
    "intelligenz", "kompetenzmessung", "leistungstest",
    # fr
    "réponse à l'item", "psychométri", "questionnaire", "auto-évaluation",
    "analyse factorielle", "rendement scolaire", "compréhension écrite",
    "vocabulaire", "compétence linguistique", "raisonnement", "capacité spatiale",
    "estime de soi", "dépression", "anxiété", "bien-être", "personnalité",
    "motivation", "résilience", "qualité de vie", "solitude", "épuisement",
    "intelligence", "aptitude",
    # nl
    "itemrespons", "psychometri", "vragenlijst", "zelfrapportage",
    "factoranalyse", "schoolprestatie", "begrijpend lezen", "woordenschat",
    "taalvaardigheid", "redeneer", "ruimtelijk inzicht", "zelfwaardering",
    "depressie", "angst", "welbevinden", "persoonlijkheid", "motivatie",
    "veerkracht", "levenskwaliteit", "eenzaamheid", "burn-out", "intelligentie",
    "vaardigheidstoets", "leerlingtoets",
]
# Scripts with no word boundaries (\b never fires between two CJK/Arabic
# characters, so these must be matched as bare substrings).
TRANSLATED_TERMS_NOBOUNDARY = [
    # zh
    "项目反应", "心理测量", "问卷", "自评", "因素分析", "学业成就", "成就测验",
    "阅读理解", "词汇", "语言能力", "推理", "空间能力", "自尊", "抑郁", "焦虑",
    "幸福感", "人格", "动机", "心理韧性", "生活质量", "孤独", "倦怠", "智力",
    "认知测验", "学生评估", "量表信效度",
    # ja
    "項目反応", "心理測定", "質問紙", "自己報告", "因子分析", "学業成績",
    "学力テスト", "読解力", "語彙", "言語能力", "推論", "空間能力", "自尊感情",
    "抑うつ", "不安", "幸福感", "性格", "動機づけ", "レジリエンス", "生活の質",
    "孤独感", "バーンアウト", "知能", "認知テスト",
    # ko
    "문항반응", "심리측정", "설문", "자기보고", "요인분석", "학업성취",
    "성취도 검사", "읽기 이해", "어휘", "언어 능력", "추론", "공간 능력",
    "자아존중감", "우울", "불안", "행복", "성격", "동기", "회복탄력성",
    "삶의 질", "외로움", "소진", "지능", "인지 검사",
    # ar
    "استجابة المفردة", "القياس النفسي", "استبيان", "التقرير الذاتي",
    "التحليل العاملي", "التحصيل الدراسي", "الفهم القرائي", "المفردات",
    "الكفاءة اللغوية", "الاستدلال", "القدرة المكانية", "تقدير الذات",
    "الاكتئاب", "القلق", "الرفاهية", "الشخصية", "الدافعية", "المرونة النفسية",
    "جودة الحياة", "الوحدة", "الاحتراق النفسي", "الذكاء",
]

# EXCLUSIONS: clinical/epidemiology study language. A construct word like
# "depression" pulls in huge amounts of MEDICAL research that studies the
# outcome without measuring it via item responses (e.g. "aspirin and risk of
# depression"). A title with any of these is blocked even if it names a
# construct, because it's a study ABOUT a condition, not item-response data.
EXCLUDE_TERMS = [
    "risk of", "cross-sectional", "case-control", "cohort study",
    "odds ratio", "hazard ratio", "relative risk", "prevalence", "incidence",
    "mortality", "meta-analysis", "systematic review", "biomarker",
    "comorbidit", "all-cause", "etiology", "aetiology", "pathogenesis",
    "association between",
]

# WIDELY-USED INSTRUMENTS — named scales used across thousands of studies.
# An instrument name is the highest-precision signal there is: a title saying
# "PHQ-9" or "Rosenberg" is almost certainly real item-response data. These
# pass on their own and also catch acronym-only titles (TROG, WAIS) that the
# construct terms miss. Add the instruments for the constructs you care about.
INSTRUMENT_TERMS = [
    # personality
    "big five inventory", "bfi", "neo-pi", "neo-ffi", "ipip", "hexaco",
    "eysenck personality", "epq", "16pf", "mbti", "dark triad", "sd3",
    "dirty dozen",
    # depression
    "beck depression", "bdi", "phq-9", "phq", "ces-d", "hamilton depression",
    "madrs", "geriatric depression", "gds",
    # anxiety
    "gad-7", "state-trait anxiety", "stai", "beck anxiety", "bai",
    "hospital anxiety and depression", "hads",
    # affect / well-being / life satisfaction
    "panas", "positive and negative affect", "satisfaction with life", "swls",
    "warwick-edinburgh", "wemwbs", "ryff",
    # self-esteem / stress / resilience / burnout / loneliness
    "rosenberg", "rses", "perceived stress scale", "pss", "brief cope",
    "connor-davidson", "cd-risc", "maslach burnout", "mbi", "ucla loneliness",
    # cognitive ability / intelligence
    "raven's progressive matrices", "progressive matrices", "wechsler", "wais",
    "wisc", "icar", "stanford-binet",
    # executive function tasks
    "stroop", "trail making", "flanker", "stop signal", "n-back",
    "brixton", "wisconsin card sorting", "tower of london", "tower of hanoi",
    "behavior rating inventory of executive function", "brief-a",
    # educational achievement / reading
    "woodcock-johnson", "dibels", "aimsweb", "kaufman assessment", "kabc",
    "dynamic indicators of basic early literacy",
    # values / language / large-scale assessments
    "schwartz values", "portrait values", "peabody picture vocabulary", "ppvt",
    "test for reception of grammar", "trog",
    "pisa", "timss", "pirls", "naep",
]

# Compile word-boundary matchers so short acronyms are safe (e.g. "irt" won't
# match inside "shirt", "bai" won't match inside "bait").
def _matcher(terms):
    return re.compile(r"\b(?:" + "|".join(re.escape(t) for t in terms) + r")\b")

_RE_INSTRUMENT = _matcher(INSTRUMENT_TERMS)
_RE_STRONG     = _matcher(STRONG_TERMS)
_RE_CONSTRUCT  = _matcher(CONSTRUCT_TERMS)
_RE_EXCLUDE    = _matcher(EXCLUDE_TERMS)
_RE_TRANS_LAT  = _matcher(TRANSLATED_TERMS_LATIN)
# No \b here on purpose -- see TRANSLATED_TERMS_NOBOUNDARY.
_RE_TRANS_NB   = re.compile(
    "|".join(re.escape(t) for t in TRANSLATED_TERMS_NOBOUNDARY))

# Supplementary-file titles: journal papers upload individual tables, figures,
# and data sheets as repository items. These are never standalone datasets and
# reliably have no downloadable tabular file. Block them unconditionally.
_RE_SUPPLEMENTARY = re.compile(
    r"^(?:table\s+\d+[_\s]|data\s+sheet\s+\d+[_\s]|"
    r"supplementary\s+(?:file|material|table|figure|data)\b|"
    r"figure\s+\d+[_\s]|appendix\s*\d*[_:\s])"
    # DataCite-specific: SAGE/Springer supplemental files named "sj-ext-N-jrnl-doi"
    r"|^sj-[a-z]+-\d+-"
    # Anything flagged mid-title as supplemental material for a paper
    r"|\bsupplemental\s+material\s+for\b"
    # Software/package files accidentally filed as datasets (.tar, version strings)
    r"|_\d+\.\d+\.\d+\.tar$",
    re.IGNORECASE
)


# Repositories that mint a DOI *per version* of the same deposit. DataCite
# indexes every version as its own record, so one Mendeley deposit arrives as
# `10.17632/j33ytz7wsx`, `.1` and `.2` -- three candidates, three downloads,
# three triage verdicts, and three rows for a human to read, all of the same
# data. Figshare does the same with a `.vN` suffix. Collapsing the suffix is
# scoped to these prefixes on purpose: most DOIs legitimately end in `.digits`
# (`10.1371/journal.pone.0235154`), so a blanket rule would corrupt them.
_VERSIONED_DOI_RULES = (
    (re.compile(r"^10\.17632/[^/]+?(\.\d+)$"),               1),  # Mendeley Data
    (re.compile(r"^10\.6084/m9\.figshare\.[^/]+?(\.v\d+)$"), 1),  # figshare
    (re.compile(r"^10\.5061/dryad\.[^/]+?(\.\d+)$"),         1),  # Dryad
)


def canonical_doi(doi: str) -> str:
    """Strip a repository version suffix so every version of one deposit maps
    to a single dedup key. Returns the DOI unchanged when no rule applies."""
    d = (doi or "").strip().lower()
    for rx, grp in _VERSIONED_DOI_RULES:
        m = rx.match(d)
        if m:
            return d[: m.start(grp)]
    return d


@dataclass
class Hit:
    source: str
    title: str
    url: str
    doi: str = ""
    published: str = ""


def norm_doi(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi:\s*", "", s)
    return s


def is_relevant(h: Hit, enabled: bool, query: str = "") -> bool:
    """Relevant if the title names an instrument, or carries a strong/construct
    signal — and isn't clinical/epi study language. Word-boundary matched so
    short acronyms don't match inside other words. Ambiguous words don't pass.
    Named instruments override the exclusion gate: a validation study of the
    PHQ-9 in a clinical cohort still has the item-response data we want.

    `query` is the search term that surfaced this hit. A title that contains
    the very term we searched for is relevant by construction, and checking
    that is strictly better than widening the global vocabulary: it only
    admits "fatigue" for the fatigue query, not for every query. Without it
    the filter silently contradicted the search list -- measured 2026-08-25,
    87 of the 125 standing terms in irw_discover_monthly.TERM_LIST produced
    titles this function dropped, including 9 of the 15 weekly high-yield
    terms (grit, self-efficacy, resilience, procrastination, perceived
    stress, loneliness, life satisfaction, growth mindset, work engagement).
    The pipeline was searching for "grit" and discarding datasets titled
    "Grit" before triage ever saw them."""
    if not enabled:
        return True
    # figshare (and some DataCite records) carry HTML in the title, e.g.
    # "<p>Rasch analysis results for the Rasch model ...</p>". The
    # supplementary-file patterns below are anchored at "^", so the leading
    # "<p>" made every one of them unreachable and figure/table supplements
    # sailed through the gate to die at triage as no_usable_file.
    title = re.sub(r"<[^>]+>", " ", h.title).strip()
    # Supplementary file naming convention — never a standalone dataset, always
    # blocked regardless of content or instrument mentions.
    if _RE_SUPPLEMENTARY.search(title):
        return False
    text = title.lower()
    # Named instrument always passes — validation studies have the data.
    if _RE_INSTRUMENT.search(text):
        return True
    # Epi/medical study language blocks everything else.
    if _RE_EXCLUDE.search(text):
        return False
    if (_RE_STRONG.search(text) or _RE_CONSTRUCT.search(text)
            or _RE_TRANS_LAT.search(text) or _RE_TRANS_NB.search(title)):
        return True
    # The searched-for term itself, matched whole so "hope" does not fire
    # inside "hopeless" and a two-word term must appear as a phrase.
    q = (query or "").strip().lower()
    if len(q) >= 3:
        if re.search(r"(?<!\w)" + re.escape(q) + r"(?!\w)", text):
            return True
    return False


# ---------------------------------------------------------------------------
# Source connectors — each yields Hit objects, paginating to exhaustion.
# ---------------------------------------------------------------------------

def from_dataverse(query: str, max_pages: int = 5, per: int = 50):
    start = 0
    for _ in range(max_pages):
        try:
            r = requests.get(
                "https://dataverse.harvard.edu/api/search",
                params={"q": query, "type": "dataset", "per_page": per, "start": start},
                headers=UA, timeout=30)
            if r.headers.get("x-amzn-waf-action") == "challenge":
                raise SourceBlocked(
                    f"dataverse.harvard.edu is behind an AWS WAF JS "
                    f"bot-challenge (HTTP {r.status_code}, empty body) -- "
                    "site-wide, not query-specific; no header/retry fixes "
                    "this, needs Harvard to allowlist or the challenge to "
                    "lift")
            r.raise_for_status()
            data = r.json().get("data", {})
            items = data.get("items", [])
        except SourceBlocked:
            raise
        except Exception as e:
            print(f"[dataverse] {e}", file=sys.stderr); return
        if not items:
            return
        for it in items:
            yield Hit("dataverse", it.get("name", ""), it.get("url", ""),
                      norm_doi(it.get("global_id", "")), it.get("published_at", ""))
        start += per
        if start >= data.get("total_count", 0):
            return
        time.sleep(0.5)


def from_zenodo(query: str, max_pages: int = 5, per: int = 25):
    query = query.replace("-", " ")   # Zenodo returns 400 on hyphenated queries
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://zenodo.org/api/records",
                params={"q": query, "size": per, "page": page, "type": "dataset"},
                headers=UA, timeout=30)
            r.raise_for_status()
            hits = r.json().get("hits", {}).get("hits", [])
        except Exception as e:
            print(f"[zenodo] {e}", file=sys.stderr); return
        if not hits:
            return
        for h in hits:
            md = h.get("metadata", {})
            yield Hit("zenodo", md.get("title", ""),
                      h.get("links", {}).get("html", ""),
                      norm_doi(h.get("doi", "")), md.get("publication_date", ""))
        time.sleep(0.5)


def from_osf(query: str, max_pages: int = 5, per: int = 50):
    url = "https://api.osf.io/v2/nodes/"
    params = {"filter[tags]": query, "page[size]": per}
    for _ in range(max_pages):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=30)
            r.raise_for_status()
            body = r.json()
        except Exception as e:
            print(f"[osf] {e}", file=sys.stderr); return
        for node in body.get("data", []):
            a = node.get("attributes", {})
            yield Hit("osf", a.get("title", ""),
                      node.get("links", {}).get("html", ""),
                      "", a.get("date_created", ""))
        nxt = body.get("links", {}).get("next")
        if not nxt:
            return
        url, params = nxt, {}
        time.sleep(0.5)


def from_dryad(query: str, max_pages: int = 5, per: int = 50):
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://datadryad.org/api/v2/search",
                params={"q": query, "per_page": per, "page": page},
                headers=UA, timeout=30)
            r.raise_for_status()
            sets = r.json().get("_embedded", {}).get("stash:datasets", [])
        except Exception as e:
            print(f"[dryad] {e}", file=sys.stderr); return
        if not sets:
            return
        for d in sets:
            yield Hit("dryad", d.get("title", ""),
                      f"https://datadryad.org/dataset/{d.get('identifier','')}",
                      norm_doi(d.get("identifier", "")),
                      d.get("publicationDate", ""))
        time.sleep(0.5)


def from_figshare(query: str, max_pages: int = 5, per: int = 50):
    for page in range(1, max_pages + 1):
        try:
            r = requests.post(
                "https://api.figshare.com/v2/articles/search",
                json={"search_for": query, "page_size": per, "page": page,
                      "item_type": 3},  # 3 = dataset
                headers=UA, timeout=30)
            r.raise_for_status()
            arts = r.json()
        except Exception as e:
            print(f"[figshare] {e}", file=sys.stderr); return
        if not arts:
            return
        for a in arts:
            yield Hit("figshare", a.get("title", ""), a.get("url_public_html", ""),
                      norm_doi(a.get("doi", "")), a.get("published_date", ""))
        time.sleep(0.5)


def from_gesis(query: str, max_pages: int = 5, per: int = 25):
    """GESIS Vitrine API — Elasticsearch-backed social/behavioral science archive."""
    for page in range(max_pages):
        try:
            r = requests.get(
                "https://api.vitrine.gesis.org/search/gesis-soda/_search",
                params={"q": query, "size": per, "from": page * per},
                headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json()
            hits = data.get("hits", {}).get("hits", [])
        except Exception as e:
            print(f"[gesis] {e}", file=sys.stderr); return
        if not hits:
            return
        for h in hits:
            s = h.get("_source", {})
            title_obj = s.get("title", {})
            title = title_obj.get("en") or title_obj.get("pref", "")
            handles = s.get("handles", [])
            doi = handles[0].get("notation", "") if handles else ""
            url = handles[0].get("url", "") if handles else ""
            pubs = s.get("publications", [{}])
            published = pubs[0].get("startDate", "") if pubs else ""
            yield Hit("gesis", title, url, norm_doi(doi), published)
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        if (page + 1) * per >= total:
            return
        time.sleep(0.5)


# Publishers already covered by other connectors — skip their DataCite records
# to avoid duplicate candidates (DOI dedup catches exact matches, but publisher
# filtering avoids pulling in thousands of Zenodo/Figshare records we already have).
_DATACITE_SKIP = {
    "zenodo", "figshare", "dryad data", "harvard dataverse",
    "open science framework", "osf",
}

# Which _DATACITE_SKIP publisher strings belong to which connector. When that
# connector is BLOCKED, its publishers stop being duplicates and become the only
# way to see that repository at all -- so the skip lifts and DataCite backfills
# it. This is what saves a run like 2026-08-17, where Harvard's site-wide WAF
# challenge made dataverse unreachable while DataCite still indexed 321 Harvard
# Dataverse hits for "personality" alone. Restores itself automatically: nothing
# is blocked next run, nothing is un-skipped.
_DATACITE_FALLBACK_FOR = {
    "dataverse":       {"harvard dataverse"},
    "zenodo":          {"zenodo"},
    "figshare":        {"figshare"},
    "dryad":           {"dryad data"},
    "osf":             {"open science framework", "osf"},
    "scholars_portal": {"scholars portal", "scholars portal dataverse"},
    "surf":            {"surf"},
    "aussda":          {"aussda", "austrian social science data archive"},
}


def _effective_datacite_skip() -> set[str]:
    """_DATACITE_SKIP minus the publishers whose own connector is blocked.

    Note this is evaluated per query, not once per run: a source that blocks on
    query 1 has its DataCite backfill active from query 2 on. Only if DataCite
    is ordered BEFORE the blocked source in --sources does the very first query
    miss the backfill, which costs one query's worth of that publisher."""
    skip = set(_DATACITE_SKIP)
    for src in blocked_sources():
        skip -= _DATACITE_FALLBACK_FOR.get(src, set())
    return skip


def from_datacite(query: str, max_pages: int = 5, per: int = 25):
    """DataCite REST API — aggregates datasets from ICPSR, UK Data Service, DANS,
    and hundreds of other repositories not covered by the other connectors."""
    skip = _effective_datacite_skip()
    if skip != _DATACITE_SKIP:
        print(f"  [datacite] backfilling for blocked source(s): "
              f"{', '.join(sorted(_DATACITE_SKIP - skip))}", flush=True)
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://api.datacite.org/dois",
                params={"query": query, "resource-type-id": "dataset",
                        "page[size]": per, "page[number]": page},
                headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json()
            items = data.get("data", [])
        except Exception as e:
            print(f"[datacite] {e}", file=sys.stderr); return
        if not items:
            return
        for item in items:
            a = item.get("attributes", {})
            publisher = a.get("publisher", "").lower()
            if any(s in publisher for s in skip):
                continue
            titles = a.get("titles", [{}])
            title = titles[0].get("title", "") if titles else ""
            doi = a.get("doi", "")
            url = a.get("url", "") or f"https://doi.org/{doi}"
            published = str(a.get("publicationYear", ""))
            # Strip version suffixes (e.g. 10.3886/icpsr21661.v3) for cleaner dedup
            doi_norm = re.sub(r"\.v\d+$", "", norm_doi(doi))
            yield Hit("datacite", title, url, doi_norm, published)
        meta = data.get("meta", {})
        if page >= meta.get("totalPages", 1):
            return
        time.sleep(0.5)


def _dataverse_connector(name: str, base_url: str):
    """Generate a Dataverse-compatible source function for a given instance."""
    def fn(query: str, max_pages: int = 5, per: int = 50):
        start = 0
        for _ in range(max_pages):
            try:
                r = requests.get(
                    f"{base_url}/api/search",
                    params={"q": query, "type": "dataset", "per_page": per, "start": start},
                    headers=UA, timeout=30)
                r.raise_for_status()
                data = r.json().get("data", {})
                items = data.get("items", [])
            except Exception as e:
                print(f"[{name}] {e}", file=sys.stderr); return
            if not items:
                return
            for it in items:
                yield Hit(name, it.get("name", ""), it.get("url", ""),
                          norm_doi(it.get("global_id", "")), it.get("published_at", ""))
            start += per
            if start >= data.get("total_count", 0):
                return
            time.sleep(0.5)
    fn.__name__ = f"from_{name}"
    return fn


from_scholars_portal = _dataverse_connector(
    "scholars_portal", "https://dataverse.scholarsportal.info")
from_surf            = _dataverse_connector("surf", "https://dataverse.nl")
from_aussda          = _dataverse_connector("aussda", "https://data.aussda.at")


def from_openaire(query: str, max_pages: int = 5, per: int = 25):
    """OpenAIRE — European open research aggregator (EU-funded datasets)."""
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://api.openaire.eu/search/datasets",
                params={"keywords": query, "size": per, "page": page, "format": "json"},
                headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json()
            results = data.get("response", {}).get("results", {}).get("result", [])
            total = int(data.get("response", {}).get("header", {}).get("total", {}).get("$", 0))
        except Exception as e:
            print(f"[openaire] {e}", file=sys.stderr); return
        if not results:
            return
        for res in results:
            md = res.get("metadata", {}).get("oaf:entity", {}).get("oaf:result", {})
            t = md.get("title", [])
            if isinstance(t, list) and t:
                title = t[0].get("$", "")
            elif isinstance(t, dict):
                title = t.get("$", "")
            else:
                title = ""
            pids = md.get("pid", [])
            doi = ""
            for p in (pids if isinstance(pids, list) else [pids]):
                if isinstance(p, dict) and p.get("@classid") == "doi":
                    doi = p.get("$", "")
                    break
            url_obj = md.get("url", {})
            url = url_obj.get("$", "") if isinstance(url_obj, dict) else ""
            if not url and doi:
                url = f"https://doi.org/{doi}"
            dates = md.get("dateofacceptance", {})
            published = dates.get("$", "")[:10] if isinstance(dates, dict) else ""
            yield Hit("openaire", title, url, norm_doi(doi), published)
        if page * per >= total:
            return
        time.sleep(0.5)


# Also update skip list so DataCite doesn't duplicate our new Dataverse instances
_DATACITE_SKIP.update({"scholars portal", "scholars portal dataverse", "surf",
                        "aussda", "austrian social science data archive"})


SOURCES = [from_dataverse, from_zenodo, from_osf, from_dryad, from_figshare,
           from_datacite, from_scholars_portal, from_surf]

# Opt-in only -- reachable with `--sources openaire ...`, deliberately NOT in
# SOURCES. OpenAIRE is an aggregator like DataCite (it re-indexes Zenodo,
# figshare, SAGE, national repositories, sciencedb.cn, ...), so folding it
# into the default set would multiply every scheduled run's cost for a large
# fraction of records the dedicated connectors already return. It does reach
# hosts nothing else does, though, which is why it's wired up at all: before
# 2026-08-25 from_openaire() was defined but absent from SOURCES *and*
# SOURCE_MAP, i.e. dead code no run could ever call.
#
# from_gesis() is deliberately still not wired: as of 2026-08-25 the GESIS
# Vitrine endpoint it calls returns HTTP 403 for every query, so it yields
# nothing. Fix the endpoint before adding it here.
OPTIONAL_SOURCES = [from_openaire]

SOURCE_MAP = {fn.__name__.replace("from_", ""): fn
              for fn in SOURCES + OPTIONAL_SOURCES}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# IRW dictionary: authoritative list of what is already in the warehouse.
DICT_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/export?format=csv&gid=0"
)


def _extract_doi_from_url(url: str) -> str | None:
    """Best-effort extraction of a normalised DOI from a data repository URL."""
    if not url:
        return None
    # doi.org resolver
    m = re.search(r'doi\.org/(.+?)(?:\s|$)', url)
    if m:
        return norm_doi(m.group(1))
    # Harvard Dataverse persistent ID
    m = re.search(r'persistentId=doi:(.+?)(?:&|$)', url, re.I)
    if m:
        return norm_doi(m.group(1))
    # OSF project page
    m = re.search(r'osf\.io/([a-z0-9]+)/?$', url, re.I)
    if m:
        return norm_doi(f'10.17605/osf.io/{m.group(1)}')
    # Zenodo record page
    m = re.search(r'zenodo\.org/record/(\d+)', url)
    if m:
        return norm_doi(f'10.5281/zenodo.{m.group(1)}')
    # Figshare article page (any subdomain). Real URLs have a variable number
    # of path segments between "articles/" and the numeric ID -- at minimum
    # a type segment ("dataset"), often also a title slug
    # (.../articles/dataset/Some_Title_Here/19158812) -- so anchor on the
    # trailing digits rather than assuming exactly one segment in between.
    m = re.search(r'figshare\.com/articles/.+?(\d+)(?:\.v\d+)?/?(?:[?#]|$)', url)
    if m:
        return norm_doi(f'10.6084/m9.figshare.{m.group(1)}')
    return None


def _load_existing_irw_dois() -> set:
    """Fetch DOIs of datasets already in the IRW dictionary Google Sheet."""
    try:
        r = requests.get(DICT_SHEET_URL, timeout=15)
        r.raise_for_status()
        reader = csv.DictReader(r.text.splitlines())
        dois = set()
        for row in reader:
            url_doi = _extract_doi_from_url(row.get("URL (for data)", ""))
            if url_doi:
                dois.add(url_doi)
            paper_doi = norm_doi(row.get("DOI (for paper)", "") or "")
            if "/" in paper_doi and " " not in paper_doi:
                dois.add(paper_doi)
        return dois
    except Exception as e:
        print(f"[warn] Could not fetch IRW dictionary from Google Sheet: {e}",
              file=sys.stderr)
        return set()


def _load_human_review_exclusions() -> set:
    """Load DOIs already logged as a human_review row in a past batch.

    Reads every human_review/*.csv (the permanent archive replacing the old
    "human eye" queue-sheet tab, deprecated 2026-08-12) relative to cwd — the
    pipeline is always run from inside automated_finding/, same assumption
    _load_existing_irw_dois() and everything else here already makes. A file
    without a `doi` column (unlikely, but tolerate it) contributes nothing
    rather than erroring.
    """
    dois = set()
    for path in glob.glob(os.path.join("human_review", "*.csv")):
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or "doi" not in reader.fieldnames:
                    continue
                # googlesheet_humaneye.csv is the export of the retired "human
                # eye" queue tab. It is NOT a record of decisions: of its 4,833
                # rows only 31 ever got a Decision and 32 an Evaluator -- the
                # tab was retired in 2026-08-12 precisely because nobody could
                # work through it. Excluding all of it turned an unworked
                # backlog into a permanent blocklist, hiding ~2,300 candidates
                # from every future discovery run. Only the rows somebody
                # actually adjudicated count as reviewed; the rest stay
                # discoverable. (The per-batch human_review_*.csv files keep
                # their original exclude-everything semantics.)
                decision_col = next(
                    (c for c in reader.fieldnames if c.startswith("Decision")), None)
                gate = decision_col if os.path.basename(path).startswith(
                    "googlesheet_") else None
                for row in reader:
                    # Only the three real decision values count. Some rows in
                    # that sheet are column-shifted (a title or a source name
                    # landed in the Decision cell), and those are not decisions.
                    if gate and (row.get(gate) or "").strip().lower() not in (
                            "yes", "no", "maybe"):
                        continue
                    d = norm_doi(row.get("doi", "") or "")
                    if "/" in d and " " not in d:
                        dois.add(d)
        except Exception as e:
            print(f"[warn] Could not read {path}: {e}", file=sys.stderr)
    return dois


def _load_auto_exclusions() -> set:
    """Load DOIs to exclude: already in the IRW dictionary, or already
    logged as a human_review row in a past batch."""
    existing = _load_existing_irw_dois()
    reviewed = _load_human_review_exclusions()
    print(f"[exclude] {len(existing)} DOIs already in IRW, "
          f"{len(reviewed)} already logged in human_review/", flush=True)
    return existing | reviewed


RUNS_DIR = "runs"


def in_runs_dir(path: str) -> str:
    """Put a per-run output file in runs/ unless it already names a directory.

    Every disposable per-run artifact of this pipeline (candidate lists,
    triage/retriage outputs, sanity-check files) lives in `runs/` so the
    top level of automated_finding/ holds only standing records --
    search_terms_log.csv, *_seen_dois.csv, repo_triage_seen_keys.csv,
    license_blocked_candidates.csv, plos_deferred_candidates.csv,
    human_review/. A bare filename ("candidates.csv") is rewritten to
    "runs/candidates.csv"; a path with any directory component (an
    explicit "/tmp/x.csv" or an already-runs/-prefixed name) is honored
    as given.
    """
    if os.path.dirname(path):
        return path
    os.makedirs(RUNS_DIR, exist_ok=True)
    return os.path.join(RUNS_DIR, path)


def resolve_in_path(path: str) -> str:
    """Find a per-run input file, looking in runs/ if it isn't at cwd.

    Lets `irw_batch_updated.py candidates.csv` keep working now that the
    discovery scripts write to runs/candidates.csv."""
    if path and not os.path.exists(path) and not os.path.dirname(path):
        alt = os.path.join(RUNS_DIR, path)
        if os.path.exists(alt):
            return alt
    return path


def resolve_out_path(explicit: str | None, default: str) -> str:
    """Pick a per-run output path in runs/ that will not clobber an
    existing run.

    The scheduled discovery scripts name their output by mode and UTC date,
    so two runs of the same mode on the same day collide -- e.g. a manual
    backlog sweep in the morning and the cron'd monthly run that evening
    (2026-08-16, which lost the morning sweep's 93 triaged rows on main).
    When the default path is taken, append `-2`, `-3`, ... until the name is
    free. An explicit --out is the caller's choice and is returned as-is.
    """
    if explicit:
        return in_runs_dir(explicit)
    default = in_runs_dir(default)
    if not os.path.exists(default):
        return default
    stem, ext = os.path.splitext(default)
    n = 2
    while os.path.exists(f"{stem}-{n}{ext}"):
        n += 1
    path = f"{stem}-{n}{ext}"
    print(f"[out] {default} already exists (earlier run today) -- writing {path}",
          flush=True)
    return path


def _older_than(published: str, since: str) -> bool:
    """Is `published` strictly older than the `since` cutoff?

    Sources disagree on date granularity: most give a full ISO timestamp, but
    DataCite exposes only `publicationYear` ("2026"). A naive string compare
    reads "2026" < "2026-08-03" as True and silently drops every current-year
    DataCite record -- i.e. exactly the recent ones a --since run is looking
    for. So compare at the coarsest granularity the two values share: a
    year-only date is dropped only when its year precedes the cutoff's year.
    Errs toward keeping (triage does the precision work), consistent with the
    existing rule that a missing date isn't evidence a hit is old."""
    p = published[:10]
    if len(p) == 4:
        return p < since[:4]
    return p < since


def discover(queries, exclude: set, relevance_on: bool, sources=None,
             on_hit=None, since: str | None = None) -> list:
    """Discover candidates across all sources for each query.

    on_hit: optional callable(Hit) invoked immediately when a new candidate
    passes all filters — use this to write results incrementally rather than
    waiting for the full run to finish.
    since: optional "YYYY-MM-DD" — drop hits whose `published` date is
    earlier than this. Applied client-side after each source's normal
    (unfiltered) pagination, since not every source API supports a
    date-range query param and `Hit.published` already carries a comparable
    ISO date string for all of them. A hit with no `published` value is
    kept rather than dropped, since a missing date isn't evidence it's old.
    """
    import time as _time
    active = sources if sources is not None else SOURCES
    seen, results = set(), []
    total = len(queries)
    t0 = _time.time()
    for i, q in enumerate(queries, 1):
        q_new = 0
        q_start = _time.time()
        print(f"[query {i}/{total}] {q}", flush=True)
        for src in active:
            if src.__name__ in _blocked_sources:
                continue
            src_new = 0
            try:
                for hit in src(q):
                    # Collapse repository version suffixes so one deposit is
                    # one candidate: DataCite indexes every version of a
                    # Mendeley/figshare/Dryad deposit as its own record.
                    key = (canonical_doi(hit.doi) if hit.doi
                           else f"{hit.source}:{hit.title.strip().lower()}")
                    if not key or key in seen:
                        continue
                    if hit.doi and hit.doi in exclude:
                        continue
                    if not is_relevant(hit, relevance_on, query=q):
                        continue
                    if since and hit.published and _older_than(hit.published, since):
                        continue
                    seen.add(key)
                    results.append(hit)
                    q_new += 1
                    src_new += 1
                    if on_hit:
                        on_hit(hit)
            except SourceBlocked as e:
                _blocked_sources.add(src.__name__)
                print(f"  [{src.__name__:20}] BLOCKED, skipping for rest "
                      f"of run -- {e}", file=sys.stderr, flush=True)
                continue
            if src_new:
                print(f"  [{src.__name__:20}] +{src_new}", flush=True)
        elapsed = _time.time() - t0
        print(f"  → {q_new} new this query | {len(results)} total | "
              f"{elapsed:.0f}s elapsed", flush=True)
    if _blocked_sources:
        print(f"[discover] sources blocked this run (see BLOCKED lines "
              f"above for why): {', '.join(sorted(_blocked_sources))}",
              file=sys.stderr, flush=True)
    return results


from irw_triage_updated import preflight_deps


def main():
    preflight_deps()
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*", default=["item response theory"])
    ap.add_argument("--all", action="store_true", help="disable relevance filter")
    ap.add_argument("--out", default="candidates.csv")
    ap.add_argument("--sources", metavar="NAME", nargs="+",
                    help=f"query only these sources (choices: {', '.join(SOURCE_MAP)})")
    ap.add_argument("--since", metavar="YYYY-MM-DD",
                    help="only keep hits published/created on or after this date")
    args = ap.parse_args()

    queries = args.queries or ["item response theory"]

    if args.sources:
        unknown = set(args.sources) - set(SOURCE_MAP)
        if unknown:
            ap.error(f"Unknown sources: {', '.join(unknown)}. Choices: {', '.join(SOURCE_MAP)}")
        active_sources = [SOURCE_MAP[s] for s in args.sources]
        print(f"Querying sources: {', '.join(args.sources)}")
    else:
        active_sources = None

    exclude = _load_auto_exclusions()

    if exclude:
        print(f"Excluding {len(exclude):,} DOIs already in the IRW dictionary")
    print()

    fieldnames = ["source", "title", "doi", "published", "url"]
    args.out = in_runs_dir(args.out)
    outf = open(args.out, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()
    outf.flush()

    hits = []

    def on_hit(h):
        hits.append(h)
        writer.writerow(asdict(h))
        outf.flush()

    discover(queries, exclude, relevance_on=not args.all, sources=active_sources,
             on_hit=on_hit, since=args.since)
    outf.close()

    print(f"{len(hits)} candidates found -> {args.out}")
    for h in hits[:25]:
        print(f"  [{h.source:9}] {h.title[:70]}")


if __name__ == "__main__":
    main()
