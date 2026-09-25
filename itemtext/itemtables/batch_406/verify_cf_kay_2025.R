# verify_cf_kay_2025.R -- Step 5b re-runnable check (batch_406)
#
# CLAIM. cf_specific_1..10 are the ten 10-toss sequences in the order the study's
# Qualtrics printout lists them (1 THHTTHHHHH ... 10 THTTHTTTTT), and cf_overall_1 is
# "All 100 throws above". resp is raw (1 = Completely Random ... 7 = Completely Determined).
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("cf_")) + pivot_longer, no resp shift). The deposit columns are
# Qualtrics matrix exports cf_specific_<k>; the printout ('Qualtrics Survey (Time 1).pdf',
# OSF uzrgk au83k, block page_4) prints the sequences with EMPTY export tags "()", so the
# suffix k is Qualtrics' row id and the tie to wording is by printed order (paper_order).
#
# ROUTE. (0) deposit == live (per-item n/mean/floor/ceiling; live numbers hard-coded from
# item_stats.R, 2026-09-24) so the deposit's column names ARE the live codes. (1) the
# printout's order == shipped item_text. (2) Step 5b route 4, a parameter implied by the
# item text itself: streaky sequences (max run >= 5) should look least random. This pins
# class membership and the single run-6 sequence; it does NOT order items within the
# balanced class {4..9} or separate 1 from 10.

V  <- "view_only=aca403a5146240bda740e1e6d640751f"
dl <- function(id, f) { p <- file.path(tempdir(), f)
  if (!file.exists(p)) download.file(sprintf("https://osf.io/download/%s/?%s", id, V), p, quiet = TRUE, mode = "wb"); p }
d  <- read.csv(dl("z28r4", "kay_data.csv"))
ok <- TRUE
codes <- c(paste0("cf_specific_", 1:10), "cf_overall_1")
SEQ <- c("THHTTHHHHH","TTTTTHHTTT","HHHHHHTHHT","HTTHTTHTTT","TTTHTTHHHT",
         "HTHHTTHTHH","HHTTHTHTHH","HTHHHTTHHT","HHTTTHTHHH","THTTHTTTTT")

# (0) deposit reproduces live
LIVE <- data.frame(item = codes,
  n  = 492,
  m  = c(3.08, 3.65, 3.92, 2.90, 2.56, 2.64, 2.65, 2.58, 2.52, 3.05, 2.63),
  fl = c(31.3, 25.6, 26.8, 37.2, 38.4, 39.0, 41.3, 38.4, 39.6, 31.3, 28.9),
  ce = c(4.9, 9.1, 15.2, 5.1, 2.6, 5.3, 4.1, 2.8, 3.5, 4.9, 1.2))
cat("(0) deposit vs live\n")
dm <- setNames(numeric(11), codes)
for (k in seq_along(codes)) {
  x <- d[[codes[k]]]; x <- x[!is.na(x)]
  n <- length(x); m <- mean(x); fl <- 100 * mean(x == 1); ce <- 100 * mean(x == 7); dm[k] <- m
  cat(sprintf("  %-15s n %d/%d  mean %.4f/%.2f  floor%% %.1f/%.1f  ceil%% %.1f/%.1f\n",
              codes[k], n, LIVE$n[k], m, LIVE$m[k], fl, LIVE$fl[k], ce, LIVE$ce[k]))
  if (n != LIVE$n[k] || abs(m - LIVE$m[k]) > 0.006 || abs(fl - LIVE$fl[k]) > 0.06 || abs(ce - LIVE$ce[k]) > 0.06) ok <- FALSE
}

# (1) printout order == shipped item_text
csvp <- "itemtables/batch_406/cf_kay_2025__items.csv"
if (file.exists(csvp)) {
  sh <- unique(read.csv(csvp, stringsAsFactors = FALSE)[, c("item", "item_text")])
  shipped <- setNames(sh$item_text, sh$item)[codes]
  same <- identical(unname(shipped), c(SEQ, "All 100 throws above"))
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 11 items: %s\n", same)); if (!same) ok <- FALSE
}
if (nzchar(Sys.which("pdftotext"))) {
  txt <- trimws(system2("pdftotext", c("-raw", dl("au83k", "kay_t1.pdf"), "-"), stdout = TRUE))
  a <- grep("^cf_specific ", txt); b <- grep("^cf_overall ", txt)
  printed <- sub(" \\(\\)$", "", grep("^[HT]{10} \\(\\)$", txt[a:b], value = TRUE))
  cat("(1) printout block page_4 sequences in printed order:", paste(printed, collapse = " "), "\n")
  if (!identical(printed, SEQ)) ok <- FALSE
  ov <- grep("^All 100 throws above \\(\\)$", txt)
  cat(sprintf("    'All 100 throws above' printed under cf_overall: %s\n", length(ov) == 1 && ov > b))
  if (!(length(ov) == 1 && ov > b)) ok <- FALSE
} else { cat("pdftotext unavailable -- cannot check printed order\n"); ok <- FALSE }

# (2) route 4: streakiness implied by the shipped text vs mean "determined" rating
maxrun <- sapply(SEQ, function(s) max(rle(strsplit(s, "")[[1]])$lengths))
m10 <- dm[1:10]
cat("(2) item  sequence    maxrun  mean\n")
for (k in 1:10) cat(sprintf("    %-15s %s  %d  %.3f\n", codes[k], SEQ[k], maxrun[k], m10[k]))
top4   <- sort(names(sort(m10, decreasing = TRUE))[1:4])
streak <- sort(codes[1:10][maxrun >= 5])
rho <- cor(rank(m10), rank(maxrun))
cat(sprintf("    4 highest-mean codes: %s\n    codes with max run >= 5: %s\n", paste(top4, collapse=","), paste(streak, collapse=",")))
cat(sprintf("    highest mean: %s (%.3f); unique run-6 sequence at: %s\n", names(which.max(m10)), max(m10), codes[which(maxrun == 6)]))
cat(sprintf("    Spearman(mean, max run) = %.3f; P(top-4 set == streaky set | random code permutation) = 1/%d\n", rho, choose(10, 4)))
if (!identical(top4, streak) || names(which.max(m10)) != codes[which(maxrun == 6)]) ok <- FALSE
cat("    Lowest-streak class {4..9} means span", sprintf("%.3f-%.3f", min(m10[4:9]), max(m10[4:9])),
    "-- NOT separated by this route; nor is 1 vs 10 (both run 5).\n")

cat("Scope: (2) pins the streaky/balanced split and item 3; within-class order rests on the\n",
    "Qualtrics printed order (1), which is presentation-order inference, not an export tag.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
