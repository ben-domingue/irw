# verify_carney_2023_substance_use.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: each IRW item code names the substance indicator whose
# item_text we shipped, and in particular that `alcohol` is the AUDIT
# hazardous/harmful-use dichotomy (>8) rather than "any alcohol use".
#
# ROUTE: published per-substance prevalence (Carney et al. 2023, PLOS ONE
# 10.1371/journal.pone.0290781, Results / "Substance use prevalence") matched
# against the count of resp==1 in each column of the study's own S1 dataset --
# the file data/carney_2023_substance_use.py melts into the IRW table, with
# `item` taken verbatim from the column name (so the column IS the item code).
# The eight published counts are all distinct, so the match distinguishes every
# item from every other.
#
# QUOTA: no irw_fetch() here by design (standing rule: never export a published
# table to satisfy a gate). Live structure is confirmed with the server-side
# aggregates of irw::irw_table_sets().

suppressMessages(library(irw))

TABLE <- "carney_2023_substance_use"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0290781.s001"

# Published counts of participants positive on each indicator (n = 414).
PUBLISHED <- c(alcohol = 147, stimulant = 98, sedatives = 50, opioid = 20,
               `club drugs` = 36, cannabis = 284, amylnitrite = 65,
               hallucinogen = 58)

cache <- file.path(".cache", TABLE, "s001.xlsx")
if (!file.exists(cache)) {
    dir.create(dirname(cache), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(URL, cache, mode = "wb", quiet = TRUE)
}
df <- as.data.frame(readxl::read_excel(cache))
names(df) <- trimws(names(df))

obs <- sapply(names(PUBLISHED), function(c) sum(df[[c]] == 1, na.rm = TRUE))

cat(sprintf("%-14s %10s %10s %6s\n", "item", "published", "observed", "diff"))
for (i in seq_along(obs))
    cat(sprintf("%-14s %10d %10d %6d\n", names(obs)[i], PUBLISHED[i],
                obs[i], obs[i] - PUBLISHED[i]))

counts_ok <- all(obs == PUBLISHED)
distinct_ok <- !any(duplicated(PUBLISHED))
cat(sprintf("\nall eight counts match: %s | all published counts distinct: %s\n",
            counts_ok, distinct_ok))

# Live structure, server-side (no export).
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pit <- as.data.frame(s$per_item)
live_ok <- setequal(s$items, names(PUBLISHED)) && setequal(s$resp, c(0, 1)) &&
    all(pit$n == 414)
cat(sprintf("live: %d items, resp set {%s}, per-item n all 414: %s\n",
            length(s$items), paste(sort(s$resp), collapse = ","), live_ok))

cat("Note: this does NOT establish the literal administered ASSIST/AUDIT wording",
    "-- the paper names both instruments but reproduces no item stems, so",
    "item_text describes the derived binary indicator in the paper's own words.",
    "Live per-item resp==1 counts were not re-exported (quota); the check runs",
    "against the S1 file the processing script melts by column name.\n", sep = "\n")

cat(if (counts_ok && distinct_ok && live_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
