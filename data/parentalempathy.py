"""
Requirements:
    pip install pyreadstat pandas --break-system-packages

Input files (place in the same folder, or edit the paths below):
    Repository_Copy_Undergrad_Analog_Data.sav   -> Study 1 (pilot, N=142)
    Repository_Copy_Triple-F_Data.sav           -> Study 2 (parents, N=212)

Output:
    One CSV per construct/sample, written to OUT_DIR, named per the IRW
    convention: [study]_[author]_[year]_[subconstruct]_[sample].csv
"""

import os
import re

import pandas as pd
import pyreadstat

# ---------------------------------------------------------------------------
# Config — edit these paths as needed
# ---------------------------------------------------------------------------
STUDY1_PATH = "Repository Copy Undergrad Analog Data.sav"
STUDY2_PATH = "Repository Copy Triple-F Data.sav"
OUT_DIR = "./irw_tables"

os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Reshaping helpers
# ---------------------------------------------------------------------------
def simple_melt(df, id_col, cols, out_id_prefix="", cov=None):
    """
    Wide -> long for a plain questionnaire block (e.g. EQS1..EQS22), where
    each column IS the item and the item name can be kept as-is.

    cov: optional DataFrame with an 'id' column plus one or more cov_*
    columns to attach (person-level covariates, constant across a person's
    items — e.g. condition, role).
    """
    sub = df[[id_col] + cols].copy()
    long = sub.melt(id_vars=id_col, value_vars=cols, var_name="item", value_name="resp")
    long = long.rename(columns={id_col: "id"})
    long["id"] = out_id_prefix + long["id"].astype(str)
    long = long.dropna(subset=["resp"])

    if cov is not None:
        cov_df = cov.copy()
        cov_df["id"] = out_id_prefix + cov_df["id"].astype(str)
        long = long.merge(cov_df, on="id", how="left")

    return long.sort_values(["id", "item"]).reset_index(drop=True)


