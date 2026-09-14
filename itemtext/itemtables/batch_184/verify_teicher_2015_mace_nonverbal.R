# verify_teicher_2015_mace_nonverbal.R -- copied from references/verify_template.R
#
# Claim: item codes Closet / P_diff_please / P_no_time / Financial_pressure /
# Kept_secrets (S9 File column names, used verbatim by data/teicher_2015_mace_items.py)
# carry the MACE-X wording of items 6 / 55 / 56 / 66 / 67, and resp 1 = "Yes", 0 = "No".
#
# Falsifiable prediction: Teicher & Parigger (2015) PLOS ONE Table 3 (image,
# doi:10.1371/journal.pone.0117423.t003) prints "% Yes" for each non-verbal
# emotional abuse item against its wording (n = 1048). The five shipped items'
# published values are 3.3 / 43.9 / 24.0 / 37.4 / 30.3 -- pairwise at least 6.3
# points apart -- so each observed live %resp==1 must match its OWN published
# value and no other item's. A swap of any two item_texts, or a flipped Yes/No
# direction (Closet would read 96.7), breaks this.

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_nonverbal"

# Table 3, "% Yes", keyed by the wording printed there (MACE-52 numbering in parens)
PUBLISHED <- c(
    Closet             = 3.3,   # (5)  Locked you in closet, basement, garage, etc.
    P_diff_please      = 43.9,  # (40) Parent very difficult to please
    P_no_time          = 24.0,  # (41) Parent no time or interest
    Financial_pressure = 37.4,  # (49) Felt family financial pressure
    Kept_secrets       = 30.3   # (50) Kept important secrets/facts from you
)
# Table 3 also lists (48) "Had to shoulder adult responsibilities" 33.9 -- not in this table.
TOL <- 0.5  # percentage points; paper n=1048 vs live n (1050 non-missing in S9)

d <- irw::irw_fetch(TABLE)
n_obs <- tapply(d$resp, d$item, length)
pct <- 100 * tapply(d$resp == 1, d$item, mean)
pct <- pct[names(PUBLISHED)]

cat(sprintf("%-20s %6s %10s %10s %8s  %s\n", "item", "n", "published", "observed", "diff", "nearest published"))
ok <- TRUE
for (it in names(PUBLISHED)) {
    nearest <- names(PUBLISHED)[which.min(abs(PUBLISHED - pct[[it]]))]
    dev <- pct[[it]] - PUBLISHED[[it]]
    cat(sprintf("%-20s %6d %10.1f %10.2f %8.2f  %s\n", it, n_obs[[it]], PUBLISHED[[it]], pct[[it]], dev, nearest))
    if (abs(dev) > TOL || nearest != it) ok <- FALSE
}
gaps <- dist(PUBLISHED)
cat(sprintf("\nsmallest gap between published values: %.1f points (tolerance %.1f)\n", min(gaps), TOL))
cat(sprintf("resp values present: %s\n", paste(sort(unique(d$resp)), collapse = ", ")))
cat("Every item's observed %Yes must sit within tolerance of its own published value AND be\n",
    "nearest to it; with gaps >= 6.3 points this distinguishes all 5 items from each other and\n",
    "fixes resp=1 as 'Yes'. It does not check section_prompt wording or the online form's layout.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
