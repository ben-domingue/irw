# verify_guo_2025_ase.R -- Step 5b mapping check for guo_2025_ase (batch_734).
#
# Claim: ase_1..ase_22 are the Academic Self-Efficacy block of the CC BY 4.0 supplement
# 41598_2025_88187_MOESM1_ESM.xlsx (Guo et al. 2025, Sci Rep 15:3670), sheet 1, header
# row 3, columns 20..41, whose headers read "1.I believe that I have the ability to
# achieve good results ..." .. "22.Even if the teacher doesn't require it ...".
# data/guo_2025_teacher_support.py assigns the codes POSITIONALLY (walking the 47 item
# columns in legend order tes 15 / ase 22 / ar 5 / le 5), so the check is a re-run of
# that derivation: each live ase_k response vector, keyed by id (= the xlsx "Number"
# column), must equal the xlsx column at header "k." cell for cell, and must NOT equal
# any other ASE column. That distinguishes every item from every other item, provided
# no two source columns are identical (largest off-diagonal agreement printed below).
# Also printed, as a content sanity check only: the four negatively worded items
# (14, 16, 17, 20) should correlate negatively / weakly with the rest (stored raw).

suppressMessages({library(irw); library(readxl)})
TABLE <- "guo_2025_ase"
URL <- paste0("https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-025-88187-x/",
              "MediaObjects/41598_2025_88187_MOESM1_ESM.xlsx")
N <- 22; cols <- 19 + (1:N)

f <- tempfile(fileext = ".xlsx")
ok <- tryCatch({download.file(URL, f, mode = "wb", quiet = TRUE); TRUE}, error = function(e) FALSE)
if (!ok) {
  alt <- c("../../.cache/guo_2025_ase/supp.xlsx", "itemtext/.cache/guo_2025_ase/supp.xlsx",
           ".cache/guo_2025_ase/supp.xlsx")
  alt <- alt[file.exists(alt)]
  if (!length(alt)) stop("cannot fetch the supplement xlsx and no cached copy found")
  f <- alt[1]
}
raw <- suppressMessages(read_excel(f, col_names = FALSE))
hdr <- unlist(raw[3, ])
stopifnot(hdr[1] == "Number")
stopifnot(all(startsWith(unname(hdr[cols]), paste0(1:N, "."))))
cat("Source headers at columns 20..41 (first 50 chars):\n")
cat(sprintf("  col %d: %s\n", cols, substr(unname(hdr[cols]), 1, 50)), sep = "")
src <- data.frame(id = as.numeric(unlist(raw[-(1:3), 1])))
for (k in 1:N) src[[paste0("src_", k)]] <- as.numeric(unlist(raw[-(1:3), cols[k]]))

d <- irw::irw_fetch(TABLE)
live <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
m <- merge(src, live, by = "id")
cat(sprintf("\nrespondents: source %d, live %d, matched on id %d\n", nrow(src), nrow(live), nrow(m)))

A <- matrix(NA, N, N, dimnames = list(paste0("ase_", 1:N), paste0("src_", 1:N)))
for (i in 1:N) for (j in 1:N) A[i, j] <- mean(m[[paste0("resp.ase_", i)]] == m[[paste0("src_", j)]])
cat("\nDiagonal agreement (live ase_k vs source column k):\n"); print(round(diag(A), 3))
off <- A; diag(off) <- NA
cat("\nLargest off-diagonal agreement per live item:\n"); print(round(apply(off, 1, max, na.rm = TRUE), 3))
cat("\nPer-item means, live vs source column:\n")
for (k in 1:N) cat(sprintf("ase_%-2d live %.4f  src %.4f\n", k,
    mean(m[[paste0("resp.ase_", k)]]), mean(m[[paste0("src_", k)]])))

L <- sapply(1:N, function(k) m[[paste0("resp.ase_", k)]])
tot <- rowSums(L)
itc <- sapply(1:N, function(k) cor(L[, k], tot - L[, k]))
cat("\nCorrected item-total r (content sanity; negatively worded 14,16,17,20 expected lowest):\n")
print(setNames(round(itc, 3), paste0("ase_", 1:N)))

diag_ok <- all(diag(A) == 1) && nrow(m) == nrow(src) && nrow(m) == nrow(live)
mx <- max(off, na.rm = TRUE)
cat(sprintf("\ndiagonal all 1: %s; largest off-diagonal agreement: %.3f\n", diag_ok, mx))
cat(if (diag_ok && mx < 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
