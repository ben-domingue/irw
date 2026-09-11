# verify_tan_2026_stem_technology_integration.R
#
# Claim: item_01..item_15 are the 15 digit-led columns of the figshare deposit's
# "Form Responses 1" sheet (belief,attitude and practice.xlsx, file 63759105), in
# column order, and each code's item_text is that column's header with its leading
# "N." numbering stripped.
#
# The processing script assigns codes POSITIONALLY (enumerate over columns whose
# name starts with a digit) and assigns id = sheet row index + 1. So the check is:
#   (A) header diff: the k-th digit-led header carries the number k, and its text
#       (numbering stripped) equals the shipped item_text for item_k, verbatim;
#   (B) per-respondent join: live resp for (id, item_k) equals the xlsx value in
#       row id, column k, for all 80 respondents -- and does NOT equal any other
#       column j != k at 100%, so the route separates every item from every other.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "tan_2026_stem_technology_integration"
URL   <- "https://ndownloader.figshare.com/files/63759105"

here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) NULL)
if (is.null(here)) {
  a <- commandArgs(trailingOnly = FALSE)
  f <- sub("^--file=", "", a[grep("^--file=", a)])
  here <- if (length(f)) dirname(normalizePath(f)) else "."
}
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))

tmp <- tempfile(fileext = ".xlsx")
download.file(URL, tmp, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "irw-itemtext-verify/1.0"))
x <- as.data.frame(read_excel(tmp, sheet = "Form Responses 1"))
hdr <- names(x)[grepl("^[0-9]", names(x))]
cat("digit-led columns in xlsx:", length(hdr), "\n\n")

shipped <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
shipped <- unique(shipped[, c("item", "item_text")])

ok <- TRUE

# (A) header diff
cat("(A) header diff\n")
nA <- 0
for (k in seq_along(hdr)) {
  num  <- as.integer(sub("^([0-9]+)\\..*$", "\\1", hdr[k]))
  txt  <- sub("^[0-9]+\\.\\s*", "", hdr[k])
  code <- sprintf("item_%02d", k)
  st   <- shipped$item_text[shipped$item == code]
  m    <- length(st) == 1 && identical(st, txt) && num == k
  nA   <- nA + m
  cat(sprintf("  %s <- col %2d header no. %2d : %s\n", code, k, num, if (m) "MATCH" else "MISMATCH"))
}
cat(sprintf("  %d/%d verbatim\n\n", nA, length(hdr)))
if (nA != length(hdr) || length(hdr) != 15) ok <- FALSE

# (B) per-respondent join
live <- irw::irw_fetch(TABLE)
x$id <- seq_len(nrow(x))
cat("(B) per-respondent agreement, % of 80 respondents: live item_k (rows) vs xlsx column j (cols)\n")
M <- matrix(NA_real_, 15, 15, dimnames = list(sprintf("item_%02d", 1:15), paste0("c", 1:15)))
for (k in 1:15) {
  lk <- live[live$item == sprintf("item_%02d", k), c("id", "resp")]
  mm <- merge(lk, x[, c("id", hdr)], by = "id")
  for (j in 1:15) M[k, j] <- 100 * mean(mm$resp == mm[[hdr[j]]])
  if (nrow(mm) != 80) { cat("  join size", nrow(mm), "for item", k, "\n"); ok <- FALSE }
}
options(width = 200, max.print = 10000)
print(round(M, 1))
diag_v <- diag(M)
off    <- M; diag(off) <- NA
cat(sprintf("\n  diagonal: min %.1f%%  | off-diagonal: max %.1f%% (%s)\n",
            min(diag_v), max(off, na.rm = TRUE),
            paste(which(off == max(off, na.rm = TRUE), arr.ind = TRUE)[1, ], collapse = ",")))
if (any(diag_v < 100) || max(off, na.rm = TRUE) >= 100) ok <- FALSE
for (k in 1:15) if (which.max(M[k, ]) != k) ok <- FALSE

# Context only (not part of the verdict): keying of the two negatively worded items.
w <- reshape(as.data.frame(live)[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
others <- sprintf("item_%02d", setdiff(1:15, 9:10))
r9  <- sapply(others, function(o) cor(w$item_09, w[[o]]))
r10 <- sapply(others, function(o) cor(w$item_10, w[[o]]))
cat(sprintf("\ncontext: item_09 r with other 13 items %.2f..%.2f; item_10 %.2f..%.2f; r(09,10) = %.2f\n",
            min(r9), max(r9), min(r10), max(r10), cor(w$item_09, w$item_10)))

cat("\nWhat this does NOT establish: the response anchors or their direction. The Google\n",
    "Forms export stores bare 1-5 with no labels, so option_text is blank. Nor does it settle\n",
    "whether negatively worded items 9-10 were reverse-keyed: they correlate positively with\n",
    "the other 13 items (printed above) and the deposit gives no keying information.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
