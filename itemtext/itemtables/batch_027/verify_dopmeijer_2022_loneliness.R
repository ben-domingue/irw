# verify_dopmeijer_2022_loneliness.R -- Step 5b route 9 (response-frequency matching).
#
# WHAT IS AT STAKE. The source S1 File (.sav, PLOS 10.1371/journal.pone.0267175.s001)
# codes the loneliness items 1 = "Yes! Totally agree!" ... 5 = "No! Totally disagree!"
# (its own value labels, and the paper says the same: "All items were scored from
# 1 (Yes! Totally agree) to 5 (No! Totally disagree)"). The IRW table stores the
# OPPOSITE direction, because data/dopmeijer_2022_burnout_battery.py reads the .sav
# with pandas (categorical labels) and re-maps the label STRINGS through
# MAP_LON = {"No! Totally disagree!": 1, ..., "Yes! Totally agree!": 5}.
# So the shipped option_text contradicts both the .sav codes and the paper by design,
# and that is exactly the claim that has to reproduce from the data.
#
# THE TEST. Per item x per level counts. The .sav's counts of each LABEL are compared
# against the live table's counts of each INTEGER under the shipped mapping. All 55
# cells must match exactly. A flipped direction or any permuted level breaks it at once;
# the 11 count vectors are also mutually distinct, so the same comparison simultaneously
# pins which item each Loneliness_* code is.
#
# Source counts are hard-coded from the .sav (they cannot change) -- read back with
#   pyreadstat.read_sav("...0267175.s001") ; df[col].value_counts()
# Live data is fetched.

suppressMessages(library(irw))

TABLE <- "dopmeijer_2022_loneliness"
LEVELS <- c("No! Totally disagree!", "No", "More or less", "Yes", "Yes! Totally agree!")

# Rows = Loneliness_A..K, columns = LEVELS above, i.e. counts of that label in the .sav.
SAV <- rbind(
  Loneliness_A = c(  47,  142,  516, 1102, 1334),
  Loneliness_B = c( 946, 1286,  449,  323,  137),
  Loneliness_C = c( 734, 1371,  561,  388,   87),
  Loneliness_D = c(  40,  143,  426, 1311, 1221),
  Loneliness_E = c( 798, 1451,  476,  348,   68),
  Loneliness_F = c( 689, 1360,  510,  469,  113),
  Loneliness_G = c(  81,  426,  672, 1216,  746),
  Loneliness_H = c(  50,  294,  598, 1373,  826),
  Loneliness_I = c( 767, 1478,  478,  365,   53),
  Loneliness_J = c( 913, 1494,  437,  235,   62),
  Loneliness_K = c(  34,  144,  537, 1298, 1128))
colnames(SAV) <- LEVELS

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = rownames(SAV)), factor(d$resp, levels = 1:5))

cat("shipped mapping: ", paste(sprintf("%d=%s", 1:5, LEVELS), collapse = " | "), "\n\n", sep = "")
cat(sprintf("%-14s %-22s %8s %8s %6s\n", "item", "option_text (resp)", ".sav", "live", "diff"))
bad <- 0
for (i in rownames(SAV)) for (j in 1:5) {
    s <- SAV[i, j]; l <- as.integer(live[i, j])
    if (s != l) bad <- bad + 1
    cat(sprintf("%-14s %-18s (%d) %8d %8d %6d\n", i, LEVELS[j], j, s, l, l - s))
}
cat(sprintf("\nmismatched cells: %d of 55\n", bad))

# The flipped alternative, for contrast: what the .sav's own coding would predict.
flip <- sum(abs(SAV - live[, 5:1]))
cat(sprintf("total absolute discrepancy under shipped direction: %d\n", sum(abs(SAV - live))))
cat(sprintf("total absolute discrepancy under the .sav/paper direction (reversed): %d\n", flip))

cat("Note: this pins every item AND every response level (the 11 count vectors are\n",
    "mutually distinct), but it says nothing about the WORDS -- item_text is the study's\n",
    "own English variable labels standing in for a Dutch administration, see provenance.\n", sep = "")

cat(if (bad == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
