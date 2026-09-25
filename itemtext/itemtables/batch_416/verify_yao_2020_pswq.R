# verify_yao_2020_pswq.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes pswq1..pswq16 carry the canonical PSWQ
# wording in canonical numbering (Meyer et al. 1990), with pswq1, 3, 8, 10, 11
# being the five reverse-worded ("I do not worry" / "easy to dismiss") items,
# stored RAW, on 1 = "Not at all typical of me" ... 5 = "Very typical of me".
#
# Code derivation: data/yao_2020_intolerance_uncertainty.py melts the deposit's
# own columns matching 'pswq\d+' by name, so the IRW code IS the source column
# name. The .sav has no variable or value labels (0 of 109 columns), so what is
# inferred is what the NAME means -- the instrument's printed numbering.
#
# Predictions (pass conditions):
#   P0  (plumbing) live id i == .sav row i after the 999 recode; 0 mismatches.
#   P1  (study's own key) the deposit ships reverse-scored copies PSWQ<n>new for
#       exactly n in {1,3,8,10,11} -- the canonical PSWQ reverse set -- and each
#       equals 6 - pswq<n> in every row. This is the STUDY marking which of its
#       numbered columns are reverse-worded, independent of any statistics.
#   P2  (route 6, polarity in the live data) item-rest correlation (raw items,
#       live table) is negative for exactly {1,3,8,10,11} and positive for the
#       other 11. A permutation moving any item across the polarity boundary
#       breaks this; it also shows the live table stores these items RAW.
#   P3  (option axis) every item uses all five levels 1..5 in the live data.
#
# REPORTED, NOT A PASS CONDITION: pswq10 "I never worry about anything" has the
# lowest mean of all 16 items (observed after the fact, so not pre-registered).
#
# WHAT THIS DOES NOT ESTABLISH: it pins each item's polarity CLASS (5 reverse
# vs 11 forward) but not order within a class -- e.g. a swap of pswq2 and
# pswq15, or of pswq3 and pswq8, would pass. Cross-instrument correlations with
# the GAD-7 in the same file are dominated by a general factor (gad2/gad3 both
# peak on pswq15) and do not separate forward items. Status: PARTIAL.

suppressMessages(library(irw))

TABLE <- "yao_2020_pswq"
KEY   <- "94p8m47y58"
p   <- paste0("pswq", 1:16)
REV <- c(1, 3, 8, 10, 11)

d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", p)]

meta <- jsonlite::fromJSON(sprintf("https://data.mendeley.com/public-api/datasets/%s", KEY))
f <- meta$files
url <- f$content_details$download_url[f$filename == "data upload_IU.sav"]
tf <- tempfile(fileext = ".sav")
utils::download.file(url, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(haven::zap_labels(haven::read_sav(tf)))
x[x == 999] <- NA
x$id <- seq_len(nrow(x))

ok <- TRUE

# P0
xm <- merge(w, x[, c("id", p)], by = "id", suffixes = c("", ".sav"))
mism <- sum(as.matrix(xm[, p]) != as.matrix(xm[, paste0(p, ".sav")]), na.rm = TRUE)
cat(sprintf("P0 id alignment: %d live respondents matched to .sav rows; %d cell mismatches\n\n",
            nrow(xm), mism))
ok <- ok && mism == 0 && nrow(xm) == nrow(w)

# P1
newc <- grep("^PSWQ[0-9]+new$", names(x), value = TRUE)
newn <- sort(as.integer(sub("^PSWQ([0-9]+)new$", "\\1", newc)))
cat("P1 deposit reverse-scored columns:", paste(newc, collapse = ", "), "\n")
cat("   numbers:", paste(newn, collapse = ","), " expected:", paste(REV, collapse = ","), "\n")
p1 <- identical(newn, as.integer(REV))
for (n in newn) {
  a <- x[[sprintf("PSWQ%dnew", n)]]; b <- x[[sprintf("pswq%d", n)]]
  sh <- mean(a + b == 6, na.rm = TRUE)
  cat(sprintf("   PSWQ%dnew + pswq%d == 6 in %.4f of %d rows\n", n, n, sh, sum(!is.na(a + b))))
  p1 <- p1 && sh == 1
}
cat("P1:", if (p1) "PASS" else "FAIL", "\n\n")
ok <- ok && p1

# P2
tot <- rowSums(w[, p])
ir <- sapply(p, function(v) cor(w[[v]], tot - w[[v]], use = "pairwise"))
mn <- colMeans(w[, p], na.rm = TRUE)
cat(sprintf("%-7s %6s %9s %8s\n", "item", "mean", "itemrest", "class"))
for (i in 1:16) cat(sprintf("%-7s %6.3f %9.3f %8s\n", p[i], mn[i], ir[i],
                            if (i %in% REV) "reverse" else "forward"))
neg <- which(ir < 0)
cat("P2 negative item-rest items:", paste(neg, collapse = ","),
    "| forward min item-rest:", round(min(ir[-REV]), 3),
    "| reverse max item-rest:", round(max(ir[REV]), 3), "\n")
p2 <- identical(as.integer(neg), as.integer(REV))
cat("P2:", if (p2) "PASS" else "FAIL", "\n\n")
ok <- ok && p2

# P3
lv <- tapply(d$resp, d$item, function(r) paste(sort(unique(r)), collapse = ""))
cat("P3 levels used per item:", paste(names(lv), lv, sep = "=", collapse = " "), "\n")
p3 <- all(lv == "12345")
cat("P3:", if (p3) "PASS" else "FAIL", "\n\n")
ok <- ok && p3

cat(sprintf("REPORTED: lowest-mean item = %s (%.3f); next lowest = %s (%.3f)\n\n",
            names(sort(mn))[1], sort(mn)[1], names(sort(mn))[2], sort(mn)[2]))

cat(if (ok) "VERDICT: PASS" else "VERDICT: FAIL", "\n", sep = "")
