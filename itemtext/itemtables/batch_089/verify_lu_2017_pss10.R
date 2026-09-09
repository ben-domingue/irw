# verify_lu_2017_pss10.R -- Step 5b, mapping evidence BANKED for a blocked table.
#
# STATUS: lu_2017_pss10 is BLOCKED on instrument rights (PSS family; irw#1945
# 2026-09-05, irw#1955 2026-09-06, extended to the whole PSS family 2026-09-07).
# No {table}__items.csv was written, so there is no shipped item_text mapping for
# this script to verify. What it does instead is bank the structural evidence so
# that, if the rights ruling is ever reversed, the extraction is a re-run rather
# than a restart. The verification row is recorded NO_ROUTE.
#
# WHAT IS BANKED (three falsifiable claims, none of them a re-run of the Step 5
# set checks):
#   (a) The IRW codes PSS_1..PSS_10 ARE the deposit's own column names --
#       data/lu_2017_pss10_battery.py melts SCALES["lu_2017_pss10"] =
#       ["PSS_1".."PSS_10"] BY NAME (var_name="item"), no positional step. The
#       falsifiable prediction is per-item live n == per-item count of source
#       values in 0..4 across the two deposit files, which is 1425 for nine items
#       and 1424 for PSS_5 alone (one stray -1 that the script nulls). That
#       1425/1424 fingerprint is wrong for any permutation of the ten codes --
#       it pins PSS_5 outright.
#   (b) Keying polarity (route 6). The paper states "six of which are negative
#       (items 1, 2, 3, 6, 9, and 10) while the others are positive (items 4, 5,
#       7, and 8)". The data must reproduce that split in the sign of each item's
#       correlation with the negative-block sum.
#   (c) Storage direction / published total (route 3). The paper reports the main
#       sample's SCPSS-10 score as 13.7 +/- 5.6. Only the CANONICALLY REVERSE-
#       SCORED sum of the stored values reproduces it; the raw sum does not. So
#       the live table stores RAW, unreversed values.
#
# Live side uses irw::irw_table_sets() (server-side aggregate), NOT irw_fetch(),
# so this script costs no Redivis export quota.

suppressMessages(library(irw))

TABLE <- "lu_2017_pss10"
URLS  <- c(s002 = paste0("https://journals.plos.org/plosone/article/file",
                         "?type=supplementary&id=10.1371/journal.pone.0189543.s002"),
           s001 = paste0("https://journals.plos.org/plosone/article/file",
                         "?type=supplementary&id=10.1371/journal.pone.0189543.s001"))

cache_dir <- file.path("itemtext", ".cache", TABLE)
if (!dir.exists(cache_dir)) cache_dir <- file.path(".cache", TABLE)
dir.create(cache_dir, recursive = TRUE, showWarnings = FALSE)

get_file <- function(nm) {
    p <- file.path(cache_dir, paste0(nm, ".xlsx"))
    if (!file.exists(p)) utils::download.file(URLS[[nm]], p, mode = "wb", quiet = TRUE)
    as.data.frame(readxl::read_excel(p))
}

items <- paste0("PSS_", 1:10)
main  <- get_file("s002")   # wave 1, N = 1296
rt    <- get_file("s001")   # wave 2, N = 129 (retest subsample)
stopifnot(all(items %in% names(main)), all(items %in% names(rt)))

num <- function(d) {
    x <- sapply(items, function(v) suppressWarnings(as.numeric(d[[v]])))
    x[!is.na(x) & (x < 0 | x > 4)] <- NA          # the script's own <0 rule
    as.data.frame(x)
}
m <- num(main); r <- num(rt)
both <- rbind(m, r)

## (a) per-item n, source vs live -------------------------------------------
src_n  <- colSums(!is.na(both))
s      <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi     <- as.data.frame(s$per_item)
live_n <- setNames(as.integer(pi$n), pi$item)[items]

cat(sprintf("%-8s %10s %10s %8s\n", "item", "n_source", "n_live", "match"))
for (i in items)
    cat(sprintf("%-8s %10d %10d %8s\n", i, src_n[[i]], live_n[[i]],
                ifelse(src_n[[i]] == live_n[[i]], "OK", "MISMATCH")))
n_ok <- sum(src_n == live_n)
cat(sprintf("per-item n reconciled: %d/10   (PSS_5 is the lone 1424; the others 1425)\n\n", n_ok))
cat("live resp set: ", paste(sort(as.numeric(s$resp)), collapse = ","), "\n\n", sep = "")
resp_ok <- identical(sort(as.numeric(s$resp)), c(0, 1, 2, 3, 4))

## (b) keying polarity --------------------------------------------------------
neg_items <- paste0("PSS_", c(1, 2, 3, 6, 9, 10))   # paper: negative items
pos_items <- paste0("PSS_", c(4, 5, 7, 8))          # paper: positive items
negsum <- rowSums(both[, neg_items])
cat("correlation of each item with the sum of the paper's negative block (1,2,3,6,9,10):\n")
rs <- sapply(items, function(i) cor(both[[i]], negsum, use = "complete.obs"))
for (i in items)
    cat(sprintf("  %-8s %+6.3f  %s\n", i, rs[[i]],
                ifelse(i %in% pos_items, "(paper says POSITIVE -> expect negative r)",
                                         "(paper says negative)")))
pol_ok <- all(rs[pos_items] < 0) && all(rs[neg_items] > 0)
cat(sprintf("polarity split matches the paper's stated 6/4 assignment: %s\n\n", pol_ok))

## (c) published total / storage direction ------------------------------------
raw <- rowSums(m)
rev <- raw
for (i in c(4, 5, 7, 8)) rev <- rev - m[[paste0("PSS_", i)]] + (4 - m[[paste0("PSS_", i)]])
cat(sprintf("main sample (N=%d), stored values summed RAW:              %.2f +/- %.2f\n",
            sum(!is.na(raw)), mean(raw, na.rm = TRUE), sd(raw, na.rm = TRUE)))
cat(sprintf("main sample, canonically REVERSE-SCORED (4,5,7,8):         %.2f +/- %.2f\n",
            mean(rev, na.rm = TRUE), sd(rev, na.rm = TRUE)))
cat("paper's published SCPSS-10 score for this sample:           13.70 +/- 5.60\n")
tot_ok <- abs(mean(rev, na.rm = TRUE) - 13.7) < 0.3 &&
          abs(mean(raw, na.rm = TRUE) - 13.7) > 3
cat(sprintf("reverse-scored total reproduces the paper, raw does not: %s\n\n", tot_ok))

cat("Note: this establishes the code<->source-column identity, the 0-4 anchor set,\n",
    "the polarity CLASS of each item and the raw storage direction. It does NOT\n",
    "establish any item_text mapping -- no item text was written or uploaded for\n",
    "this table, which is BLOCKED on the PSS rights ruling. Order within each\n",
    "polarity class is not distinguished by anything here.\n", sep = "")

cat(if (n_ok == 10 && resp_ok && pol_ok && tot_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
