# verify_tran_2023_gad7.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes GAD1..GAD7 carry the canonical GAD-7
# items in canonical numbering (GAD1 = "Feeling nervous, anxious or on edge" ...
# GAD7 = "Feeling afraid as if something awful might happen"), and resp 0..3 =
# Not at all .. Nearly every day.
#
# Nothing in the study ties those codes to text. data/tran_2023_gi_mental_battery.py
# melts the S1 Data workbook's own columns GAD1..GAD7 by name (the item code IS
# the source column name -- no positional step), but the workbook
# (doi:10.1371/journal.pone.0289123.s002, one sheet "Analyse") has a bare header
# row, no label row, no codebook and no non-ASCII text anywhere, and the paper
# prints no item. So the tie rests on the authors having numbered the columns
# in the GAD-7 form's own printed order; that has to be tested against content.
#
# ITEM AXIS -- two structural predictions from GAD-7 content:
#
#   P1  {GAD1, GAD2, GAD3} (nervous / can't stop worrying / worrying too much)
#       is the most intercorrelated of all 35 item triads. Chance under a random
#       relabelling: 1/35 = 2.9%. The prediction was checked first on the three
#       IRW GAD-7 tables whose codes are tied to wording by the source file's own
#       labels (mapping_basis=data_labels): triad {1,2,3} ranks 1st of 35 in
#       ali_2021_gad7 (0.563) and pranckeviciene_2022_gad7 (0.759), and 2nd in
#       shu_2024_gad7 (0.707, behind {2,3,4} 0.737).
#   P2  GAD6 (irritability, the one item outside the worry/tension content) has
#       the lowest mean inter-item correlation. Chance: 1/7. Weaker prior than
#       P1: it holds in rosetti_2023_gad7 and near-holds in pranckeviciene (0.526
#       vs GAD7 0.521) and shu (0.611 vs 0.613), but not in ali_2021_gad7.
#   Joint chance of P1 and P2 under a random relabelling: 1/35 * 1/4 = 0.71%.
#
# OPTION AXIS (option_text <-> resp):
#   P3  the deposit's own totalGAD7 equals the raw UNREVERSED sum of GAD1..GAD7
#       for every respondent, its GAD flag equals totalGAD7 >= 10 for every
#       respondent, and that raw coding reproduces the paper's reported GAD
#       prevalence of 6.8% ("A score of 10 or greater on GAD-7 was considered the
#       presence of generalized anxiety disorder"; "The prevalences of GAD and
#       MDD were 6.8% and 10.2%"). A flipped 0-3 coding cannot reproduce it.
#
# WHAT THIS DOES NOT ESTABLISH: P1 pins {GAD1,GAD2,GAD3} as a SET against
# {GAD4..GAD7} but not the order within it; P2 pins GAD6 within the second block;
# GAD4, GAD5 and GAD7 are not distinguished from one another. A permutation
# within {1,2,3} or within {4,5,7} would survive. Status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE   <- "tran_2023_gad7"
DEPOSIT <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0289123.s002"
gad <- paste0("GAD", 1:7)
PUB_PREV <- 6.8

# --- live IRW data ----------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- tapply(d$resp, list(d$id, d$item), function(x) x[1])[, gad]
r <- cor(w, use = "pairwise.complete.obs")
mir <- (colSums(r) - 1) / 6

cat("Live per-item mean / mean inter-item r (n =", nrow(w), "respondents)\n")
for (i in gad) cat(sprintf("  %-5s mean %.3f   mean r %.3f\n", i, mean(w[, i], na.rm = TRUE), mir[i]))

# --- P1 ---------------------------------------------------------------------
tri <- combn(7, 3)
tm  <- apply(tri, 2, function(k) mean(r[k, k][upper.tri(diag(3))]))
o   <- order(-tm)
rank123 <- which(apply(tri[, o, drop = FALSE], 2, function(k) all(k == 1:3)))
cat("\nP1  top triads by mean intercorrelation:\n")
for (j in o[1:4]) cat(sprintf("      {%s}  %.3f\n", paste(gad[tri[, j]], collapse = ","), tm[j]))
cat(sprintf("    triad {GAD1,GAD2,GAD3} ranks %d of %d\n", rank123, ncol(tri)))

# --- P2 ---------------------------------------------------------------------
srt <- sort(mir)
cat(sprintf("P2  lowest mean inter-item r: %s %.3f (next lowest %s %.3f)\n",
            names(srt)[1], srt[1], names(srt)[2], srt[2]))

# --- P3: option axis, from the deposit --------------------------------------
tf <- tempfile(fileext = ".xlsx")
utils::download.file(DEPOSIT, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(suppressMessages(readxl::read_excel(tf, sheet = "Analyse")))
x <- x[!is.na(x$STT), ]
raw <- rowSums(x[, gad])
dd  <- max(abs(raw - x$totalGAD7))
flag_ok <- sum((x$totalGAD7 >= 10) == (x$GAD == 1))
prev_raw  <- 100 * mean(raw >= 10)
prev_flip <- 100 * mean((21 - raw) >= 10)
cat(sprintf("P3  deposit totalGAD7 vs raw sum of GAD1..GAD7: max |diff| = %g (n = %d)\n", dd, nrow(x)))
cat(sprintf("    deposit GAD flag == (totalGAD7 >= 10) for %d of %d respondents\n", flag_ok, nrow(x)))
cat(sprintf("    prevalence of total >= 10: raw coding %.2f%%, flipped coding %.2f%%; paper reports %.1f%%\n",
            prev_raw, prev_flip, PUB_PREV))

ok <- c(P1 = rank123 == 1,
        P2 = names(srt)[1] == "GAD6",
        P3 = dd == 0 && flag_ok == nrow(x) && round(prev_raw, 1) == PUB_PREV &&
             abs(prev_flip - PUB_PREV) > 50)
cat("\n"); for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins {GAD1,GAD2,GAD3} as a set, GAD6 within {GAD4..GAD7}, and the 0-3\n",
    "direction. Does NOT order GAD1/GAD2/GAD3 or GAD4/GAD5/GAD7 -- status PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