def empat_blocks(df, meta, id_col, table_match, out_id_prefix=""):
    """
    Wide -> long for an EMPAT stimulus-response block, where a single
    stimulus (e.g. "Boy Happy" audio clip) is rated on several emotions,
    and the column name alone doesn't identify the emotion (columns are
    just numbered .1-.10). We recover the correct grouping and emotion
    label from each column's SPSS variable *label* instead of its name,
    e.g. label "EMPA-TEA Child Boy Happy: Scared" ->
         stimulus = "EMPA-TEA Child Boy Happy", emotion = "Scared".

    table_match: list of substrings that must ALL appear in the stimulus
    label to select this construct, e.g. ["EMPA-TEA", "Child"].
    """
    groups = {}
    for c in df.columns:
        label = meta.column_names_to_labels.get(c)
        if not label or ":" not in label:
            continue
        stim, emo = [x.strip() for x in label.split(":", 1)]
        if all(tok in stim for tok in table_match):
            groups.setdefault(stim, {})[c] = emo

    if not groups:
        return None

    blocks = []
    for stim, colmap in groups.items():
        stim_slug = re.sub(r"[^A-Za-z0-9]+", "_", stim).strip("_")
        cols = list(colmap.keys())
        sub = df[[id_col] + cols].copy()
        long = sub.melt(id_vars=id_col, value_vars=cols, var_name="col", value_name="resp")
        long["item"] = stim_slug + "__" + long["col"].map(colmap)
        blocks.append(long.drop(columns="col"))

    out = pd.concat(blocks, ignore_index=True)
    out = out.rename(columns={id_col: "id"})
    out["id"] = out_id_prefix + out["id"].astype(str)
    out = out.dropna(subset=["resp"])
    return out[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
df1, meta1 = pyreadstat.read_sav(STUDY1_PATH)
df2, meta2 = pyreadstat.read_sav(STUDY2_PATH)

id1 = id2 = "ID#"
results = {}

# ---------------------------------------------------------------------------
# Study 1 — undergrad pilot (N=142)
# ---------------------------------------------------------------------------
cov_ea = df1[[id1, "EmpEA.Child.Version", "EmpEA.Self.Version"]].rename(columns={
    id1: "id",
    "EmpEA.Child.Version": "cov_ea_child_order",
    "EmpEA.Self.Version": "cov_ea_self_order",
})

results["parentalempathy_gonzalez_2021_eqs_pilot"] = simple_melt(
    df1, id1, [f"EQS{i}" for i in range(1, 23)])
results["parentalempathy_gonzalez_2021_iri_pilot"] = simple_melt(
    df1, id1, [f"IRI{i}" for i in range(1, 15)])
results["parentalempathy_gonzalez_2021_empates_child_pilot"] = empat_blocks(
    df1, meta1, id1, ["EMPA-TES", "Child"])
results["parentalempathy_gonzalez_2021_empates_self_pilot"] = empat_blocks(
    df1, meta1, id1, ["EMPA-TES", "Self"])

empeac1 = empat_blocks(df1, meta1, id1, ["EMPA-TEA", "Child"])
empeas1 = empat_blocks(df1, meta1, id1, ["EMPA-TEA", "Self"])
results["parentalempathy_gonzalez_2021_empatea_child_pilot"] = empeac1.merge(
    cov_ea[["id", "cov_ea_child_order"]], on="id", how="left")
results["parentalempathy_gonzalez_2021_empatea_self_pilot"] = empeas1.merge(
    cov_ea[["id", "cov_ea_self_order"]], on="id", how="left")

# ---------------------------------------------------------------------------
# Study 2 — Triple-F parent sample, Time 4 (N=212)
# ---------------------------------------------------------------------------
cov_role = df2[[id2]].copy()
cov_role["cov_parent_role"] = df2[id2].str.extract(r"(MOM|DAD)$")[0]
cov_role = cov_role.rename(columns={id2: "id"})

paq_items = ["PAQ4", "PAQ5", "PAQ8", "PAQ11", "PAQ15", "PAQ20", "PAQ22", "PAQ23", "PAQ27", "PAQ30"]
reacct_items = ["Reacct2", "Reacct5", "Reacct6", "Reacct10", "Reacct11", "Reacct12", "Reacct16", "Reacct18"]

results["parentalempathy_gonzalez_2021_pem_tripleF"] = simple_melt(
    df2, id2, [f"PEM{i}" for i in range(1, 26)], cov=cov_role)
results["parentalempathy_gonzalez_2021_pareqs_tripleF"] = simple_melt(
    df2, id2, [f"PAR_EQS{i}" for i in range(1, 20)], cov=cov_role)
results["parentalempathy_gonzalez_2021_paqauthoritative_tripleF"] = simple_melt(
    df2, id2, paq_items, cov=cov_role)
results["parentalempathy_gonzalez_2021_iri_tripleF"] = simple_melt(
    df2, id2, [f"IRI{i}" for i in range(1, 15)], cov=cov_role)
results["parentalempathy_gonzalez_2021_parycsupport_tripleF"] = simple_melt(
    df2, id2, [f"PARYC{i}" for i in range(1, 8)], cov=cov_role)
results["parentalempathy_gonzalez_2021_reacctcompliance_tripleF"] = simple_melt(
    df2, id2, reacct_items, cov=cov_role)

empeac2 = empat_blocks(df2, meta2, id2, ["EMPA-TEA", "Child"])
empeas2 = empat_blocks(df2, meta2, id2, ["EMPA-TEA", "Self"])
empesc2 = empat_blocks(df2, meta2, id2, ["EMPA-TES", "Child"])
results["parentalempathy_gonzalez_2021_empatea_child_tripleF"] = empeac2.merge(cov_role, on="id", how="left")
results["parentalempathy_gonzalez_2021_empatea_self_tripleF"] = empeas2.merge(cov_role, on="id", how="left")
results["parentalempathy_gonzalez_2021_empates_child_tripleF"] = empesc2.merge(cov_role, on="id", how="left")

# ---------------------------------------------------------------------------
# Write CSVs + print a summary you can sanity-check against the paper
# ---------------------------------------------------------------------------
summary = []
for name, tbl in results.items():
    if tbl is None:
        summary.append((name, "MISSING", None, None))
        continue
    tbl.to_csv(f"{OUT_DIR}/{name}.csv", index=False)
    summary.append((name, tbl.shape[0], tbl["id"].nunique(), tbl["item"].nunique()))

print(pd.DataFrame(summary, columns=["table", "n_rows", "n_ids", "n_items"]).to_string(index=False))