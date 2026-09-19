# verify_powell_2018_qcae.R -- Step 5b evidence, re-runnable.
#
# WHAT NEEDS VERIFYING. The live item codes QCAE1..QCAE31 ARE the column names of
# the study's own S1 Dataset (PLOS 10.1371/journal.pone.0194569.s005), which
# data/powell_2018_empathy.py melts unchanged (var_name="item"), so there is no
# positional or renaming step. But the deposit carries NO item wording: its S2
# variable-definitions supplement says only "QCAE# | QCAE questionnaire item # |
# Ordinal | 1-4". The shipped wording is the canonical QCAE (Reniers et al. 2011),
# keyed by that item NUMBER -- 27 of the 31 taken verbatim from the numbered SPSS
# variable labels of an independent QCAE deposit (Gomez et al. 2022, PLOS
# 10.1371/journal.pone.0261914 S2 File, e.g. QCAE15 = "15. I can easily tell if
# someone else wants to enter a conversation."), the four reverse-worded items
# 1/2/17/29 from the canonical instrument as shipped in batch_041.
#
# So the falsifiable claim is: Powell's column number n = Reniers' item number n.
# Three checks below test it, in descending strength.
#
#   (a) COMPOSITE ARITHMETIC. The deposit ships its own CE and AE totals. Summing
#       the live items under Reniers' subscale membership, reversing exactly items
#       1, 2, 17 and 29, must reproduce both totals for every respondent. This is
#       arithmetic, not statistics: it pins which 19 items are Cognitive Empathy,
#       which 12 are Affective Empathy, and which four are the reverse-worded ones.
#       It does NOT pin order within a subscale (a sum is permutation-invariant).
#   (b) KEYING POLARITY. The live table stores RAW (unreversed) responses, so the
#       reverse-worded items must correlate NEGATIVELY with the rest of their own
#       subscale. Pins item 1 as the single reverse OS item and item 11 as the
#       single forward PER item; does not order the rest.
#   (c) CROSS-STUDY MEAN PROFILE. Gomez et al.'s 27 labelled items are a level-1
#       tie of number to text in an independent sample. If Powell's numbering were
#       permuted relative to Reniers', the per-item mean profile would not line up.
#       Hard-coded below (a published deposit; it will not change).
#
# WHAT NONE OF THIS ESTABLISHES: it does not separate every item from every other
# item within a subscale. Near-tied means (e.g. items 19 vs 27 in Perspective
# Taking) leave some within-subscale permutations numerically competitive, so the
# status recorded is PARTIAL, not VERIFIED. Within-subscale identity rests on the
# item numbering itself, stated by the study's S2 supplement and matched to the
# Gomez .sav's numbered labels.

suppressMessages(library(irw))

TABLE <- "powell_2018_qcae"

PT  <- c(15, 16, 19, 20, 21, 22, 24, 25, 26, 27)   # Perspective Taking   (CE)
OS  <- c(1, 3, 4, 5, 6, 18, 28, 30, 31)            # Online Simulation    (CE)
EC  <- c(8, 9, 13, 14)                             # Emotion Contagion    (AE)
PRO <- c(7, 10, 12, 23)                            # Proximal Responsivity(AE)
PER <- c(2, 11, 17, 29)                            # Peripheral Respons.  (AE)
REV <- c(1, 2, 17, 29)
code <- function(n) paste0("QCAE", n)

# Gomez et al. (2022) PLOS ONE 10.1371/journal.pone.0261914 S2 File .sav,
# per-item means for items 1..31 (the four reverse items scored in the same
# direction as here, i.e. reverse-worded item scored high = more empathic).
GOMEZ <- c(2.9901, 2.6946, 3.2365, 3.3103, 2.9310, 3.0148, 2.7931, 2.6946,
           3.1675, 3.1429, 2.8719, 2.6897, 2.7685, 2.7882, 3.2414, 3.1281,
           2.7389, 2.9507, 3.0197, 3.3448, 3.2167, 3.3448, 3.3399, 3.2857,
           2.8670, 3.1133, 2.8325, 3.1281, 2.8818, 3.0591, 2.7833)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- as.data.frame(tapply(d$resp, list(as.character(d$id), as.character(d$item)),
                          identity))

## ---- (a) composite arithmetic ------------------------------------------------
S1 <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0194569.s005&type=supplementary"
raw <- tryCatch(read.csv(S1, stringsAsFactors = FALSE), error = function(e) NULL)

