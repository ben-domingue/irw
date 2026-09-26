# verify_trusz_2025_nfi.R -- Step 5b mapping check for trusz_2025_nfi (batch_446).
#
# Claim: live item i<k> is appendix item k of the NFI-72 (Appendix1_ENI72&ENI30_after rev.docx,
# first table, rows numbered 1..72), and resp 1..5 = definitely not .. definitely yes.
#
# Chain tested here, all against the study's own deposit (doi:10.7910/DVN/DWCBOE, file
# EFA_NFI72_N660.sav, id 13673103, the file data/trusz_2025_nfi.py reads):
#   (1) live i<k> == .sav column i<k> for every (id, item) -- per-item n and mean identical;
#   (2) .sav i<k> is a deterministic recode of the raw answer column "@<k>.<Polish item text>"
#       (paper codes 1,2,3,4,5 -> 1,2,4,5,3; text labels Zdecydowanie nie..Zdecydowanie tak -> 1..5),
#       and matches @k far better than any other @j -- this distinguishes every item from every other;
#   (3) the @k column name is numbered k and carries item k's Polish wording (read by hand 72/72
#       against the English appendix row k; printed below for a spot sample);
#   (4) resp axis: the text-labelled respondents' Polish labels map 1:1 onto live 1..5 in the
#       shipped order (route 9).
suppressMessages({library(irw); library(haven)})

TABLE <- "trusz_2025_nfi"
f <- file.path(tempdir(), "EFA_NFI72_N660.sav")
if (!file.exists(f))
  download.file("https://dataverse.harvard.edu/api/access/datafile/13673103", f, mode = "wb", quiet = TRUE)
s <- as.data.frame(read_sav(f))
at <- grep("^@", names(s), value = TRUE)
stopifnot(length(at) == 72)
num <- as.integer(sub("^@([0-9]+)\\..*", "\\1", at))
stopifnot(identical(num, 1:72))

recode <- function(x) {
  x <- tolower(trimws(as.character(x)))
  map <- c("1" = 1, "2" = 2, "3" = 4, "4" = 5, "5" = 3,
           "zdecydowanie nie" = 1, "raczej nie" = 2, "nie mam zdania" = 3,
           "raczej tak" = 4, "zdecydowanie tak" = 5)
  unname(map[x])
}
R <- sapply(at, function(a) recode(s[[a]]))
I <- sapply(1:72, function(k) as.numeric(s[[paste0("i", k)]]))

# (2) agreement matrix: rows = i_k, cols = @j
agree <- function(k, j) { ok <- !is.na(R[, j]) & !is.na(I[, k]); mean(R[ok, j] == I[ok, k]) }
diag_ag <- sapply(1:72, function(k) agree(k, k))
off_best <- sapply(1:72, function(k) max(sapply(setdiff(1:72, k), function(j) agree(k, j))))
cat(sprintf("(2) i_k vs recode(@k): diagonal agreement min %.4f median %.4f; best off-diagonal max %.3f median %.3f\n",
            min(diag_ag), median(diag_ag), max(off_best), median(off_best)))
cat(sprintf("    items whose own @k beats every other @j by >= 0.25: %d/72\n", sum(diag_ag - off_best >= 0.25)))

# (1) live vs .sav i_k
d <- irw::irw_fetch(TABLE)
live_n <- tapply(d$resp, d$item, length); live_m <- tapply(d$resp, d$item, mean)
# data/trusz_2025_nfi.py casts resp with astype(int), truncating the .sav's six half-point cells
half <- sum(!is.na(I) & I != round(I))
cat(sprintf("    .sav i_k half-point cells (truncated by the processing script): %d\n", half))
I <- trunc(I)
sav_n <- colSums(!is.na(I) & I >= 1 & I <= 5); sav_m <- sapply(1:72, function(k) { x <- I[, k]; mean(x[!is.na(x) & x >= 1 & x <= 5]) })
names(sav_n) <- names(sav_m) <- paste0("i", 1:72)
dn <- max(abs(live_n[names(sav_n)] - sav_n)); dm <- max(abs(live_m[names(sav_m)] - sav_m))
cat(sprintf("(1) live vs .sav i_k: max |n diff| = %d, max |mean diff| = %.2e over 72 items\n", dn, dm))
id_ok <- all(sort(unique(d$id)) %in% s$lp)
x <- merge(d, data.frame(id = rep(s$lp, 72), item = rep(paste0("i", 1:72), each = nrow(s)), sresp = as.vector(I)), by = c("id", "item"))
n_eq <- sum(x$resp == x$sresp, na.rm = TRUE)
cat(sprintf("    row-aligned on id=lp: %d/%d live rows equal the (truncated) .sav value\n", n_eq, nrow(d)))

# (3) spot sample of name <-> shipped text
fa <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
here <- if (length(fa)) dirname(normalizePath(fa)) else "itemtables/batch_446"
it <- read.csv(file.path(here, "trusz_2025_nfi__items.csv"), stringsAsFactors = FALSE)
for (k in c(1, 24, 46, 54, 70)) cat(sprintf("(3) %-55s | %s\n", at[k], unique(it$item_text[it$item == paste0("i", k)])))

# (4) resp axis, text-labelled cells only
lab <- tolower(trimws(unlist(lapply(at, function(a) as.character(s[[a]])))))
ii <- as.vector(I)
keep <- lab %in% c("zdecydowanie nie", "raczej nie", "nie mam zdania", "raczej tak", "zdecydowanie tak") & !is.na(ii)
tab <- table(lab[keep], ii[keep]); print(tab)
offdiag <- sum(tab) - sum(sapply(rownames(tab), function(r) tab[r, as.character(recode(r))]))
cat(sprintf("(4) text-labelled cells: %d, off-mapping cells: %d\n", sum(tab), offdiag))

# polarity sanity: reverse-worded item 54 ("are rarely related to physical activity") vs HEA items
hea <- c(16, 28, 41, 61, 63, 70)
cat(sprintf("    r(i54, HEA physical items %s) = %s\n", paste(hea, collapse = ","),
            paste(sprintf("%.2f", cor(I[, 54], I[, hea], use = "pairwise")), collapse = " ")))

pass <- min(diag_ag) >= 0.99 && sum(diag_ag - off_best >= 0.25) == 72 && dn == 0 && dm < 1e-9 && n_eq == nrow(d) && offdiag == 0
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
