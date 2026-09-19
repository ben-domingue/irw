# verify_ordak_2026_vaccine_misreasoning.R
#
# CLAIM UNDER TEST: each item code carries the Table 1 definition of the SAME
# misreasoning category the code names -- i.e. `base_rate_neglect` holds the
# base-rate-neglect definition rather than, say, the denominator-neglect one.
#
# FALSIFIABLE PREDICTION: PLOS ONE 10.1371/journal.pone.0355341 Table 2 publishes,
# for each of the ten named categories, the number of the 597 posts in which that
# category was identified. Those ten counts are all distinct, so if any two item
# codes were swapped relative to their category names the counts would no longer
# line up. This checks the mapping, not the item set.
#
# It also fixes the direction of `resp`: the count matched is the count of resp == 1,
# so 1 = category identified in the post, 0 = not identified (which is what
# option_text says).

suppressMessages(library(irw))

TABLE <- "ordak_2026_vaccine_misreasoning"

# Paper Table 2, "Prevalence of statistical misreasoning categories across 597
# analysed posts" (column n), keyed by the IRW item code for the same category.
PUBLISHED <- c(
  correlation_causation      = 420,
  base_rate_neglect          = 347,
  denominator_neglect        = 296,
  cherry_picking             = 295,
  small_sample_fallacy       = 263,
  intuitive_reasoning        = 238,
  overinterpretation_pct     = 189,
  relative_absolute_risk     = 160,
  random_fluctuation         = 127,
  graphical_scale_misreading =  76
)

d <- irw::irw_fetch(TABLE)          # 5,970 rows -- a negligible export
d$resp <- as.numeric(d$resp)
obs <- tapply(d$resp, d$item, function(v) sum(v == 1, na.rm = TRUE))
obs <- obs[names(PUBLISHED)]

cat(sprintf("%-28s %10s %10s %6s\n", "item", "Table 2 n", "resp==1", "diff"))
for (i in seq_along(PUBLISHED))
  cat(sprintf("%-28s %10d %10d %6d\n", names(PUBLISHED)[i], PUBLISHED[i],
              obs[i], obs[i] - PUBLISHED[i]))

ok <- all(obs == PUBLISHED) && length(unique(PUBLISHED)) == length(PUBLISHED)
cat(sprintf("\nall ten counts match exactly: %s; all ten published counts distinct: %s\n",
            all(obs == PUBLISHED), length(unique(PUBLISHED)) == length(PUBLISHED)))
cat("Note: this pins each item code to its category name and the resp direction.\n",
    "It does NOT independently re-check the wording of the definition text itself,\n",
    "which is transcribed from Table 1 under the same category names.\n", sep = "")

cat(if (isTRUE(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
