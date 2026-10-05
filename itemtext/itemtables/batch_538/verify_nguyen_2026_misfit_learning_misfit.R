# verify_nguyen_2026_misfit_learning_misfit.R -- Step 5b check, batch_538.
#
# Claim being verified: live item MF1/MF2/MF3 is the deposit column of the same name
# (Mendeley 10.17632/j8tkztz636 V3 data .xlsx, sha256 dff3f0ee...b03b4 / 9dda4cc9...81f6,
# the two copies are cell-identical), and the deposit's own Appendix_Questionnaire_Revised.docx
# (sha256 ff366998...970bf) prints each item's wording against those very codes, MF1..MF3,
# under the "Learning Misfit" heading. data/nguyen_2026_online_learning_misfit.py melts the
# .xlsx columns by name, so the IRW code IS the source column name.
#
# What this route establishes:
#  (a) live code -> deposit column: per-item response-frequency match, cell for cell, against
#      counts hard-coded below from the .xlsx. The three count vectors all differ, so any
#      permutation of codes would break the match (checked: cross-matches must be 0).
#  (b) deposit column -> wording: the questionnaire's printed code labels. It prints exactly
#      three MF items (MF1, MF2, MF3) and the data carry exactly MF1-MF3, so unlike the
#      sibling PE block (4 printed / 3 in data) there is no dropped item and no possible
#      renumbering; every code has exactly one printed wording.
# What it does NOT establish: (b) is a label match, not a statistical test -- the three items
# share one 1-5 scale (means 3.05/3.02/3.05, inter-item r 0.78-0.82) and no per-item
# statistics are published, so no data route could independently catch the authors
# mislabelling their own columns.

suppressMessages(library(irw))
TABLE <- "nguyen_2026_misfit_learning_misfit"

SOURCE <- list(                       # counts of resp 1..5 per deposit column
  MF1 = c(171, 335, 724, 411, 182),
  MF2 = c(179, 371, 689, 396, 188),
  MF3 = c(182, 348, 677, 431, 185))
PRINTED_CODES <- c("MF1", "MF2", "MF3")  # questionnaire "Learning Misfit" block

d <- irw::irw_fetch(TABLE)
ok <- TRUE
cnt <- function(it) as.integer(table(factor(d$resp[d$item == it], levels = 1:5)))
cat(sprintf("%-5s %-26s %-26s %s\n", "item", "deposit counts (1..5)", "live counts (1..5)", "mean"))
for (it in names(SOURCE)) {
  live <- cnt(it)
  cat(sprintf("%-5s %-26s %-26s %.4f %s\n", it, paste(SOURCE[[it]], collapse = "/"),
              paste(live, collapse = "/"), mean(d$resp[d$item == it]),
              if (all(live == SOURCE[[it]])) "match" else "MISMATCH"))
  ok <- ok && all(live == SOURCE[[it]])
}
perm_hits <- 0
for (a in names(SOURCE)) for (b in names(SOURCE))
  if (a != b && all(cnt(a) == SOURCE[[b]])) perm_hits <- perm_hits + 1
cat(sprintf("cross-matches between different codes: %d (must be 0)\n", perm_hits))
ok <- ok && perm_hits == 0
same_codes <- setequal(PRINTED_CODES, sort(unique(d$item))) && length(PRINTED_CODES) == length(unique(d$item))
cat(sprintf("printed codes %s vs live codes %s: %s\n", paste(PRINTED_CODES, collapse = ","),
            paste(sort(unique(d$item)), collapse = ","), if (same_codes) "identical, 1:1" else "DIFFER"))
ok <- ok && same_codes
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
