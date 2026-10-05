# verify_wu_2025_drone_delivery.R -- Step 5b mapping check (route: re-run the
# processing script's positional derivation over the raw deposit).
#
# data/wu_2025_drone_delivery.py assigns Q1..Q38 POSITIONALLY to the 38
# non-composite columns of figshare 30236404 (pone.0333422.s001.xlsx), whose
# headers ARE the English item statements. The shipped item_text for Qi is the
# header of the i-th such column. This script proves the code->column tie from
# the data: for every live item Qi, the live per-respondent response vector
# (id = raw row index) must equal raw column i exactly and no other column, and
# the shipped item_text must equal that column's header verbatim. It also checks
# the live itemcov_construct against the composite header above each column.

suppressMessages({library(irw); library(readxl)})
TABLE <- "wu_2025_drone_delivery"
here <- tryCatch(dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))),
                 error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))

tmp <- tempfile(fileext = ".xlsx")
download.file("https://ndownloader.figshare.com/files/58365574", tmp, mode = "wb", quiet = TRUE)
x <- suppressMessages(read_excel(tmp))
x <- x[, !grepl("^\\.\\.\\.", names(x))]
covs <- c("Serial Number","Sexes","Age","Education attainment","Current place of residence",
          "Type of occupation","Frequency of online shopping")
cand <- setdiff(names(x), covs)
is_comp <- sapply(cand, function(c) { u <- na.omit(x[[c]]); any(u != round(u)) || length(unique(u)) > 5 })
stmts <- cand[!is_comp]
cur <- NA; construct <- character(0)
for (c in cand) { if (is_comp[[c]]) cur <- trimws(c) else construct[c] <- cur }
cat(sprintf("raw: %d rows, %d composites, %d statement columns\n", nrow(x), sum(is_comp), length(stmts)))

d <- as.data.frame(irw::irw_fetch(TABLE))
codes <- paste0("Q", 1:38)
live <- sapply(codes, function(q) { s <- d[d$item == q, ]; v <- rep(NA_real_, nrow(x)); v[s$id] <- s$resp; v })
rawm <- sapply(stmts, function(c) as.numeric(x[[c]]))

shipped <- read.csv(items_csv, stringsAsFactors = FALSE)
txt <- tapply(shipped$item_text, shipped$item, function(v) v[1])

ok <- TRUE; n_ok <- 0
cat(sprintf("%-4s %6s %6s %-10s %-5s %-5s %s\n", "item", "liveM", "rawM", "matches", "text", "cnstr", "header"))
for (i in seq_along(codes)) {
  q <- codes[i]
  hits <- which(sapply(seq_len(ncol(rawm)), function(j) identical(unname(live[, q]), unname(rawm[, j]))))
  txt_ok <- identical(txt[[q]], stmts[i])
  lc <- unique(d$itemcov_construct[d$item == q])
  c_ok <- length(lc) == 1 && trimws(lc) == construct[[stmts[i]]]
  good <- identical(hits, i) && txt_ok && c_ok
  ok <- ok && good; n_ok <- n_ok + good
  cat(sprintf("%-4s %6.3f %6.3f %-10s %-5s %-5s %s\n", q, mean(live[, q], na.rm = TRUE),
              mean(rawm[, i], na.rm = TRUE), paste(hits, collapse = ","), txt_ok, c_ok, substr(stmts[i], 1, 50)))
}
cat(sprintf("\n%d/38 live items match exactly one raw column (their own position), with matching header text and construct\n", n_ok))
cat("Does NOT establish: that the English headers are the administered (Chinese) wording --",
    "they are the study's own English rendering; the mapping itself is pinned item-by-item.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
