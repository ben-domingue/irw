# verify_falih_2026_dass21.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST: each IRW item code carries the canonical DASS-21 item of the
# same number (Q3_A = DASS item 3, ... Q21 = DASS item 21), so the shipped
# item_text is on the right code.
#
# WHY THE CODES CAN BE CHECKED AT ALL: data/falih_2026_dass21.py melts the source
# columns by name (DASS_ITEMS list), so the IRW item code IS the column name in
# the Harvard Dataverse file -- no positional or generated assignment. This script
# therefore fetches the source file (CC0, 26 KB) rather than exporting the live
# IRW table, which would burn the account-wide Redivis export quota.
#
# THE DOCUMENTARY EVIDENCE (not re-tested here, stated for the reader): the
# deposit's own DDI metadata orders the columns under three all-null section
# header variables DEPRESSI / ANXIETY / STRESS, and the numbers falling under
# them are {3,5,10,13,16,17,21} / {2,4,7,9,15,19,20} / {1,6,8,11,12,14,18} --
# exactly the canonical DASS-21 subscale partition. A relabelling would
# reproduce that partition by chance with probability 1 / (21!/(7!)^3) = 2.5e-9.
#
# WHAT THIS SCRIPT TESTS, in the data: that the three blocks behave like the
# DASS-21 subscales they are labelled as.
#   (a) each block's within-subscale mean r exceeds that same block's mean r with
#       EACH other block (the convergent/discriminant test). Note the weaker
#       global form -- min(within) > max(between) -- does NOT hold here: Anxiety
#       within (0.370) sits below the Depression-Stress pair (0.397), which is
#       the DASS's well-known general-distress factor, not a mapping defect.
#   (b) subscale means order Stress > Depression > Anxiety, the standard
#       non-clinical DASS-21 profile
#   (c) marker item: DASS-21 item 17 ("I felt I wasn't worth much as a person")
#       is the least endorsed depression item in a working, non-clinical sample
#
# WHAT IT DOES NOT ESTABLISH: order WITHIN a subscale. Swapping the text of, say,
# Q3_A and Q5_A (both depression) would leave every number below unchanged. That
# is why the mapping_verification row is PARTIAL, not VERIFIED.

TAB <- "https://dataverse.harvard.edu/api/access/datafile/13638063"
f <- tempfile(fileext = ".tab")
utils::download.file(TAB, f, quiet = TRUE)
df <- utils::read.delim(f, sep = "\t", check.names = FALSE)

items <- c(paste0("Q", 1:16, "_A"), paste0("Q", 17:21))
num   <- c(1:16, 17:21)
d <- df[, items]
d[] <- lapply(d, function(x) { x <- suppressWarnings(as.numeric(x)); x[x < 0 | x > 3] <- NA; x })

sub <- list(Depression = c(3,5,10,13,16,17,21),
            Anxiety    = c(2,4,7,9,15,19,20),
            Stress     = c(1,6,8,11,12,14,18))
code <- setNames(items, num)

C <- cor(d, use = "pairwise.complete.obs")
mr <- function(a, b) {
  A <- code[as.character(a)]; B <- code[as.character(b)]
  m <- C[A, B, drop = FALSE]
  if (identical(A, B)) mean(m[upper.tri(m)]) else mean(m)
}

cat("=== (a) within- vs between-subscale mean correlation ===\n")
wi <- sapply(names(sub), function(k) mr(sub[[k]], sub[[k]]))
bt <- combn(names(sub), 2, function(p) mr(sub[[p[1]]], sub[[p[2]]]))
btn <- combn(names(sub), 2, function(p) paste(p, collapse = "-"))
for (k in names(wi)) cat(sprintf("  within  %-11s r = %.3f\n", k, wi[k]))
for (i in seq_along(bt)) cat(sprintf("  between %-11s r = %.3f\n", btn[i], bt[i]))
ok_a <- all(sapply(names(sub), function(k) {
  others <- setdiff(names(sub), k)
  all(wi[k] > sapply(others, function(o) mr(sub[[k]], sub[[o]])))
}))
cat(sprintf("  every block more coherent internally than with either other: %s\n", ok_a))
cat(sprintf("  (global min-within %.3f vs max-between %.3f -- general factor, not tested)\n",
            min(wi), max(bt)))

cat("\n=== (b) subscale mean levels (expect Stress > Depression > Anxiety) ===\n")
sm <- sapply(sub, function(v) mean(as.matrix(d[, code[as.character(v)]]), na.rm = TRUE))
for (k in names(sm)) cat(sprintf("  %-11s mean = %.3f\n", k, sm[k]))
ok_b <- sm["Stress"] > sm["Depression"] && sm["Depression"] > sm["Anxiety"]
cat(sprintf("  ordering holds: %s\n", ok_b))

cat("\n=== (c) marker item: DASS-21 item 17 lowest of the depression block ===\n")
dep <- code[as.character(sub$Depression)]
im <- sort(colMeans(d[, dep], na.rm = TRUE))
for (k in names(im)) cat(sprintf("  %-6s mean = %.3f\n", k, im[k]))
ok_c <- names(im)[1] == "Q17"
cat(sprintf("  lowest depression item is Q17: %s\n", ok_c))

cat("\nNot established by any of the above: the order of items WITHIN a subscale.\n")
cat(if (ok_a && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
