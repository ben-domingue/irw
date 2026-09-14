# verify_moe2025_erq.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST. moe2025_erq ships the canonical Gross & John (2003) ERQ
# wording against item codes ERQ1_pre .. ERQ10_pre, i.e. code ERQn carries the
# canonical ERQ item n. The deposit (figshare 30385261, a single .sav) carries NO
# variable or value labels for the ERQ columns, so the code->text tie rests on the
# canonical numbering. What makes that falsifiable is the .sav's OWN derived
# composite column `Reappraisal`: the canonical ERQ scores reappraisal from items
# {1,3,5,7,8,10} and suppression from {2,4,6,9}. If the shipped assignment of
# reappraisal vs suppression wording were wrong, that composite would not
# reproduce from the items we call reappraisal.
#
# TEST 1 -- is `Reappraisal` the mean of the six columns we labelled reappraisal,
#           and is that subset UNIQUE among all 210 six-column subsets?
# TEST 2 -- does the live IRW table's per-item distribution match the .sav column
#           of the same name, so that the subset identified in the .sav is the same
#           set of live item codes? (per-item n / resp range via the server-side
#           irw_table_sets(), plus per-item means; the table is 950 rows, so the
#           fetch is negligible against the export cap.)
#
# WHAT THIS DOES NOT ESTABLISH: order WITHIN each subscale. ERQ 1/3/7/10 are
# near-parallel wordings ("more positive"/"less negative" x "change what I'm
# thinking about"/"change the way I'm thinking about the situation") and no
# statistic in this data separates them. Hence status PARTIAL, not VERIFIED.

suppressMessages({library(irw); library(haven)})

TABLE <- "moe2025_erq"
SAV   <- "https://ndownloader.figshare.com/files/58837756"   # Moe SC ER demotivating styles.sav
REA   <- c(1, 3, 5, 7, 8, 10)   # canonical ERQ reappraisal items
SUP   <- c(2, 4, 6, 9)          # canonical ERQ suppression items

f <- tempfile(fileext = ".sav")
download.file(SAV, f, quiet = TRUE, mode = "wb")
raw <- haven::read_sav(f)
cols <- paste0("ERQ", 1:10, "_pre")
X <- as.data.frame(lapply(raw[cols], as.numeric))
cat(sprintf("source .sav: %d respondents, %d ERQ columns\n", nrow(X), ncol(X)))

## ---- TEST 1: the study's own Reappraisal composite ------------------------
R <- as.numeric(raw$Reappraisal)
subs <- combn(1:10, 6, simplify = FALSE)
dev <- sapply(subs, function(s) max(abs(R - rowMeans(X[, s, drop = FALSE]))))
o <- order(dev)
cat("\nmax |Reappraisal - rowMeans(subset)| over 95 respondents, 210 subsets of size 6:\n")
for (i in o[1:4])
  cat(sprintf("  {%-22s}  %.6f\n", paste(subs[[i]], collapse = ","), dev[i]))
shipped <- which(sapply(subs, function(s) identical(as.integer(s), as.integer(REA))))
cat(sprintf("shipped reappraisal subset {%s}: deviation %.6f  (rank %d of 210, runner-up %.6f)\n",
            paste(REA, collapse = ","), dev[shipped], which(o == shipped), dev[o[2]]))
t1 <- dev[shipped] < 1e-9 && which(o == shipped) == 1L && dev[o[2]] > 0.1

## ---- TEST 2: the live table is the same columns ---------------------------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- s$per_item
d  <- irw::irw_fetch(TABLE)
live_mean <- tapply(d$resp, d$item, mean)
cat("\nper-item, .sav column vs live item code:\n")
cat(sprintf("%-11s %5s %5s %8s %8s | %5s %5s %8s\n",
            "item", "n", "max", "mean", "sd", "n", "max", "mean"))
ok2 <- TRUE
for (i in 1:10) {
  cn <- cols[i]; v <- X[[cn]]
  p  <- pi[pi$item == cn, ]
  lm_ <- live_mean[[cn]]
  cat(sprintf("%-11s %5d %5g %8.4f %8.4f | %5d %5g %8.4f\n",
              cn, sum(!is.na(v)), max(v, na.rm = TRUE), mean(v, na.rm = TRUE), sd(v, na.rm = TRUE),
              p$n, p$resp_max, lm_))
  ok2 <- ok2 && p$n == sum(!is.na(v)) &&
         p$resp_max == max(v, na.rm = TRUE) &&
         abs(lm_ - mean(v, na.rm = TRUE)) < 1e-10
}
cat(sprintf("all 10 items reconcile (n, resp_max, mean to 1e-10): %s\n", ok2))

## ---- corroboration: polarity block means ---------------------------------
cat(sprintf("\nmean of shipped reappraisal items %.2f vs suppression items %.2f (live)\n",
            mean(live_mean[cols[REA]]), mean(live_mean[cols[SUP]])))
cat("Note: this route pins the reappraisal/suppression partition exactly and\n",
    "does NOT pin order within either subscale.\n", sep = "")

cat(if (t1 && ok2) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")
