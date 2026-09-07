# verify_gomez_2022_qcae.R -- Step 5b evidence, re-runnable.
#
# WHAT NEEDS VERIFYING. 27 of the 31 items are tied to their text by the source
# .sav's own numbered variable labels (data_labels; PLOS s002 of
# 10.1371/journal.pone.0261914), and the IRW item code IS that .sav column name
# (data/gomez_2022_qcae.py melts QCAE_COLS unchanged). Nothing to check there.
#
# The FOUR reverse-scored columns -- QCAE1r, QCAE2r, QCAE17r, QCAE29r -- carry NO
# variable label and no value labels in the .sav. Their wording was taken from the
# canonical QCAE (Reniers et al. 2011), keyed by the item NUMBER embedded in the
# code. This script tests that keying against the data:
#
#   (a) all four are stored ALREADY REVERSE-SCORED (so the shipped anchors for
#       those four are flipped: resp 1 = "Strongly Agree");
#   (b) QCAE1r belongs to the Online Simulation block, not Peripheral
#       Responsivity -- so it must be the single reverse-worded OS item,
#       "I sometimes find it difficult to see things from the 'other guy's'
#       point of view.";
#   (c) QCAE17r is the weak, non-narrative member of the PER block, matching the
#       loading of .29 that THIS paper reports for item 17 and matching Queiros
#       et al. (2018, PLOS ONE 13(6):e0197755), who print item 17's wording by
#       number -- "It is hard for me to see why some things upset people so much"
#       -- and say items 2, 11 and 29 are the narrative (film/play/novel) ones.
#
# What it does NOT establish: QCAE2r vs QCAE29r. Both are narrative PER items
# ("I am usually objective when I watch a film or play..." vs "I usually stay
# emotionally detached when watching a film."), they behave alike in the data,
# and no published quantity is keyed to their TEXT. That assignment rests on
# documentation only (Reniers' item sourcing: items 1-6 come from the IRI, whose
# reverse Fantasy item is the "objective when I watch a film or play" one, and
# items 15-29 from the Empathy Quotient, which supplies the "emotionally
# detached when watching a film" one). Hence status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "gomez_2022_qcae"

# Reniers et al. (2011) subscale membership, in the ORIGINAL item numbering the
# .sav column names use.
PT  <- c(15, 16, 19, 20, 21, 22, 24, 25, 26, 27)
OS  <- c(1, 3, 4, 5, 6, 18, 28, 30, 31)
EC  <- c(8, 9, 13, 14)
PER <- c(2, 11, 17, 29)
PRO <- c(7, 10, 12, 23)
REV <- c(1, 2, 17, 29)                       # the four unlabelled columns
code <- function(n) paste0("QCAE", n, ifelse(n %in% REV, "r", ""))

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- as.data.frame(tapply(d$resp, list(as.character(d$id), as.character(d$item)), identity))

itemrest <- function(n, grp) {
  others <- setdiff(grp, n)
  cor(w[[code(n)]], rowSums(w[, code(others), drop = FALSE]),
      use = "complete.obs")
}

cat("(a) Are the four 'r' columns stored already reverse-scored?\n")
cat("    A reverse-WORDED item stored RAW would correlate NEGATIVELY with the\n")
cat("    rest of its own subscale. Observed item-rest correlations:\n")
grpof <- list(PT = PT, OS = OS, EC = EC, PER = PER, PRO = PRO)
rev_ok <- TRUE
for (n in REV) {
  g <- names(grpof)[sapply(grpof, function(x) n %in% x)]
  r <- itemrest(n, grpof[[g]])
  cat(sprintf("      %-8s (%s) item-rest r = %+.3f\n", code(n), g, r))
  if (r <= 0) rev_ok <- FALSE
}
cat(sprintf("    all four positive: %s -> anchors are flipped for these four\n\n", rev_ok))

