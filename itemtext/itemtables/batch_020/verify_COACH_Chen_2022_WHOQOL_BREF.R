# verify_COACH_Chen_2022_WHOQOL_BREF.R
#
# WHAT IS BEING VERIFIED
#
# mapping_basis is data_labels: the deposit's own codebook keys item text to the
# exact source variable names (RA_WHOQOL_BREF_Q1..Q26) and data/COACH_Chen_2022.R
# only lowercases the header and strips the wave token, so the item_text<->item
# axis needs no statistical check.
#
# The axis that DID carry a decision is option_text<->resp for item 26. The
# codebook prints Q26's anchors as 1="Always" ... 5="Never", i.e. high resp =
# GOOD. Under that reading Q26 must correlate POSITIVELY with the other quality
# of life items and NEGATIVELY with depression severity. The shipped table
# reverses those five labels (1="Never" ... 5="Always", the canonical
# WHOQOL-BREF raw direction), which predicts the opposite signs. This script is
# the test that would break if the reversal were wrong.
#
# Data source is the study's own Harvard Dataverse raw file, not irw_fetch():
# the live table is a deterministic filter of it and this avoids the Redivis
# export quota.

suppressMessages(library(readxl))

URL <- "https://dataverse.harvard.edu/api/access/datafile/6322305"
f <- file.path(tempdir(), "coach_raw.xlsx")
if (!file.exists(f)) download.file(URL, f, quiet = TRUE, mode = "wb")
d <- suppressWarnings(as.data.frame(read_excel(f, sheet = 1)))

num <- function(x, valid) { x <- suppressWarnings(as.numeric(x)); x[!x %in% valid] <- NA; x }

waves <- c("Baseline", "Sixth_Month", "Twelfth_Month")
Q <- lapply(1:26, function(q)
    unlist(lapply(waves, function(w) num(d[[sprintf("RA_%s_WHOQOL_BREF_Q%d", w, q)]], 1:5))))
names(Q) <- paste0("q", 1:26)
QM <- do.call(cbind, Q)

# items whose polarity is not in doubt (higher = better quality of life)
POS <- setdiff(1:26, c(3, 4, 26))
rest <- function(q) rowMeans(QM[, setdiff(POS, q), drop = FALSE], na.rm = TRUE)

cat(sprintf("%-5s %6s %9s   %s\n", "item", "mean", "r(rest+)", "n"))
rr <- numeric(26)
for (q in c(1, 2, 5, 15, 19, 3, 4, 26)) {
    rr[q] <- cor(QM[, q], rest(q), use = "complete.obs")
    cat(sprintf("q%-4d %6.3f %+9.3f   %d\n", q, mean(QM[, q], na.rm = TRUE),
                rr[q], sum(!is.na(QM[, q]))))
}

# External anchor: baseline PHQ-9 and HDRS totals (both increase with depression)
tot <- function(pfx, k, valid) {
    m <- sapply(1:k, function(i) num(d[[sprintf("%s%d", pfx, i)]], valid))
    ok <- rowSums(is.na(m)) == 0
    ifelse(ok, rowSums(m), NA)
}
phq <- tot("PCP_Baseline_PHQ9_Q", 9, 0:3)
hdrs <- tot("RA_Baseline_HDRS_Q", 17, 0:4)
bl <- sapply(1:26, function(q) num(d[[sprintf("RA_Baseline_WHOQOL_BREF_Q%d", q)]], 1:5))

cat("\n", sprintf("%-5s %10s %10s\n", "item", "r(PHQ9)", "r(HDRS)"), sep = "")
ext <- matrix(NA, 26, 2)
for (q in c(1, 5, 3, 4, 26)) {
    ext[q, 1] <- cor(bl[, q], phq, use = "complete.obs")
    ext[q, 2] <- cor(bl[, q], hdrs, use = "complete.obs")
    cat(sprintf("q%-4d %+10.3f %+10.3f\n", q, ext[q, 1], ext[q, 2]))
}

ok <- rr[26] < -0.2 && rr[3] < 0 && rr[4] < 0 && rr[1] > 0.5 &&
      ext[26, 1] > 0.1 && ext[26, 2] > 0.1 && ext[1, 1] < 0

cat("\nq26 sits with q3 (pain) and q4 (medical dependence): negative against the\n",
    "positive-item rest and POSITIVE against both depression totals. That is only\n",
    "possible if high resp on q26 means MORE negative feelings, i.e. 1='Never' and\n",
    "5='Always' -- the reverse of the codebook's printed anchor order.\n", sep = "")
cat("This establishes the option_text<->resp direction for q26 (and corroborates q3/q4\n",
    "as stored raw). It does NOT establish the item_text<->item mapping, which rests on\n",
    "the codebook's variable-name keying, nor the order of the middle anchors within q26.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
