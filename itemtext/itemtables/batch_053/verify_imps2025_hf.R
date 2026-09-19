# verify_imps2025_hf.R -- Step 5b evidence for imps2025_hf (Hearts and Flowers).
#
# THE CLAIM. Two mappings were made and both are testable against the live data:
#   (a) the item code names the stimulus -- "heart left" is a red heart shown on the
#       left, and so the heart section_prompt ("Press on the same side as the
#       stimulus.") governs it, while "flower *" takes the opposite-side rule;
#   (b) option_text Incorrect=0 / Correct=1 is the accuracy coding
#       data/imps2025_hf.R defines: heart trials score 1 iff resp_side == stim_side,
#       flower trials score 1 iff resp_side != stim_side.
# The live table keeps stim_shape, stim_side and resp_side as covariates, so both
# claims are checkable cell-for-cell rather than statistically.
#
# NO EXPORT: this runs one server-side GROUP BY (8 rows out), not irw_fetch().
# Nothing here re-checks item counts -- validate_items.R already did that.

suppressMessages(library(irw))
ns <- getNamespace("irw")

TABLE <- "imps2025_hf"
tbl <- ns$.fetch_redivis_table(TABLE, source = ns$.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference

q <- sprintf(paste(
  "SELECT CAST(item AS STRING) item, CAST(stim_shape AS STRING) stim_shape,",
  "CAST(stim_side AS STRING) stim_side, CAST(resp_side AS STRING) resp_side,",
  "CAST(resp AS STRING) resp, COUNT(*) n FROM `%s`",
  "GROUP BY 1,2,3,4,5 ORDER BY 1,2,3,4,5"), ref)
d <- as.data.frame(ns$.irw_query_tibble(q))
d$n <- as.numeric(d$n)

cat("-- item x stimulus x response cross-tab (server-side, no export) --\n")
print(d, row.names = FALSE)
cat(sprintf("\ntotal rows in cross-tab: %s\n", format(sum(d$n), big.mark = ",")))

# (a) does the item code equal "<stim_shape> <stim_side>"?
bad_code <- d[d$item != paste(d$stim_shape, d$stim_side), ]
cat(sprintf("\n(a) rows whose item code disagrees with their own stim_shape/stim_side: %s of %s\n",
            format(sum(bad_code$n), big.mark = ","), format(sum(d$n), big.mark = ",")))

# (b) does resp=1 mean "correct" under the shipped heart-same / flower-opposite rule?
expected <- ifelse(d$stim_shape == "heart",
                   ifelse(d$stim_side == d$resp_side, "1", "0"),
                   ifelse(d$stim_side != d$resp_side, "1", "0"))
bad_resp <- d[d$resp != expected, ]
cat(sprintf("(b) rows violating resp=1 <=> (heart & same side) or (flower & opposite side): %s of %s\n",
            format(sum(bad_resp$n), big.mark = ","), format(sum(d$n), big.mark = ",")))
if (nrow(bad_resp)) print(bad_resp, row.names = FALSE)

# Corroboration: the congruency effect must run heart > flower in accuracy.
acc <- tapply(d$n * (d$resp == "1"), d$stim_shape, sum) / tapply(d$n, d$stim_shape, sum)
cat(sprintf("\naccuracy by stimulus: heart %.3f (congruent) vs flower %.3f (incongruent) -- diff %.3f\n",
            acc[["heart"]], acc[["flower"]], acc[["heart"]] - acc[["flower"]]))

cat("\nNOT established by this script: it verifies the item code, the rule attached to each\n",
    "item, and the accuracy coding. It says nothing about whether the canonical Wright &\n",
    "Diamond (2014) instruction wording matches the script this study read to children --\n",
    "that script was never published, which is what the public_note discloses. item_text is\n",
    "blank by design (picture stimuli).\n", sep = "")

ok <- sum(bad_code$n) == 0 && sum(bad_resp$n) == 0 && acc[["heart"]] > acc[["flower"]]
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