cat("(b) Which block does QCAE1r sit in?\n")
r_os  <- cor(w$QCAE1r, rowSums(w[, code(setdiff(OS, 1)), drop = FALSE]), use = "complete.obs")
r_per <- cor(w$QCAE1r, rowSums(w[, code(PER), drop = FALSE]), use = "complete.obs")
cat(sprintf("      QCAE1r vs Online Simulation rest : r = %+.3f\n", r_os))
cat(sprintf("      QCAE1r vs Peripheral Responsivity: r = %+.3f\n", r_per))
b_ok <- r_os > r_per + 0.20
cat(sprintf("    OS clearly dominant: %s -> QCAE1r is the reverse-worded OS item\n\n", b_ok))

cat("(c) Which PER item is the weak, non-narrative one?\n")
cat("    Gomez et al. report a loading of .29 for item 17 (lowest in PER; .36 for\n")
cat("    item 31 in OS is the only other sub-.40 loading). Observed:\n")
per_r <- sapply(PER, itemrest, grp = PER)
names(per_r) <- code(PER)
for (i in seq_along(per_r)) cat(sprintf("      %-8s PER item-rest r = %+.3f\n", names(per_r)[i], per_r[i]))
cat("    Correlations of QCAE17r with the three narrative PER items:\n")
for (n in c(2, 11, 29))
  cat(sprintf("      QCAE17r vs %-8s r = %+.3f\n", code(n),
              cor(w$QCAE17r, w[[code(n)]], use = "complete.obs")))
r31 <- itemrest(31, OS)
cat(sprintf("    QCAE31 (the other sub-.40 loading) OS item-rest r = %+.3f; next-lowest OS item = %+.3f\n",
            r31, min(sapply(setdiff(OS, c(31, 1)), itemrest, grp = OS))))
c_ok <- (names(which.min(per_r)) == "QCAE17r") &&
        (r31 == min(sapply(setdiff(OS, 1), itemrest, grp = OS)))
cat(sprintf("    QCAE17r lowest in PER and QCAE31 lowest in OS: %s\n\n", c_ok))

cat("NOT ESTABLISHED: QCAE2r vs QCAE29r. Both narrative PER items; item-rest\n")
cat(sprintf("  r = %+.3f and %+.3f, mutual r = %+.3f -- interchangeable in the data.\n",
            per_r[["QCAE2r"]], per_r[["QCAE29r"]],
            cor(w$QCAE2r, w$QCAE29r, use = "complete.obs")))
cat("  Their assignment rests on Reniers' documented item sourcing (IRI for items\n")
cat("  1-6, Empathy Quotient for 15-29), not on anything in this data.\n\n")

cat("(d) Which way does the 1-4 scale run? (option_text <-> resp axis)\n")
cat("    The .sav value labels say 1 = Strongly Disagree ... 4 = Strongly Agree,\n")
cat("    but this paper's Methods states the opposite ('1 (strongly agree) ...\n")
cat("    4 (strongly disagree)'). Subscale totals decide it, against published\n")
cat("    norms: Cognitive Empathy (19 items) M = 57.14 (SD 8.28) in Powell (2018,\n")
cat("    n = 844) and 59.42 (9.12) in Reniers et al. (2011, women); Affective\n")
cat("    Empathy (12 items) M = 33.75 (5.51) and 36.76 (6.08).\n")
cog <- rowSums(w[, code(c(PT, OS)), drop = FALSE])
aff <- rowSums(w[, code(c(EC, PER, PRO)), drop = FALSE])
cat(sprintf("      as stored   : Cognitive M = %.2f (SD %.2f) | Affective M = %.2f (SD %.2f)\n",
            mean(cog), sd(cog), mean(aff), sd(aff)))
cat(sprintf("      if flipped  : Cognitive M = %.2f              | Affective M = %.2f\n",
            19 * 5 - mean(cog), 12 * 5 - mean(aff)))
d_ok <- abs(mean(cog) - 57.14) < abs(19 * 5 - mean(cog) - 57.14) &&
        abs(mean(aff) - 33.75) < abs(12 * 5 - mean(aff) - 33.75)
cat(sprintf("    stored direction matches the norms, flipped does not: %s\n", d_ok))
cat("    -> the .sav value labels are right and the paper's Methods sentence is\n")
cat("       an error; shipped anchors follow the .sav.\n\n")

cat(if (rev_ok && b_ok && c_ok && d_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
