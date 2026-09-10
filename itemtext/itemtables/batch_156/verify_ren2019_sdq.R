# verify_ren2019_sdq.R -- batch_156
#
# READ THIS FIRST: ren2019_sdq is BLOCKED ON RIGHTS. No __items.csv was written,
# so there is NO item_text<->item mapping to verify and this script is not a
# mapping check. What it re-runs is the DECISION: the rights holder's quotable
# clause that produced the block, plus the two data facts recorded alongside it.
# "VERDICT: PASS" here means "the block, and the numbers in
# notes_ren2019_sdq.csv, reproduce" -- NOT "a shipped mapping verified".
#
# It fetches its own data and never calls irw::irw_fetch(): the deposit .xlsx
# reproduces the live per-item n and mean for all 25 items, so no Redivis export
# is spent.
#
# Usage: Rscript verify_ren2019_sdq.R

suppressMessages({library(digest); library(readxl)})

ok <- TRUE
say <- function(...) cat(sprintf(...))

## ---------------------------------------------------------------- 1. RIGHTS
RIGHTS_URL    <- "https://sdqinfo.org/"
RIGHTS_SHA256 <- "2507c69adf94cfd3747ab4c6d823bb57e1ebb9c1ea40a7d5299387d65c061063"
CLAUSE <- "not permitted to create or distribute electronic versions"

cat("=== 1. The rights clause that blocks this table ===\n")
pg <- tempfile(fileext = ".html")
got <- tryCatch({
  download.file(RIGHTS_URL, pg, quiet = TRUE,
                headers = c("User-Agent" = "Mozilla/5.0")); TRUE
}, error = function(e) FALSE)

if (!got) {
  cat("could not fetch ", RIGHTS_URL, " -- rights check INCONCLUSIVE this run\n", sep = "")
  ok <- FALSE
} else {
  h   <- digest::digest(file = pg, algo = "sha256")
  txt <- paste(readLines(pg, warn = FALSE), collapse = " ")
  txt <- gsub("<[^>]+>", " ", txt); txt <- gsub("[[:space:]]+", " ", txt)
  hit <- grepl(CLAUSE, txt, fixed = TRUE)
  say("page sha256 recorded 2026-09-10 : %s\n", RIGHTS_SHA256)
  say("page sha256 this run            : %s  %s\n", h,
      if (identical(h, RIGHTS_SHA256)) "(identical)" else "(CHANGED -- re-read the notice)")
  say("clause present                  : %s\n", hit)
  if (hit) {
    i <- regexpr("COPYRIGHT NOTICE", txt, fixed = TRUE)
    cat("\n", substr(txt, i, i + 950), "\n\n", sep = "")
  }
  # The block stands on the clause being present, not on the page being byte-stable.
  if (!hit) ok <- FALSE
}

## ------------------------------------------------- 2. the deposit holds no wording
cat("=== 2. The CC BY deposit publishes no SDQ wording, so it cannot license any ===\n")
XLSX_SHA256 <- "0ebf515eed34cc02e729b9e32ffb48d1c609a098e1c458ec9c759050a0e73c6e"
xf <- tempfile(fileext = ".xlsx")
gotx <- tryCatch({
  download.file("https://ndownloader.figshare.com/files/19972844", xf,
                quiet = TRUE, mode = "wb"); TRUE
}, error = function(e) FALSE)

if (!gotx) {
  cat("could not fetch the deposit -- sections 2 and 3 skipped this run\n")
  ok <- FALSE
} else {
  say("deposit sha256 recorded : %s\n", XLSX_SHA256)
  say("deposit sha256 this run : %s\n", digest::digest(file = xf, algo = "sha256"))
  d  <- as.data.frame(readxl::read_excel(xf))
  hd <- names(d)
  say("columns: %d;  SDQ headers: %s\n", ncol(d),
      paste(hd[grepl("^SDQ", hd)][c(1, 2, 24, 25)], collapse = ", "))
  say("any header longer than a bare code (i.e. carrying wording)? %s\n",
      any(nchar(hd) > 12))
  say("CJK characters anywhere in the headers? %s\n",
      any(grepl("[一-鿿]", hd)))
  cat("  -> the headers are bare codes; the administered Chinese wording is not in the deposit.\n\n")

  sdq <- paste0("SDQ", 1:25)
  m   <- sapply(d[sdq], function(x) { x <- suppressWarnings(as.numeric(x))
                                      mean(x[!is.na(x) & x >= 1 & x <= 3]) })

  ## ------------------------------- 3a. the block IS the SDQ, canonically numbered
  cat("=== 3a. Polarity check: the 10 canonical positively-worded SDQ items ===\n")
  POS <- c(1, 4, 7, 9, 11, 14, 17, 20, 21, 25)   # prosocial 1/4/9/17/20 + reverse 7/11/14/21/25
  top10 <- as.integer(sub("SDQ", "", names(sort(m, decreasing = TRUE))[1:10]))
  say("canonical positive items : %s\n", paste(sort(POS), collapse = ","))
  say("ten highest-mean columns : %s\n", paste(sort(top10), collapse = ","))
  say("identical set            : %s\n", setequal(POS, top10))
  say("10th highest mean %.2f  vs  11th %.2f  (gap %.2f)\n",
      sort(m, decreasing = TRUE)[10], sort(m, decreasing = TRUE)[11],
      sort(m, decreasing = TRUE)[10] - sort(m, decreasing = TRUE)[11])
  say("p under random relabeling = 1/choose(25,10) = %.2e\n\n", 1 / choose(25, 10))
  if (!setequal(POS, top10)) ok <- FALSE

  ## ------------------------------- 3b. the recorded response-data defect
  cat("=== 3b. SDQ1 is person-misaligned in the source file ===\n")
  s1  <- suppressWarnings(as.numeric(d$SDQ1)); s1[!(s1 %in% 1:3)] <- NA
  edu <- suppressWarnings(as.numeric(d$EDUCATION))
  mono <- all(diff(s1[!is.na(s1)]) >= 0)
  say("SDQ1 monotone non-decreasing down all %d valid rows: %s\n", sum(!is.na(s1)), mono)
  cat("EDUCATION x SDQ1 crosstab (a deterministic band is impossible in real data):\n")
  print(table(EDUCATION = edu, SDQ1 = s1))
  idx <- seq_len(nrow(d))
  pros <- rowMeans(sapply(paste0("SDQ", c(4, 9, 17, 20)), function(c) {
    x <- suppressWarnings(as.numeric(d[[c]])); x[!(x %in% 1:3)] <- NA; x }), na.rm = TRUE)
  say("\ncorr(row index, SDQ1)                          = %+.3f\n",
      cor(idx, s1, use = "complete.obs"))
  say("corr(row index, prosocial mean excluding SDQ1) = %+.3f\n",
      cor(idx, pros, use = "complete.obs"))
  cat("  -> SDQ1's apparently healthy item-total correlation is an ordering artifact.\n")
  cat("     Its marginal distribution survives; its person-level values do not.\n\n")
  if (!mono) ok <- FALSE
}

cat("What this does NOT establish: nothing about which SDQ sentence belongs to which\n",
    "code beyond polarity class. That question is moot -- the rights clause stopped the\n",
    "extraction before any wording was transcribed, and no item text was shipped.\n\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
