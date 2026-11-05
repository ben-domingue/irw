"""#3237: two published tables whose ids restart in each sample, rebuilt from the live tables (2026-11-05).

face_memory_amado_2024 (shard 2): Phase 2 and Phase 3 of EGEFACE are separate samples whose P_IDs
both start at 1 (105 shared ids; age, sex and group disagree across phases for the same id). Phase-2
ids are offset by 1000; cov_phase stays. 597 -> 702 respondents, 0 repeated id+item.

selfcompassionscale_shortform_fuochi_2025 (shard 1): ships the sample prefix data/...fuochi_2025.R has
carried since #1842 (merged 2026-09-03, never uploaded), and clears the literal "NA" resp. 300
within-sample repeats remain, accepted under #1856 (PR #2420).

Usage: python3 tools/repairs/repair_3237_sample_collisions_2026-11-05.py <out_dir>
"""
import redivis, warnings, pandas as pd, sys
warnings.filterwarnings("ignore")
S=sys.argv[1]
# face_memory_amado_2024: phase 2 and phase 3 are separate samples whose P_IDs both start at 1
fm=redivis.organization("datapages").dataset("item_response_warehouse_2").table("face_memory_amado_2024").to_pandas_dataframe(progress=False)
cols=list(fm.columns)
assert fm.id.max() < 1000
fm["id"]=fm.id.astype("int64")+(fm.cov_phase==2).astype("int64")*1000
assert not fm.duplicated(["id","item"]).any()
fm[cols].to_csv(f"{S}/face_memory_amado_2024.csv",index=False,na_rep="")
print("face_memory", len(fm), fm.id.nunique())
# fuochi: ship the #1842 sample prefix (merged 2026-09-03, never uploaded); literal "NA" resp -> missing
fu=redivis.organization("datapages").dataset("item_response_warehouse").table("selfcompassionscale_shortform_fuochi_2025").to_pandas_dataframe(progress=False)
n=len(fu)
fu["id"]=fu.cov_sample+"_"+fu.id.astype(str)
fu["resp"]=pd.to_numeric(fu.resp.replace("NA",pd.NA))
print("fuochi", n, len(fu), "dup", fu.duplicated(["id","item"]).sum(), "ids", fu.id.nunique(), "na", fu.resp.isna().sum())
fu[["id","item","resp","cov_sample"]].to_csv(f"{S}/selfcompassionscale_shortform_fuochi_2025.csv",index=False,na_rep="")
