"""Retire 23 pooled conjoint tables that were split into per-country tables (irw#3536).

Ben 2026-11-15 (#3536, item 1): a multi-country fielding whose attribute levels or design differ by country
is split into one table per country, `<table>_<iso2>`, and the pooled name is retired. The 110 country
tables are uploaded to irw_conjoint_2 first; this script then deletes each pooled table from the draft of the
shard that holds it. This is not a withdrawal: the data stay in IRW under the country names, so nothing goes
in itemtext/withdrawals.csv; metadata/table_changes.csv gets a `replaced_by` row per table after the release.

Guards: every pooled table must be in its shard's current release; every country table must already be in
the irw_conjoint_2 draft (so nothing is deleted before its replacement exists); each draft loses exactly its
targets and nothing else (KEEP = everything else).

Resumable: a target already gone from the draft is skipped. Dry run by default; APPLY=1 deletes.
"""
import json, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_conj_country_splits")
import redivis

OWNER = "datapages"
SHARDS = ["irw_conjoint", "irw_conjoint_2"]
#: pooled table -> its country tables (data/conjoint/<script>.R headers, "SPLIT BY COUNTRY")
SPLITS = json.loads(r'''{
 "aassve_2026_parenthood": [
  "aassve_2026_parenthood_ar",
  "aassve_2026_parenthood_de",
  "aassve_2026_parenthood_it",
  "aassve_2026_parenthood_us"
 ],
 "adsera_2023_value_of_democracy": [
  "adsera_2023_value_of_democracy_br",
  "adsera_2023_value_of_democracy_fr",
  "adsera_2023_value_of_democracy_us"
 ],
 "bechtel_2022_climate_multilateralism": [
  "bechtel_2022_climate_multilateralism_de",
  "bechtel_2022_climate_multilateralism_fr",
  "bechtel_2022_climate_multilateralism_gb",
  "bechtel_2022_climate_multilateralism_us"
 ],
 "borbath_2025_party_rebranding": [
  "borbath_2025_party_rebranding_at",
  "borbath_2025_party_rebranding_hu",
  "borbath_2025_party_rebranding_it"
 ],
 "buttler_2026_hiring_vignettes": [
  "buttler_2026_hiring_vignettes_de",
  "buttler_2026_hiring_vignettes_no",
  "buttler_2026_hiring_vignettes_pl",
  "buttler_2026_hiring_vignettes_ro"
 ],
 "claassen_2026_democratic_backsliding": [
  "claassen_2026_democratic_backsliding_kr",
  "claassen_2026_democratic_backsliding_pl",
  "claassen_2026_democratic_backsliding_us"
 ],
 "clayton_2025_gender_quotas": [
  "clayton_2025_gender_quotas_ar",
  "clayton_2025_gender_quotas_au",
  "clayton_2025_gender_quotas_br",
  "clayton_2025_gender_quotas_es",
  "clayton_2025_gender_quotas_fr",
  "clayton_2025_gender_quotas_gb",
  "clayton_2025_gender_quotas_mx",
  "clayton_2025_gender_quotas_no",
  "clayton_2025_gender_quotas_nz",
  "clayton_2025_gender_quotas_pe",
  "clayton_2025_gender_quotas_pt",
  "clayton_2025_gender_quotas_us"
 ],
 "duch_2022_destination_country": [
  "duch_2022_destination_country_cl",
  "duch_2022_destination_country_cn",
  "duch_2022_destination_country_gb",
  "duch_2022_destination_country_in"
 ],
 "gereke_2023_trust": [
  "gereke_2023_trust_ch",
  "gereke_2023_trust_us",
  "gereke_2023_trust_za"
 ],
 "gereke_2023_trustworthiness": [
  "gereke_2023_trustworthiness_ch",
  "gereke_2023_trustworthiness_us",
  "gereke_2023_trustworthiness_za"
 ],
 "harris_2023_neighbor_cooperation": [
  "harris_2023_neighbor_cooperation_mw",
  "harris_2023_neighbor_cooperation_zm"
 ],
 "ibbett_2024_pa_sanction_fairness": [
  "ibbett_2024_pa_sanction_fairness_id",
  "ibbett_2024_pa_sanction_fairness_tz"
 ],
 "laterzo_2023_crime_candidates": [
  "laterzo_2023_crime_candidates_ar",
  "laterzo_2023_crime_candidates_br"
 ],
 "levis_2026_carbon_messenger": [
  "levis_2026_carbon_messenger_de",
  "levis_2026_carbon_messenger_pl"
 ],
 "magistro_2024_automation_fairness": [
  "magistro_2024_automation_fairness_au",
  "magistro_2024_automation_fairness_ca",
  "magistro_2024_automation_fairness_gb",
  "magistro_2024_automation_fairness_us"
 ],
 "mueller_2024_covid_governance": [
  "mueller_2024_covid_governance_au",
  "mueller_2024_covid_governance_be",
  "mueller_2024_covid_governance_ca",
  "mueller_2024_covid_governance_ch",
  "mueller_2024_covid_governance_fr",
  "mueller_2024_covid_governance_us"
 ],
 "munzert_2022_vaccine_priority": [
  "munzert_2022_vaccine_priority_br",
  "munzert_2022_vaccine_priority_de",
  "munzert_2022_vaccine_priority_it",
  "munzert_2022_vaccine_priority_pl",
  "munzert_2022_vaccine_priority_us"
 ],
 "reher_2025_disabled_candidates": [
  "reher_2025_disabled_candidates_gb",
  "reher_2025_disabled_candidates_us"
 ],
 "rudolph_2024_arms_exports": [
  "rudolph_2024_arms_exports_de",
  "rudolph_2024_arms_exports_fr"
 ],
 "stoetzer_2023_covid_triage": [
  "stoetzer_2023_covid_triage_br",
  "stoetzer_2023_covid_triage_de",
  "stoetzer_2023_covid_triage_it",
  "stoetzer_2023_covid_triage_pl",
  "stoetzer_2023_covid_triage_us"
 ],
 "suring_2025_forest_contracts": [
  "suring_2025_forest_contracts_dk",
  "suring_2025_forest_contracts_fi"
 ],
 "williamson_2023_preacher_authority": [
  "williamson_2023_preacher_authority_ae",
  "williamson_2023_preacher_authority_bh",
  "williamson_2023_preacher_authority_eg",
  "williamson_2023_preacher_authority_jo",
  "williamson_2023_preacher_authority_kw",
  "williamson_2023_preacher_authority_lb",
  "williamson_2023_preacher_authority_ma",
  "williamson_2023_preacher_authority_qa",
  "williamson_2023_preacher_authority_sa",
  "williamson_2023_preacher_authority_tn",
  "williamson_2023_preacher_authority_tr"
 ],
 "wimmer_2024_rivalry_immigrants": [
  "wimmer_2024_rivalry_immigrants_ar",
  "wimmer_2024_rivalry_immigrants_au",
  "wimmer_2024_rivalry_immigrants_br",
  "wimmer_2024_rivalry_immigrants_ca",
  "wimmer_2024_rivalry_immigrants_de",
  "wimmer_2024_rivalry_immigrants_es",
  "wimmer_2024_rivalry_immigrants_fr",
  "wimmer_2024_rivalry_immigrants_gb",
  "wimmer_2024_rivalry_immigrants_gr",
  "wimmer_2024_rivalry_immigrants_hu",
  "wimmer_2024_rivalry_immigrants_in",
  "wimmer_2024_rivalry_immigrants_it",
  "wimmer_2024_rivalry_immigrants_jp",
  "wimmer_2024_rivalry_immigrants_kr",
  "wimmer_2024_rivalry_immigrants_nl",
  "wimmer_2024_rivalry_immigrants_pe",
  "wimmer_2024_rivalry_immigrants_ph",
  "wimmer_2024_rivalry_immigrants_pl",
  "wimmer_2024_rivalry_immigrants_se",
  "wimmer_2024_rivalry_immigrants_tr",
  "wimmer_2024_rivalry_immigrants_us",
  "wimmer_2024_rivalry_immigrants_za"
 ]
}''')
apply = os.environ.get("APPLY") == "1"


