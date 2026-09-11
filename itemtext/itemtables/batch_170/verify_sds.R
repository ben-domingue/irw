# verify_sds.R -- Step 5b mapping check for `sds` (Symptom Distress Scale, TestGardener).
#
# CLAIM: IRW item i is column i of TestGardener 3.1.1's SDS_U matrix
# (data/TestGardener.R: `item=i` over `1:ncol(SDS_U)` -- a POSITIONAL code), and
# column i is the symptom the package authors label i: vignettes/SDS.Rmd's
# `itemVec` (passed as optList$itemLab, so column i is plotted under itemVec[i])
# and the numbered list 1-13 in Ramsay, "Better Test Scores with TestGardener",
# section 2.10. The shipped item_text is itemVec verbatim.
#
# Route A (load-bearing, code axis): live item i must equal package column i cell
# for cell, and match NO other column -- every item is distinguished from every
# other at the code level, and the code-label match to itemVec/the book list is
# positional in the source itself.
# Route B (independent corroboration from the responses, content axis):
#   B1 intensity/frequency pairs {7,8} nausea and {9,10} pain are mutual top
#      correlates; {4,5} breathing/coughing are mutual top correlates.
#   B2 the missing/illegal code 6 on "Frequency of nausea" (8) occurs only when
#      "Intensity of nausea" (7) is rated none (resp 1) or is itself missing:
#      a skip dependence that ties 8 to 7.
#   B3 book Figure 5.9 says for "Intensity of pain" the middle category "is used
#      by hardly anyone", with the two highest used by the top 25%: item 9 must
#      have fewer resp=3 than resp=4, and item 10 must not (orders 9 vs 10).
# Route B alone does not separate items 1,2,3,6,11,12,13 from one another; that
# separation is Route A's source code-label match.

suppressMessages(library(irw))

TABLE <- "sds"
LABELS <- c("Inability to sleep", "Fatigue", "Bowel symptoms", "Breathing symptoms",
            "Coughing", "Inability to concentrate", "Intensity of nausea",
            "Frequency of nausea", "Intensity of pain", "Frequency of pain",
            "Bad outlook on life", "Loss of appetite", "Poor appearance")
BOOK <- c("Inability to sleep", "Fatigue", "Bowel-related symptoms",
          "Breathing-related symptoms", "Coughing", "Inability to concentrate",
          "Intensity of nausea distress", "Frequency of nausea distress",
          "Intensity of pain", "Frequency of pain", "General outlook on life",
          "Loss of appetite", "Deterioration of appearance")

ok <- TRUE

## live data -> wide
d <- as.data.frame(irw::irw_fetch(TABLE))
W <- matrix(NA_integer_, max(d$id), 13)
W[cbind(d$id, as.integer(d$item))] <- as.integer(d$resp)

## package data
td <- file.path(tempdir(), "tg311")
dir.create(td, showWarnings = FALSE)
tgz <- file.path(td, "TestGardener_3.1.1.tar.gz")
if (!file.exists(tgz))
    download.file("https://cran.r-project.org/src/contrib/Archive/TestGardener/TestGardener_3.1.1.tar.gz",
                  tgz, quiet = TRUE, mode = "wb")
untar(tgz, files = "TestGardener/data/SDS_U.rda", exdir = td)
e <- new.env(); load(file.path(td, "TestGardener/data/SDS_U.rda"), envir = e)
U <- e$SDS_U
cat(sprintf("live wide %d x %d; SDS_U %d x %d\n", nrow(W), ncol(W), nrow(U), ncol(U)))

## Route A
cat("\nRoute A: live item i vs package column k (cells equal)\n")
M <- sapply(1:13, function(k) sapply(1:13, function(i) sum(W[, i] == U[, k], na.rm = TRUE)))
match_col <- sapply(1:13, function(i) paste(which(M[i, ] == nrow(U)), collapse = ";"))
for (i in 1:13)
    cat(sprintf("  item %2d -> column(s) %-4s | itemVec: %-26s | book #%d: %s\n",
                i, match_col[i], LABELS[i], i, BOOK[i]))
A_ok <- identical(match_col, as.character(1:13))
cat(sprintf("  identity bijection (each item matches its own column and no other): %s\n", A_ok))
ok <- ok && A_ok

## Route B
X <- W; X[X == 6] <- NA
R <- cor(X, use = "pairwise.complete.obs", method = "spearman"); diag(R) <- NA
top <- apply(R, 1, which.max)
cat("\nRoute B1: Spearman top partner per item (resp 6 = missing excluded)\n")
for (i in 1:13) cat(sprintf("  item %2d top partner %2d  r=%.2f\n", i, top[i], R[i, top[i]]))
mutual <- function(a, b) top[a] == b && top[b] == a
B1 <- mutual(7, 8) && mutual(9, 10) && mutual(4, 5)
cat(sprintf("  r(7,8)=%.2f r(9,10)=%.2f r(4,5)=%.2f; max off-diagonal r=%.2f; mutual pairs: %s\n",
            R[7, 8], R[9, 10], R[4, 5], max(R, na.rm = TRUE), B1))
ok <- ok && B1

cat("\nRoute B2: item 8 == 6 (missing) cross-tab against item 7\n")
print(table(item7 = W[, 7], item8_missing = W[, 8] == 6))
B2 <- all(W[W[, 8] == 6, 7] %in% c(1, 6))
cat(sprintf("  item-8 missing only when item 7 is 1 or 6: %s (n missing = %d)\n",
            B2, sum(W[, 8] == 6)))
cat("  (for reference) item 10 == 6 by item 9:\n")
print(table(item9 = W[, 9], item10_missing = W[, 10] == 6))
ok <- ok && B2

cat("\nRoute B3: resp=3 vs resp=4 counts, pain items\n")
c9 <- table(factor(W[, 9], 1:6)); c10 <- table(factor(W[, 10], 1:6))
cat(sprintf("  item 9  (Intensity of pain): resp1..6 = %s\n", paste(c9, collapse = "/")))
cat(sprintf("  item 10 (Frequency of pain): resp1..6 = %s\n", paste(c10, collapse = "/")))
B3 <- c9[["3"]] < c9[["4"]] && c10[["3"]] >= c10[["4"]]
cat(sprintf("  item 9 middle category < fourth, item 10 not: %s\n", B3))
ok <- ok && B3

cat("\nScope: Route B pins the pairs {4,5},{7,8},{9,10} and orders 9/10; it does not\n",
    "separate 1,2,3,6,11,12,13 from one another -- that rests on Route A's code-label\n",
    "match to the package authors' own column-ordered labels.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
