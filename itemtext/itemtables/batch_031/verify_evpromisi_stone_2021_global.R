# verify_evpromisi_stone_2021_global.R
#
# STATUS: this table is BLOCKED ON RIGHTS and ships NO __items.csv. The PROMIS
# Global Health wording is HealthMeasures instrument content, whose Terms of Use
# (Approved Version 1.12-2017) bar reproducing or distributing the instrument to
# third parties without prior written agreement; per the 2026-09-04 DSES ruling
# that clause outranks the CC0 licence of the Harvard Dataverse deposit the
# wording would have come from. See notes_evpromisi_stone_2021_global.csv.
#
# What this script therefore checks is the mapping that WOULD have shipped, so the
# extraction can be reopened without redoing it if Ben rules PROMIS an exception.
#
# THE CLAIM: the deposit's five sample codebooks
# (Codebook - Ecological Validity of PROMIS - <sample> sample.docx, Participant
# characteristics table) assign response scales per item as follows --
#   Global01..Global06, Global08..Global10 : 1-5 (5 levels)
#   Global07 ("In the past 7 days ... How would you rate your pain on average?")
#                                           : 0-10 numeric rating (11 levels)
# That is a falsifiable structural prediction about the live data: exactly one item,
# and specifically Global07, must carry the 0-10 range.
#
# WHAT THIS DOES NOT ESTABLISH: it pins Global07 and only Global07. The other nine
# items all share a 1-5 scale and this route cannot tell them apart, which is why the
# verification row is NO_ROUTE/partial-at-best rather than VERIFIED. Their mapping
# rests on the codebook stating each code beside its own stem, not on the data.
#
# Deliberately uses irw::irw_table_sets() (server-side aggregate) rather than
# irw_fetch(), so re-running it costs no Redivis export quota.

suppressMessages(library(irw))

TABLE <- "evpromisi_stone_2021_global"

# Predicted from the deposit codebooks (identical in all five sample files).
PRED <- data.frame(
  item     = sprintf("Global%02d", 1:10),
  min      = c(1, 1, 1, 1, 1, 1, 0, 1, 1, 1),
  max      = c(5, 5, 5, 5, 5, 5, 10, 5, 5, 5),
  n_levels = c(5, 5, 5, 5, 5, 5, 11, 5, 5, 5),
  stringsAsFactors = FALSE
)

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
obs <- as.data.frame(s$per_item)
obs <- obs[match(PRED$item, obs$item), ]

cat(sprintf("%-9s %5s  %9s %9s   %9s %9s   %s\n",
            "item", "n", "pred_min", "obs_min", "pred_max", "obs_max", "levels pred/obs"))
ok <- TRUE
for (i in seq_len(nrow(PRED))) {
  hit <- isTRUE(obs$resp_min[i] == PRED$min[i]) &&
         isTRUE(obs$resp_max[i] == PRED$max[i]) &&
         isTRUE(obs$n_resp_levels[i] == PRED$n_levels[i])
  ok <- ok && hit
  cat(sprintf("%-9s %5s  %9s %9s   %9s %9s   %s/%s  %s\n",
              PRED$item[i], obs$n[i], PRED$min[i], obs$resp_min[i],
              PRED$max[i], obs$resp_max[i], PRED$n_levels[i],
              obs$n_resp_levels[i], if (hit) "" else "<-- MISMATCH"))
}

# The discriminating fact: 0-10 must be unique to Global07.
wide <- obs$item[obs$resp_max == 10]
cat(sprintf("\nitems with a 0-10 range: %s (codebook predicts exactly Global07)\n",
            paste(wide, collapse = ", ")))
uniq <- identical(wide, "Global07")
if (!uniq) ok <- FALSE

cat("Note: this route pins Global07 alone. Global01-06 and Global08-10 all share the\n",
    "1-5 scale and are NOT distinguished from one another here; their code-to-text tie\n",
    "comes from the codebook naming each code beside its stem, not from the data.\n", sep = "")
cat("Note: no item text was shipped for this table -- see the rights block above.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