def names(ds, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds, version=version).list_tables(max_results=2000)}


current = {ds: names(ds, "current") for ds in SHARDS}
home = {}
for t in SPLITS:
    where = [ds for ds in SHARDS if t in current[ds]]
    if len(where) != 1:
        sys.exit(f"ABORT: {t} is in {where or 'no'} shard(s) of the current release")
    home[t] = where[0]
try:
    draft2 = names("irw_conjoint_2", "next")
except Exception as exc:
    sys.exit(f"ABORT: no irw_conjoint_2 draft ({type(exc).__name__}); upload the country tables first")
missing = sorted(n for ns in SPLITS.values() for n in ns if n not in draft2)
if missing:
    sys.exit(f"ABORT: {len(missing)} country table(s) not yet in the irw_conjoint_2 draft, e.g. {missing[:5]}")

for ds in SHARDS:
    targets = {t for t, h in home.items() if h == ds}
    if not targets:
        continue
    if not apply:
        try:
            nxt = names(ds, "next")
            print(f"DRY RUN {ds}: {len(targets)} target(s), {len(targets & nxt)} still in the draft")
        except Exception as exc:
            print(f"DRY RUN {ds}: no draft open ({type(exc).__name__}); APPLY=1 would create one")
        continue
    redivis.organization(OWNER).dataset(ds).create_next_version(if_not_exists=True)
    draft = redivis.organization(OWNER).dataset(ds, version="next")
    before = {x.name for x in draft.list_tables(max_results=2000)}
    todo = sorted(targets & before)
    for t in todo:
        draft.table(t).delete()
        print(f"deleted: {ds}.{t}")
    removed = before - names(ds, "next")
    assert removed == set(todo), f"MISMATCH in {ds}: removed={sorted(removed)}, expected {todo}"
    assert not (targets & names(ds, "next")), f"{ds}: targets still present"
if not apply:
    print("Nothing deleted. Re-run with APPLY=1.")
else:
    print("OK: pooled tables removed from the drafts. Release irw_conjoint and irw_conjoint_2 together.")
