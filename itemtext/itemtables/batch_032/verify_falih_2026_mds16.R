# verify_falih_2026_mds16.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST: IRW item code Qn carries MDS-16 item n as numbered in the
# instrument's own distribution PDF (somer.co.il/images/MD/Eng-MDS-16.pdf), so
# the shipped item_text sits on the right code.
#
# WHY THE CODES CAN BE CHECKED AT ALL: data/falih_2026_mds16.py melts the source
# columns BY NAME (MDS_ITEMS = Q1..Q16), so the IRW item code IS the column name
# in the Harvard Dataverse file -- no positional or generated assignment. This
# script therefore fetches the CC0 source file (26 KB) rather than exporting the
# live IRW table, which would burn the account-wide Redivis export quota.
#
# DOCUMENTARY EVIDENCE (stated, not re-tested): the deposit's column order is
# ... MDS16 | Q1 Q2 ... Q16 | DASS21 | DEPRESSI ... -- the sixteen MDS columns
# run consecutively in numeric order under an all-null "MDS16" section header,
# unlike the DASS block in the same file, which is reordered into subscale
# blocks. The file therefore lays the MDS out in instrument order.
#
# WHAT THIS SCRIPT TESTS, in the data:
#  (a) MUSIC PAIR. Items 1 and 16 are the only two items whose content is about
#      music, and they are content-linked to each other and to nothing else in
#      the instrument. Prediction: Q1 and Q16 are each other's single strongest
#      correlate (a mutual maximum). This pins the pair {Q1,Q16} onto those two
#      codes and could not survive a relabelling that moved either off them.
#  (b) FACTOR BLOCKS. Schimmenti, Somer & Sideli (2019), Table 1, report a
#      two-factor EFA solution: "Interference with life" loads items 5,6,7,8,9,11
#      (.75-.95) and "Somato-sensory retreat" loads items 1,2,3,4,10,15,16
#      (.62-.81); items 12,13,14 cross-load and are excluded from the test.
#      Prediction: within-block mean r exceeds between-block mean r for both
#      blocks, and each item is more correlated with its own block than the other.
#  (c) MARKER ITEM. Item 15 ("to what extent do you find it comforting and/or
#      enjoyable?") is the instrument's only positively-valenced item -- the
#      appeal of daydreaming rather than its cost. Prediction: the highest mean
#      of the sixteen. (Its association with the impairment block is reported
#      alongside as context but is NOT part of the verdict -- Q1, the music
#      trigger, is even less impairment-related, so "weakest" is not a
#      prediction the instrument supports.)
#
# WHAT IT DOES NOT ESTABLISH: the order of items WITHIN a block. Swapping the
# item_text of, say, Q5 and Q8 (both "Interference with life") leaves every
# number below unchanged, and no per-item statistic has been published for this
# Iraqi sample to break those ties. Hence PARTIAL, not VERIFIED.
#
# Known, expected exception, reported not asserted: Q10 ("how annoyed do you
# feel when the real world interrupts") sits with the impairment block in this
# sample (r 0.461) rather than with the retreat block (0.360) where Schimmenti's
# Italian sample put it, and Q4 ties at 0.359/0.359. That is a sample-level
# factor shift in a well-known cross-loading region, not a code shift; the
# blockwise test below is what carries the verdict.

TAB <- "https://dataverse.harvard.edu/api/access/datafile/13638063"
f <- tempfile(fileext = ".tab")
utils::download.file(TAB, f, quiet = TRUE)
df <- utils::read.delim(f, sep = "\t", check.names = FALSE)

items <- paste0("Q", 1:16)
d <- df[, items]
d[] <- lapply(d, function(x) { x <- suppressWarnings(as.numeric(x)); x[x < 0 | x > 10] <- NA; x })
cat(sprintf("n = %d respondents, %d items\n\n", nrow(d), ncol(d)))

C <- cor(d, use = "pairwise.complete.obs"); diag(C) <- NA

cat("=== (a) music pair: Q1 and Q16 should be each other's strongest correlate ===\n")
for (i in items)
  cat(sprintf("  %-4s strongest partner = %-4s r = %.3f\n",
              i, items[which.max(C[i, ])], max(C[i, ], na.rm = TRUE)))
ok_a <- items[which.max(C["Q1", ])] == "Q16" && items[which.max(C["Q16", ])] == "Q1"
cat(sprintf("  Q1<->Q16 mutual maximum (r = %.3f): %s\n", C["Q1", "Q16"], ok_a))

cat("\n=== (b) Schimmenti 2019 Table 1 two-factor blocks ===\n")
F1 <- paste0("Q", c(5, 6, 7, 8, 9, 11))    # Interference with life
F2 <- paste0("Q", c(1, 2, 3, 4, 10, 15, 16)) # Somato-sensory retreat
mr <- function(A, B) { m <- C[A, B, drop = FALSE]
                       if (identical(A, B)) mean(m[upper.tri(m)]) else mean(m) }
w1 <- mr(F1, F1); w2 <- mr(F2, F2); bt <- mr(F1, F2)
cat(sprintf("  within Interference-with-life   r = %.3f\n", w1))
cat(sprintf("  within Somato-sensory-retreat   r = %.3f\n", w2))
cat(sprintf("  between blocks                  r = %.3f\n", bt))
ok_b <- w1 > bt && w2 > bt
cat(sprintf("  both blocks more coherent internally than across: %s\n", ok_b))
own <- sapply(c(F1, F2), function(i) {
  o1 <- mean(C[i, setdiff(F1, i)], na.rm = TRUE)
  o2 <- mean(C[i, setdiff(F2, i)], na.rm = TRUE)
  cat(sprintf("    %-4s ownF1 %.3f  ownF2 %.3f  assigned %s\n",
              i, o1, o2, if (i %in% F1) "F1" else "F2"))
  if (i %in% F1) o1 > o2 else o2 > o1
})
cat(sprintf("  items landing in their published block: %d/%d\n", sum(own), length(own)))

cat("\n=== (c) marker item Q15 (the only positively-valenced item) ===\n")
m <- sort(colMeans(d, na.rm = TRUE), decreasing = TRUE)
for (k in names(m)) cat(sprintf("    %-4s mean = %.2f\n", k, m[k]))
ok_c <- names(m)[1] == "Q15"
q15_f1 <- mean(C["Q15", F1], na.rm = TRUE)
cat(sprintf("  Q15 has the highest mean of the sixteen: %s\n", ok_c))
cat(sprintf("  context (not gating): Q15 mean r with the impairment block = %.3f,\n", q15_f1))
cat(sprintf("    second lowest of the retreat block behind Q1 at %.3f\n",
            mean(C["Q1", F1], na.rm = TRUE)))

cat("\nNot established above: order WITHIN a block (e.g. Q5 vs Q8, Q1 vs nothing else).\n")
cat(if (ok_a && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
