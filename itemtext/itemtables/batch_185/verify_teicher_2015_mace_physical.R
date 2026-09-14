# verify_teicher_2015_mace_physical.R -- copied from references/verify_template.R
#
# Claim: item codes Pushed / Hit / Hit_med / Spank_open / Spanked_bare / Spanked_strap
# (S9 File column names, used verbatim by data/teicher_2015_mace_items.py) carry the
# MACE-X wording of items 7 / 8 / 9 / 10 / 11 / 12, and resp 1 = "Yes", 0 = "No".
#
# Falsifiable prediction: Teicher & Parigger (2015) PLOS ONE Table 4 (image,
# doi:10.1371/journal.pone.0117423.t004, "Rasch analysis of parental physical
# maltreatment scale", Observations = 1051 per item) prints "% Yes" for each item
# against an abbreviated wording. Published values are 30.9 / 15.1 / 3.1 / 63.7 /
# 23.1 / 24.5. With n = 1051 each published value pins an integer count to within
# one respondent, so each item's live %resp==1 must reproduce its OWN value to
# rounding (0.05 points; tolerance set at 0.1) and be nearest to it. The closest
# pair is Spanked_bare 23.1 vs Spanked_strap 24.5 (1.4 points = ~14 respondents),
# 14x the tolerance, so a swap of those two -- or any other pair -- fails, as does a
# flipped Yes/No direction (Spank_open would read 36.3).

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_physical"

# Table 4, "% Yes", keyed by the wording printed there (MACE-52 numbering)
PUBLISHED <- c(
    Pushed        = 30.9,  # 6.  Intentionally pushed, pinched, slapped, kicked etc.
    Hit           = 15.1,  # 7   Hit you so hard it left marks for more than a few minutes
    Hit_med       = 3.1,   # 8   Hit or harmed you so severely that it needed medical attention
    Spank_open    = 63.7,  # 9   Spanked you on buttocks, arms or legs
    Spanked_bare  = 23.1,  # 10  Spanked you on unclothed buttocks
    Spanked_strap = 24.5   # 11  Spanked you with object (belt, paddle)
)
PUB_N <- 1051
TOL <- 0.1  # percentage points; published to one decimal, same n as live

d <- irw::irw_fetch(TABLE)
n_obs <- tapply(d$resp, d$item, length)
pct <- 100 * tapply(d$resp == 1, d$item, mean)

cat(sprintf("%-14s %6s %10s %10s %8s  %-14s %s\n", "item", "n", "published", "observed",
            "diff", "nearest pub.", "flipped(%resp==0)"))
ok <- TRUE
for (it in names(PUBLISHED)) {
    nearest <- names(PUBLISHED)[which.min(abs(PUBLISHED - pct[[it]]))]
    dev <- pct[[it]] - PUBLISHED[[it]]
    cat(sprintf("%-14s %6d %10.1f %10.2f %8.2f  %-14s %.2f\n", it, n_obs[[it]], PUBLISHED[[it]],
                pct[[it]], dev, nearest, 100 - pct[[it]]))
    if (abs(dev) > TOL || nearest != it || n_obs[[it]] != PUB_N) ok <- FALSE
}
gaps <- dist(PUBLISHED)
cat(sprintf("\nsmallest gap between published values: %.1f points (tolerance %.1f)\n", min(gaps), TOL))
cat(sprintf("resp values present: %s\n", paste(sort(unique(d$resp)), collapse = ", ")))

# Wording-consistency check (not a mapping route on its own): the general spanking item
# must contain both specific spanking items, as its wording implies.
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
nb <- sum(w$resp.Spanked_bare == 1 & w$resp.Spank_open == 0, na.rm = TRUE)
ns <- sum(w$resp.Spanked_strap == 1 & w$resp.Spank_open == 0, na.rm = TRUE)
db <- sum(w$resp.Spanked_bare == 1, na.rm = TRUE)
ds <- sum(w$resp.Spanked_strap == 1, na.rm = TRUE)
cat(sprintf("Spanked_bare=1 & Spank_open=0: %d of %d; Spanked_strap=1 & Spank_open=0: %d of %d\n",
            nb, db, ns, ds))
if (nb > 0 || ns > 0 || db == 0 || ds == 0) ok <- FALSE

cat("Every item's observed %Yes must reproduce its own published value AND be nearest to it;\n",
    "with a minimum gap of 1.4 points against a 0.1 tolerance this distinguishes all 6 items\n",
    "from each other and fixes resp=1 as 'Yes'. It does not check section_prompt wording or\n",
    "the online administration's layout.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
