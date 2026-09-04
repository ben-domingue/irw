# verify_CV_OASIS_ODSIS_PPE_Novak_2020_DSES.R
#
# WHAT IS BEING VERIFIED
# The 7 live item codes (DSES_1, DSES_10..DSES_15) are the source columns of the
# OSF deposit (osf.io/z2mgv, ex.dataset.csv / pa.dataset.csv), numbered on the
# CZECH 15-item DSES (Malinakova et al. 2018 = Underwood's 16 items minus item 5,
# which correlated .92 with item 4). Under that numbering the shipped mapping is
#   DSES_1  = Underwood 1  "I feel God's presence."
#   DSES_10 = Underwood 11 "...beauty of creation."
#   DSES_11 = Underwood 12 "...thankful for my blessings."
#   DSES_12 = Underwood 13 "...selfless caring for others."
#   DSES_13 = Underwood 14 "...accept others even when..."
#   DSES_14 = Underwood 15 "...desire to be closer to God..."
#   DSES_15 = Underwood 16 "In general, how close do you feel to God?"
# No source file carries item labels, so this is a reconstruction and it is what
# the three tests below try to break.
#
# NOT established here: the order WITHIN each block -- DSES_1 vs DSES_14, DSES_10
# vs DSES_11, DSES_12 vs DSES_13 are not separated by any test in this file. That
# is why the recorded status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "CV_OASIS_ODSIS_PPE_Novak_2020_DSES"
ok <- TRUE

## ---- Test 1: response FORMAT pins DSES_15 (live data, server-side aggregate) ----
s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
cat("-- live per-item resp levels (irw_table_sets, no export) --\n")
print(pi, row.names = FALSE)
lv <- setNames(pi$n_resp_levels, pi$item)
t1 <- lv[["DSES_15"]] == 4 && all(lv[setdiff(names(lv), "DSES_15")] == 6)
cat(sprintf("\nT1  DSES_15 has %d levels, the other 6 items have 6 -> DSES_15 is the\n",
            lv[["DSES_15"]]))
cat("    Czech version's only 4-point item, i.e. Underwood 16 'how close ... to God'.  ",
    if (t1) "PASS\n" else "FAIL\n", sep = "")
ok <- ok && t1

## ---- raw source (same rows the IRW script pivoted) ----
u <- c(ex = "https://osf.io/download/hvx57/", pa = "https://osf.io/download/teybc/")
rd <- function(url) { f <- tempfile(fileext = ".csv"); download.file(url, f, quiet = TRUE)
                      read.csv2(f, stringsAsFactors = FALSE) }
ex <- rd(u[["ex"]]); pa <- rd(u[["pa"]])
IT <- c("DSES_1", paste0("DSES_", 10:15))
d  <- rbind(ex[, IT], pa[, IT])
d  <- d[complete.cases(d), ]
d[] <- lapply(d, as.numeric)
cat(sprintf("\nraw complete cases n = %d ; live per-item n = %d (must be equal)\n",
            nrow(d), unique(pi$n)[1]))
t0 <- nrow(d) == unique(pi$n)[1]
cat("T0  raw deposit reproduces the live per-item n exactly.                        ",
    if (t0) "PASS\n" else "FAIL\n", sep = "")
ok <- ok && t0

## ---- Test 2: option_text <-> resp DIRECTION, against the study's own faith item ----
# If resp 1 were "Many times a day" (Underwood prints the anchors in descending
# order) the group means would run the other way.
fa <- ex$faith[complete.cases(ex[, IT])]
sub <- ex[complete.cases(ex[, IT]), ]
grp <- function(pat, v) mean(as.numeric(sub[[v]][grepl(pat, fa)]))
ath <- grp("convinced atheist", "DSES_1");  mem <- grp("^Yes, I am a member", "DSES_1")
ath16 <- grp("convinced atheist", "DSES_15"); mem16 <- grp("^Yes, I am a member", "DSES_15")
cat(sprintf("\nT2  DSES_1  mean: convinced atheists %.2f vs church members %.2f\n", ath, mem))
cat(sprintf("    DSES_15 mean: convinced atheists %.2f vs church members %.2f\n", ath16, mem16))
t2 <- mem > ath + 1 && mem16 > ath16 + 0.5
cat("    higher code = more frequent experience / closer to God, so resp 1 =\n")
cat("    'Never or almost never' and 1 = 'Not close' as shipped.                     ",
    if (t2) "PASS\n" else "FAIL\n", sep = "")
ok <- ok && t2

## ---- Test 3: block structure keyed to the format-pinned item ----
r <- cor(d)["DSES_15", ]
cat("\nT3  correlation of each item with the format-pinned DSES_15:\n")
for (i in IT) cat(sprintf("      %-8s %.3f\n", i, r[[i]]))
godly <- c("DSES_1", "DSES_14")   # shipped as explicit-God wording
horiz <- c("DSES_12", "DSES_13")  # shipped as wording with no religious referent
t3 <- min(r[godly]) > max(r[setdiff(IT, c(godly, "DSES_15"))]) &&
      max(r[horiz]) < min(r[c("DSES_10", "DSES_11")])
cat(sprintf("    God-explicit pair %.3f/%.3f > mixed pair %.3f/%.3f > no-referent pair %.3f/%.3f  %s",
            r[["DSES_1"]], r[["DSES_14"]], r[["DSES_11"]], r[["DSES_10"]],
            r[["DSES_12"]], r[["DSES_13"]], if (t3) "PASS\n" else "FAIL\n"))
ok <- ok && t3

## ---- Test 4: reject the off-by-one (omission after position 10) reading ----
# If the Czech version had dropped a LATER item, DSES_10 would be Underwood 10
# "I feel God's love for me through others" -- an explicit-God item, which would
# have to sit with DSES_1/DSES_14 rather than below DSES_11.
t4 <- r[["DSES_10"]] < min(r[godly]) && r[["DSES_10"]] < r[["DSES_11"]]
cat(sprintf("\nT4  DSES_10 vs DSES_15 = %.3f, below DSES_11 (%.3f) and below both\n",
            r[["DSES_10"]], r[["DSES_11"]]))
cat("    God-explicit items -> DSES_10 is not 'God's love ... through others',\n")
cat("    so the dropped item precedes position 10 (Underwood 5), as published.      ",
    if (t4) "PASS\n" else "FAIL\n", sep = "")
ok <- ok && t4

cat("\nNot established by any test above: order within {DSES_1, DSES_14},\n",
    "within {DSES_10, DSES_11}, or within {DSES_12, DSES_13}.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
