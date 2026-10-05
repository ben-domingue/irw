# verify_nguyen_2026_misfit_academic_performance.R -- Step 5b check, batch_537.
#
# Claim being verified: live item PE1/PE2/PE3 is the deposit column of the same name
# (Mendeley 10.17632/j8tkztz636 V3 data .xlsx, sha256 dff3f0ee...b03b4 / 9dda4cc9...81f6,
# the two copies are cell-identical), and the deposit's own Appendix_Questionnaire_Revised.docx
# prints the wording against those very codes (PE1..PE4).
#
# What this route establishes: per-item response-frequency match, cell for cell, between the
# live table and the deposit's named columns (hard-coded below from the .xlsx). The three
# columns' count vectors all differ from one another, so a permutation of codes would break
# the match.
# What it does NOT establish: the questionnaire prints FOUR PE items (PE1-PE4) while every
# data file in the deposit (V1-V3, and the 3,676-row copy in 10.17632/hd2z967zjh) carries
# only PE1-PE3. If the authors dropped one item and renumbered the rest, the code labels
# would no longer tie to the printed wording, and nothing in the data (one shared 1-5 scale,
# no published per-item statistics) can test that. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "nguyen_2026_misfit_academic_performance"

SOURCE <- list(                       # counts of resp 1..5 per deposit column
  PE1 = c(204, 365, 688, 380, 186),
  PE2 = c(207, 330, 693, 403, 190),
  PE3 = c(212, 350, 665, 390, 206))

d <- irw::irw_fetch(TABLE)
ok <- TRUE
cat(sprintf("%-5s %-28s %-28s\n", "item", "deposit counts (1..5)", "live counts (1..5)"))
for (it in names(SOURCE)) {
  live <- as.integer(table(factor(d$resp[d$item == it], levels = 1:5)))
  cat(sprintf("%-5s %-28s %-28s %s\n", it, paste(SOURCE[[it]], collapse = "/"),
              paste(live, collapse = "/"), if (all(live == SOURCE[[it]])) "match" else "MISMATCH"))
  ok <- ok && all(live == SOURCE[[it]])
}
# distinctness: would any permutation of codes also match?
perm_hits <- 0
for (a in names(SOURCE)) for (b in names(SOURCE)) if (a != b &&
  all(as.integer(table(factor(d$resp[d$item == a], levels = 1:5))) == SOURCE[[b]])) perm_hits <- perm_hits + 1
cat(sprintf("cross-matches between different codes: %d (must be 0)\n", perm_hits))
ok <- ok && perm_hits == 0
cat("Note: this pins live code -> deposit column. The code -> wording tie rests on the\n",
    "questionnaire's printed labels; PE4 is printed but absent from every data file, so a\n",
    "drop-and-renumber cannot be excluded. Status recorded as PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
