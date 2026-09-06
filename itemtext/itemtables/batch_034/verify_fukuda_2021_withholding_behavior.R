# verify_fukuda_2021_withholding_behavior.R
#
# CLAIM UNDER TEST: withholding_item1..6 carry the six "Withholding ..." columns of
# S1 Data (10.1371/journal.pone.0257552.s001) in file order, and the item_text shipped
# for each is the matching question in the paper's Table 4.
#
# FALSIFIABLE PREDICTION: Table 4 publishes the number of "Yes" responses for each of
# those six questions (N column). If any two item codes were swapped, the per-item
# count of resp == 1 in the live IRW table would no longer line up with the count
# published beside the question we shipped for that code. All six published counts are
# distinct (929/959/747/911/358/354), so this separates EVERY item from every other
# item -- including the closest pair, 358 vs 354.

suppressMessages(library(irw))

TABLE <- "fukuda_2021_withholding_behavior"

# Fukuda, Ando & Fukuda (2021) PLOS ONE 16(9):e0257552, Table 4, "N" column for Yes.
PUBLISHED <- c(
  withholding_item1 = 929,  # Do you refrain from sightseeing and traveling to tourist spots?
  withholding_item2 = 959,  # Do you refrain from get-togethers that involve eating/drinking?
  withholding_item3 = 747,  # Do you refrain from going out?
  withholding_item4 = 911,  # Do you refrain from visiting amusement/entertainment facilities such as pachinko parlors?
  withholding_item5 = 358,  # Do you hold off on being examined by a physician?
  withholding_item6 = 354   # Do you hold off on being examined by a dentist?
)

# Server-side GROUP BY rather than irw_fetch(): the corpus export quota is
# account-wide, and this needs 12 numbers, not 6000 rows.
obs <- tryCatch({
    tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
    q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, COUNT(*) AS n FROM `%s`",
                       "WHERE SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) = 1",
                       "GROUP BY item"), tbl$qualified_reference)
    r <- as.data.frame(irw:::.irw_query_tibble(q))
    setNames(r$n, r$item)
}, error = function(e) {
    message("query route failed (", conditionMessage(e), "); falling back to irw_fetch()")
    d <- irw::irw_fetch(TABLE)
    tapply(as.numeric(d$resp) == 1, d$item, sum)
})

obs <- obs[names(PUBLISHED)]

cat(sprintf("%-20s %10s %10s %6s\n", "item", "published", "observed", "diff"))
for (i in seq_along(PUBLISHED))
    cat(sprintf("%-20s %10d %10d %6d\n", names(PUBLISHED)[i], PUBLISHED[i],
                as.integer(obs[i]), as.integer(obs[i]) - PUBLISHED[i]))

ok <- all(!is.na(obs)) && all(as.integer(obs) == PUBLISHED)
cat(sprintf("\nexact matches: %d of %d\n", sum(!is.na(obs) & as.integer(obs) == PUBLISHED), length(PUBLISHED)))
cat("Note: all six published Yes-counts are distinct, so this pins each item code to a\n",
    "specific Table 4 question. It does NOT verify the option labels beyond the direction\n",
    "Yes=1 (the paper states 1=yes, 0=no), and it says nothing about the Japanese wording\n",
    "respondents actually read -- only English is published.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