ok_a <- NA
cat("(a) Do the deposit's own CE / AE totals reproduce from the live items,\n")
cat("    under Reniers' subscale membership with items 1,2,17,29 reversed?\n")
if (is.null(raw)) {
  cat("    S1 Dataset not reachable -- check (a) skipped this run.\n\n")
} else {
  raw$id <- as.integer(raw$ID) + 100000L * as.integer(raw$Experiment)
  m <- match(rownames(w), as.character(raw$id))
  val <- function(n) { x <- w[[code(n)]]; if (n %in% REV) 5 - x else x }
  CE <- rowSums(sapply(c(PT, OS), val))
  AE <- rowSums(sapply(c(EC, PRO, PER), val))
  nCE <- sum(CE == raw$CE[m], na.rm = TRUE); nAE <- sum(AE == raw$AE[m], na.rm = TRUE)
  cat(sprintf("    CE reproduced exactly for %d of %d respondents (max |diff| %g)\n",
              nCE, nrow(w), max(abs(CE - raw$CE[m]), na.rm = TRUE)))
  cat(sprintf("    AE reproduced exactly for %d of %d respondents (max |diff| %g)\n\n",
              nAE, nrow(w), max(abs(AE - raw$AE[m]), na.rm = TRUE)))
  ok_a <- (nCE == nrow(w) && nAE == nrow(w))
}

## ---- (b) keying polarity -----------------------------------------------------
cat("(b) Item-rest correlations within each subscale (live data, stored RAW).\n")
cat("    Reverse-worded items must be the negative ones.\n")
itemrest <- function(n, grp) {
  others <- setdiff(grp, n)
  cor(w[[code(n)]], rowSums(w[, code(others), drop = FALSE]), use = "complete.obs")
}
for (nm in c("PT", "OS", "EC", "PRO", "PER")) {
  grp <- get(nm)
  cat(sprintf("    %-4s", nm))
  for (n in grp) cat(sprintf(" %s=%+.3f%s", code(n), itemrest(n, grp),
                             ifelse(n %in% REV, "*", "")))
  cat("\n")
}
r1  <- itemrest(1, OS)
r11 <- itemrest(11, PER)
cat(sprintf("    QCAE1 (only reverse OS item) r = %+.3f ; QCAE11 (only forward PER item) r = %+.3f\n",
            r1, r11))
ok_b <- (r1 < 0 && r11 < 0)   # QCAE11 is forward against a rest of three reverse items
cat("    * = canonical reverse-worded item\n\n")

## ---- (c) cross-study mean profile -------------------------------------------
cat("(c) Per-item means, this table (reverse items rescored 5-x to match) vs the\n")
cat("    independently label-tied Gomez et al. (2022) deposit:\n")
obs <- sapply(1:31, function(n) mean(if (n %in% REV) 5 - w[[code(n)]] else w[[code(n)]],
                                     na.rm = TRUE))
cat(sprintf("%-8s %8s %8s %8s\n", "item", "powell", "gomez", "diff"))
for (n in 1:31)
  cat(sprintf("%-8s %8.3f %8.3f %+8.3f\n", code(n), obs[n], GOMEZ[n], obs[n] - GOMEZ[n]))
r <- cor(obs, GOMEZ)
cat(sprintf("\n    profile correlation r = %.3f over 31 items; max |diff| = %.3f\n", r, max(abs(obs - GOMEZ))))

# How improbable is this alignment under a within-subscale permutation?
perm_rank <- function(grp) {
  o <- obs[grp]; g <- GOMEZ[grp]
  obs_cost <- sum(abs(o - g))
  idx <- seq_along(grp)
  set.seed(1)
  better <- 0; N <- 20000
  for (i in 1:N) {
    p <- sample(idx)
    if (sum(abs(o - g[p])) < obs_cost - 1e-12) better <- better + 1
  }
  c(obs_cost, better / N)
}
for (nm in c("PT", "OS", "EC", "PRO", "PER")) {
  z <- perm_rank(get(nm))
  cat(sprintf("    %-4s sum|diff| = %.3f ; share of 20000 random within-subscale permutations fitting better = %.4f\n",
              nm, z[1], z[2]))
}
ok_c <- (r > 0.85)

cat("\nNOT ESTABLISHED: within-subscale item order is not uniquely pinned -- some\n")
cat("near-tied permutations remain numerically competitive. Hence PARTIAL.\n")

pass <- isTRUE(ok_b) && isTRUE(ok_c) && (is.na(ok_a) || isTRUE(ok_a))
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
