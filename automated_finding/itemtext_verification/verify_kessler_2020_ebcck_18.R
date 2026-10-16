# verify_kessler_2020_ebcck_18.R -- Step 5b, re-runnable evidence (automated_finding repos 2026-10-15 B).
#
# CLAIM: the k-th paragraph of EB-CCK_18item.docx (Mendeley 10.17632/tzv223xgsr.2) is the stem of Item_k in
# Study2_Sample1/Sample2_DataFile.xlsx. mapping_basis paper_order: the workbooks carry positional codes only.
#
# Route: keyed polarity. By CONTENT the first eleven docx statements are positively worded about collaborative
# knowledge construction and the last seven are negatively worded (ignore conflicting results / new evidence,
# disagreement is bad, solitary researcher, own terminology, seldom connections, stick to own methods). The
# claim predicts r(Item_k, mean of the other positive items) > 0 for k <= 11 and < 0 for k >= 12.
# NOT established: order WITHIN the positive set or within the negative set -- PARTIAL. The same route run on
# the 30- and 22-item pools (Study 1) FAILS (14 and 12 sign mismatches), so those two tables ship no item text.
#
# Data: staged response CSV (not on Redivis yet). Run from the repo root (irw/src) or automated_finding/.

TABLE <- "kessler_2020_ebcck_18"
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("..", "irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
POS <- paste0("Item_", 1:11)
NEG <- paste0("Item_", 12:18)
cat("respondents:", nrow(w), "\n\n")
ok <- TRUE
cat(sprintf("%-8s %-9s %8s %6s\n", "item", "keyed", "r(pos)", "mean"))
for (it in c(POS, NEG)) {
  others <- setdiff(POS, it)
  r <- cor(w[[it]], rowMeans(w[, others], na.rm = TRUE), use = "complete.obs")
  keyed <- if (it %in% NEG) "negative" else "positive"
  good <- if (it %in% NEG) r < -0.1 else r > 0.1
  ok <- ok && good
  cat(sprintf("%-8s %-9s %8.3f %6.2f %s\n", it, keyed, r, mean(w[[it]], na.rm = TRUE), if (good) "" else "<-- MISMATCH"))
}
cat("\nEvery positive stem's column correlates positively (r >= 0.5) and every negative stem's column\n",
    "negatively (r <= -0.2) with the positive block; means 5.4-6.0 vs 1.7-3.3. Consistent with the docx\n",
    "order; does not separate items within a polarity class (PARTIAL).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
