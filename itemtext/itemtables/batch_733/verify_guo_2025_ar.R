# verify_guo_2025_ar.R -- Step 5b mapping check for guo_2025_ar (batch_733).
#
# Claim: ar_1..ar_5 are the Academic Resilience block of the CC BY 4.0 supplement
# 41598_2025_88187_MOESM1_ESM.xlsx (Guo et al. 2025, Sci Rep 15:3670), sheet 1,
# header row 3, columns 42..46, whose headers read "1.When facing ..." .. "5.I can do
# my best ...". data/guo_2025_teacher_support.py assigns the codes POSITIONALLY
# (walking the 47 item columns in legend order tes 15 / ase 22 / ar 5 / le 5), so
# the check is a re-run of that derivation: each live ar_k response vector, keyed by
# id (= the xlsx "Number" column), must equal the xlsx column at header "k." cell for
# cell, and must NOT equal any other AR column. That distinguishes every item from
# every other item, provided no two source columns are identical (printed below).

suppressMessages({library(irw); library(readxl)})
TABLE <- "guo_2025_ar"
URL <- paste0("https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-025-88187-x/",
              "MediaObjects/41598_2025_88187_MOESM1_ESM.xlsx")
CACHE <- "../../.cache/guo_2025_ar/supp.xlsx"

f <- tempfile(fileext = ".xlsx")
ok <- tryCatch({download.file(URL, f, mode = "wb", quiet = TRUE); TRUE}, error = function(e) FALSE)
if (!ok) {
  alt <- c(CACHE, "itemtext/.cache/guo_2025_ar/supp.xlsx", ".cache/guo_2025_ar/supp.xlsx")
  alt <- alt[file.exists(alt)]
  if (!length(alt)) stop("cannot fetch the supplement xlsx and no cached copy found")
  f <- alt[1]
}
raw <- suppressMessages(read_excel(f, col_names = FALSE))
hdr <- unlist(raw[3, ])
stopifnot(hdr[1] == "Number")
cols <- 42:46
cat("Source headers at columns 42..46:\n"); print(unname(hdr[cols]))
src <- data.frame(id = as.numeric(unlist(raw[-(1:3), 1])))
for (k in 1:5) src[[paste0("src_", k)]] <- as.numeric(unlist(raw[-(1:3), cols[k]]))

d <- irw::irw_fetch(TABLE)
live <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
m <- merge(src, live, by = "id")
cat(sprintf("\nrespondents: source %d, live %d, matched on id %d\n", nrow(src), nrow(live), nrow(m)))

# Agreement matrix: rows = live item, cols = source column. A correct mapping is
# 100% on the diagonal and clearly below 100% everywhere else.
A <- matrix(NA, 5, 5, dimnames = list(paste0("ar_", 1:5), paste0("src_", 1:5)))
for (i in 1:5) for (j in 1:5) A[i, j] <- mean(m[[paste0("resp.ar_", i)]] == m[[paste0("src_", j)]])
cat("\nShare of respondents agreeing (live item x source column):\n"); print(round(A, 3))
cat("\nPer-item means, live vs source column:\n")
for (k in 1:5) cat(sprintf("ar_%d  live %.4f  src %.4f\n", k,
    mean(m[[paste0("resp.ar_", k)]]), mean(m[[paste0("src_", k)]])))

diag_ok <- all(diag(A) == 1) && nrow(m) == nrow(src) && nrow(m) == nrow(live)
off <- max(A[row(A) != col(A)])
cat(sprintf("\ndiagonal all 1: %s; largest off-diagonal agreement: %.3f\n", diag_ok, off))
cat(if (diag_ok && off < 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
