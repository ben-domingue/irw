"""Step 1: resolve journal identities for the journal-scout yield study.

For each candidate journal title, resolve ISSN-L / print / electronic ISSNs,
publisher, and open-access status from Crossref + OpenAlex + DOAJ. Also
computes a PMC-deposit-scope *proxy* from Europe PMC (see NOTE below) since
the official PMC Journal List is a JS-rendered page with no stable scrape
target or API.

Writes journal_scout/journals_resolved.csv. Caches every raw API response
under journal_scout/cache/resolve/ (skip-if-exists, restartable).

NOTE on deposit scope: the original spec asked to check the PMC Journal
List for "all articles" vs "funder-only" deposit. That page
(pmc.ncbi.nlm.nih.gov/journals/) is client-rendered with no stable CSV/API
export we could find. Instead we compute, per journal, the ratio of
Europe PMC hitCount for `IN_PMC:y` over hitCount with no such filter for a
recent full year (2023) -- a ratio near 1.0 indicates "all articles"
deposit; a low or partial ratio indicates funder-only/selective deposit.
This reuses the Step 2 query surface rather than adding a new one.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests

sys.path.insert(0, str(Path(__file__).parent))
from journals_candidates import CANDIDATES

HERE = Path(__file__).parent
CACHE = HERE / "cache" / "resolve"
CACHE.mkdir(parents=True, exist_ok=True)
ERRLOG = HERE / "errors.log"

CONTACT_EMAIL = "ben.domingue@gmail.com"
UA = {"User-Agent": f"irw-journal-scout/0.1 (mailto:{CONTACT_EMAIL})"}

PROXY_YEAR = 2023  # recent full year used for the PMC-deposit-scope proxy


def log_error(msg: str) -> None:
    with ERRLOG.open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"  [error] {msg}", file=sys.stderr)


def cached_get(url: str, cache_key: str, params: dict | None = None) -> dict | None:
    path = CACHE / f"{cache_key}.json"
    if path.exists():
        return json.loads(path.read_text())
    try:
        resp = requests.get(url, params=params, headers=UA, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log_error(f"{cache_key}: {url} params={params} -> {e}")
        return None
    path.write_text(json.dumps(data, indent=1))
    time.sleep(0.3)
    return data


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def norm_title(title: str) -> str:
    """Loose title comparison key: lowercase, drop punctuation/whitespace
    differences (e.g. a serial comma) that Crossref/OpenAlex are
    inconsistent about even for the exact same journal -- seen for
    "Attention, Perception & Psychophysics" (Crossref/OpenAlex both index
    it without the comma)."""
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def query_crossref(title: str) -> dict | None:
    return cached_get(
        "https://api.crossref.org/journals",
        f"crossref_{slug(title)}",
        params={"query": title, "rows": 5},
    )


def query_openalex(title: str) -> dict | None:
    return cached_get(
        "https://api.openalex.org/sources",
        f"openalex_{slug(title)}",
        params={"search": title, "per_page": 5, "mailto": CONTACT_EMAIL},
    )


def query_crossref_by_issn(issn: str) -> dict | None:
    if not issn:
        return None
    return cached_get(
        f"https://api.crossref.org/journals/{issn}",
        f"crossref_issn_{issn}",
    )


def query_doaj(issn: str) -> dict | None:
    if not issn:
        return None
    return cached_get(
        f"https://doaj.org/api/search/journals/issn:{issn}",
        f"doaj_{issn}",
    )


def pmc_deposit_proxy(issn: str) -> tuple[float | None, int | None]:
    """Returns (ratio, total_hitcount) for PROXY_YEAR, or (None, None) on failure."""
    if not issn:
        return None, None
    date_range = f"[{PROXY_YEAR}-01-01 TO {PROXY_YEAR}-12-31]"
    base_q = f'ISSN:"{issn}" AND (FIRST_PDATE:{date_range})'

    total = cached_get(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        f"proxy_total_{issn}_{PROXY_YEAR}",
        params={"query": base_q, "resultType": "idlist", "pageSize": 1, "format": "json"},
    )
    inpmc = cached_get(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        f"proxy_inpmc_{issn}_{PROXY_YEAR}",
        params={"query": base_q + " AND IN_PMC:y", "resultType": "idlist", "pageSize": 1, "format": "json"},
    )
    if not total or not inpmc:
        return None, None
    t = total.get("hitCount")
    p = inpmc.get("hitCount")
    if not t:
        return None, 0
    return round(p / t, 3), t


def best_crossref_match(title: str, cr: dict | None) -> dict | None:
    if not cr:
        return None
    items = cr.get("message", {}).get("items", [])
    if not items:
        return None
    # exact case-insensitive title match wins; else return top hit flagged ambiguous by caller
    # NOTE: Crossref /journals returns "title" as a plain string (unlike /works,
    # where it's a list) -- do not iterate it as a list of titles.
    for it in items:
        if norm_title(it.get("title", "")) == norm_title(title):
            return it
    return items[0]


def best_openalex_match(title: str, oa: dict | None) -> dict | None:
    if not oa:
        return None
    results = oa.get("results", [])
    if not results:
        return None
    for r in results:
        if norm_title(r.get("display_name", "")) == norm_title(title):
            return r
    return results[0]


def resolve_one(title: str, tier: str) -> dict:
    print(f"Resolving: {title} ({tier})")
    cr = query_crossref(title)
    oa = query_openalex(title)

    cr_match = best_crossref_match(title, cr)
    oa_match = best_openalex_match(title, oa)

    cr_n_candidates = len(cr.get("message", {}).get("items", [])) if cr else 0
    oa_n_candidates = len(oa.get("results", [])) if oa else 0

    # Crossref's free-text /journals?query= search can rank an unrelated
    # journal top for short/generic titles (seen for "Psych" and "Education
    # Sciences"). If the title match wasn't exact, fall back to an
    # ISSN-based Crossref lookup using OpenAlex's ISSN and prefer it when
    # its title matches -- this is a *targeted* fix for those two, not a
    # general behavior change to non-ambiguous rows.
    issn_fallback_used = False
    cr_exact_pretest = bool(cr_match and norm_title(cr_match.get("title", "")) == norm_title(title))
    if not cr_exact_pretest and oa_match:
        candidate_issns = [oa_match.get("issn_l")] + (oa_match.get("issn") or [])
        for candidate_issn in candidate_issns:
            if not candidate_issn:
                continue
            fallback = query_crossref_by_issn(candidate_issn)
            fb_msg = (fallback or {}).get("message", {})
            if norm_title(fb_msg.get("title", "")) == norm_title(title):
                cr_match = fb_msg
                issn_fallback_used = True
                break

    cr_exact = bool(cr_match and norm_title(cr_match.get("title", "")) == norm_title(title))
    oa_exact = bool(oa_match and norm_title(oa_match.get("display_name", "")) == norm_title(title))

    issns = cr_match.get("ISSN", []) if cr_match else []
    issn_type = cr_match.get("issn-type", []) if cr_match else []
    issn_print = next((x["value"] for x in issn_type if x.get("type") == "print"), "")
    issn_electronic = next((x["value"] for x in issn_type if x.get("type") == "electronic"), "")
    issn_l = ""
    if oa_match:
        issn_l = (oa_match.get("issn_l") or "")
        if not issn_l and oa_match.get("issn"):
            issn_l = oa_match["issn"][0]

    # DOAJ check on whichever ISSN we have (prefer issn_l, else electronic, else print, else first crossref issn)
    doaj_issn = issn_l or issn_electronic or issn_print or (issns[0] if issns else "")
    doaj = query_doaj(doaj_issn) if doaj_issn else None
    in_doaj = bool(doaj and doaj.get("results"))

    publisher = cr_match.get("publisher", "") if cr_match else (oa_match.get("host_organization_name", "") if oa_match else "")
    is_oa_openalex = oa_match.get("is_oa") if oa_match else None

    proxy_issn = doaj_issn
    pmc_ratio, pmc_total = pmc_deposit_proxy(proxy_issn)

    flag = []
    if not cr_match and not oa_match:
        flag.append("NOT_FOUND")
    if cr_n_candidates > 1 and not cr_exact:
        flag.append("CROSSREF_AMBIGUOUS")
    if oa_n_candidates > 1 and not oa_exact:
        flag.append("OPENALEX_AMBIGUOUS")
    if cr_match and oa_match and publisher and oa_match.get("host_organization_name") and \
            publisher.lower() not in (oa_match.get("host_organization_name") or "").lower() and \
            (oa_match.get("host_organization_name") or "").lower() not in publisher.lower():
        flag.append("PUBLISHER_MISMATCH_CR_VS_OA")
    if issn_fallback_used:
        flag.append("CROSSREF_ISSN_FALLBACK_USED")

    return {
        "tier": tier,
        "title_queried": title,
        "title_crossref": (cr_match.get("title", "") if cr_match else ""),
        "title_openalex": (oa_match.get("display_name", "") if oa_match else ""),
        "issn_l": issn_l,
        "issn_print": issn_print,
        "issn_electronic": issn_electronic,
        "issn_crossref_all": ";".join(issns),
        "publisher_crossref": cr_match.get("publisher", "") if cr_match else "",
        "publisher_openalex": oa_match.get("host_organization_name", "") if oa_match else "",
        "is_oa_openalex": is_oa_openalex,
        "in_doaj": in_doaj,
        "pmc_deposit_ratio_2023_proxy": pmc_ratio,
        "pmc_total_hitcount_2023_proxy": pmc_total,
        "crossref_n_candidates": cr_n_candidates,
        "openalex_n_candidates": oa_n_candidates,
        "flags": ";".join(flag),
    }


def main():
    rows = []
    for tier, titles in CANDIDATES.items():
        for title in titles:
            rows.append(resolve_one(title, tier))

    import csv as csvmod
    out_path = HERE / "journals_resolved.csv"
    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="") as f:
        w = csvmod.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
