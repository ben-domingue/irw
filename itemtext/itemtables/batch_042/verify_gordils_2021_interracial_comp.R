# verify_gordils_2021_interracial_comp.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order):
#   live item COMPk  ==  S1/S4 Data spreadsheet column COMPk  ==  the k-th item of
#   the "Perceived Racial Competition" block of S1 Appendix (10.1371/journal.pone.0245671.s001).
#
# Two independent checks, neither of which re-checks item counts or set membership
# (validate_items.R already did that):
#
#  (A) PER-ITEM n FINGERPRINT -- ties each live item code to a specific spreadsheet
#      column. The processing script drops Study 2's COMP2 column (a spreadsheet
#      artifact identical to the composite mean) and drops non-numeric cells, so the
#      five items end up with five DISTINCT row counts. Re-running that filter over
#      the two raw PLOS xlsx files must reproduce each live count exactly. A permuted
#      code->column assignment breaks this immediately.
#
#  (B) CONTENT-PREDICTED CORRELATION STRUCTURE -- ties the columns to the appendix
#      wording. Appendix items 2 and 4 are near-paraphrases of one another ("it seems
#      that Blacks and Whites are competing with each other" / "it seems that Blacks
#      are competing with Whites and Whites are competing with Blacks"), and item 5 is
#      the only one about being COMPARED rather than competing. Prediction: in Study 1
#      (the only sample where all five columns are genuine) COMP2-COMP4 is the single
#      largest off-diagonal correlation, and COMP5 carries the smallest mean
#      correlation with the rest.
#
# WHAT THIS DOES NOT ESTABLISH: check (B) pins the {2,4} pair as a pair and pins 5,
# but it does not separate COMP2 from COMP4, and it says nothing about COMP1 vs COMP3
# (both are "value/importance of competition" phrasings). Those two positions rest on
# appendix presentation order alone. Hence status PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "gordils_2021_interracial_comp"
COLS  <- paste0("COMP", 1:5)
URLS  <- c(S1 = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0245671.s004",
           S2 = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0245671.s007")

## ---- live per-item n, server-side aggregate (no export) -------------------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(as.numeric(pi$n), pi$item)[COLS]

## ---- reproduce it from the raw spreadsheets -------------------------------
grab <- function(u) {
    f <- tempfile(fileext = ".xlsx")
    utils::download.file(u, f, quiet = TRUE, mode = "wb")
    as.data.frame(readxl::read_excel(f, sheet = "Sheet1"))
}
num <- function(x) suppressWarnings(as.numeric(as.character(x)))

d1 <- grab(URLS[["S1"]]); d2 <- grab(URLS[["S2"]])
d1 <- d1[which(num(d1$AttentionCheck) == 2), ]
d2 <- d2[which(num(d2$AttentionCheck) == 2), ]
d2$COMP2 <- NA                       # dropped by data/gordils_2021_interracial.py

ok_resp <- function(v) { v <- num(v); !is.na(v) & v >= 1 & v <= 7 }
raw_n <- sapply(COLS, function(cc) sum(ok_resp(d1[[cc]])) + sum(ok_resp(d2[[cc]])))

cat("(A) per-item n: live (irw_table_sets) vs re-derived from S1/S4 Data\n")
cat(sprintf("%-7s %10s %10s %7s\n", "item", "live", "raw", "diff"))
for (cc in COLS)
    cat(sprintf("%-7s %10d %10d %7d\n", cc, as.integer(live_n[[cc]]),
                as.integer(raw_n[[cc]]), as.integer(raw_n[[cc]] - live_n[[cc]])))
a_ok <- all(raw_n == live_n)
cat(sprintf("counts distinct across items: %s (%s)\n",
            length(unique(raw_n)) == 5L, paste(raw_n, collapse = ", ")))
a_ok <- a_ok && length(unique(raw_n)) == 5L

## ---- (B) content-predicted correlation structure, Study 1 only ------------
x <- as.data.frame(lapply(d1[COLS], function(v) { v <- num(v); v[v < 1 | v > 7] <- NA; v }))
R <- cor(x, use = "pairwise.complete.obs")
cat("\n(B) Study 1 correlation matrix (COMP2 is corrupt in Study 2, so Study 1 only)\n")
print(round(R, 3))
off <- R; diag(off) <- NA
top <- which(off == max(off, na.rm = TRUE), arr.ind = TRUE)[1, ]
pair <- paste(sort(c(rownames(R)[top[1]], colnames(R)[top[2]])), collapse = "-")
mrow <- sort(rowMeans(off, na.rm = TRUE))
cat(sprintf("largest off-diagonal pair: %s (r = %.3f); predicted COMP2-COMP4\n",
            pair, max(off, na.rm = TRUE)))
cat(sprintf("weakest mean correlation with the rest: %s (%.3f); predicted COMP5\n",
            names(mrow)[1], mrow[1]))
b_ok <- identical(pair, "COMP2-COMP4") && identical(names(mrow)[1], "COMP5")

cat("\nNote: (B) does not separate COMP2 from COMP4, nor COMP1 from COMP3;\n",
    "those two positions rest on S1 Appendix presentation order alone.\n", sep = "")
cat(if (a_ok && b_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
