# verify_gesbert_2021_tdeq.R
#
# CLAIM UNDER TEST: item code Q<i> in the IRW table carries the wording printed
# as item <i> in S1 Appendix of Gesbert et al. (2021), PLoS ONE 16(2):e0246823.
#
# The falsifiable prediction: the paper's Table 5 ("TDEQ-FV item analysis for
# each age-group") publishes M (SD) for 24 of the 25 items in FOUR age groups,
# keyed by ENGLISH ITEM TEXT (not by number).  So Table 5 gives text -> a
# 4-number profile; S1 Appendix gives text -> item number; the data give column
# -> a 4-number profile.  If the shipped item_text were permuted, the profiles
# would land on the wrong columns.
#
# Two stages, because the live IRW table drops the age-group covariate:
#   (1) tie live item code -> S1 Data column, from live per-item n and mean
#       (mechanical: data/gesbert_2021_tdeq.py melts the Q1..Q25 columns);
#   (2) tie S1 Data column -> Table 5 profile, using the age groups in the xlsx.
#
# NOTE the paper reversed the seven negatively worded F4-HQP items before
# printing Table 5 (stated in Methods, and S1 Data carries seven "<Q> inversé"
# columns for exactly Q1,Q5,Q7,Q11,Q12,Q16,Q24).  The live table stores the RAW
# columns, so the prediction for those seven is 7 - published.
#
# Item 8 has no Table 5 row (it was the item dropped from the CFA), so it is
# pinned by elimination once the other 24 are.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "gesbert_2021_tdeq"
ITEMS <- paste0("Q", 1:25)
REV   <- c(1, 5, 7, 11, 12, 16, 24)
S1URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0246823.s005"

# Paper Table 5: M for M15, M16, M17, M18, as printed (F4 items reverse-scored).
PUB <- rbind(
  "1"=c(4.05,3.50,3.53,3.31), "2"=c(5.36,4.93,3.84,4.75), "3"=c(5.42,5.25,3.46,4.81),
  "4"=c(3.78,3.37,3.30,3.68), "5"=c(4.94,5.31,4.30,4.93), "6"=c(5.05,5.31,4.00,4.25),
  "7"=c(4.63,4.06,4.53,4.43), "9"=c(4.94,3.93,3.46,3.43), "10"=c(4.94,4.56,4.46,4.93),
  "11"=c(3.89,4.81,4.61,4.25), "12"=c(4.00,4.50,3.84,3.87), "13"=c(4.05,3.93,4.76,4.43),
  "14"=c(4.89,5.37,5.30,4.50), "15"=c(4.05,4.00,3.07,3.12), "16"=c(4.26,3.87,3.69,3.56),
  "17"=c(3.83,3.37,2.84,3.37), "18"=c(5.84,5.50,4.30,4.81), "19"=c(4.94,4.31,4.00,4.06),
  "20"=c(4.61,4.18,4.07,4.12), "21"=c(4.21,4.18,4.76,4.00), "22"=c(4.26,3.75,3.76,3.62),
  "23"=c(4.77,4.06,3.53,3.93), "24"=c(4.15,4.37,3.53,4.25), "25"=c(4.52,3.81,2.84,3.00))

## ---- stage 1: live item code -> S1 Data column -------------------------------
d <- irw::irw_fetch(TABLE)                       # 1,596 rows; a trivial export
d$resp <- as.numeric(d$resp)
live_mean <- tapply(d$resp, d$item, mean)[ITEMS]
live_n    <- tapply(d$resp, d$item, length)[ITEMS]

tf <- tempfile(fileext = ".xlsx")
download.file(S1URL, tf, quiet = TRUE, mode = "wb")
raw <- as.data.frame(read_excel(tf))
X   <- sapply(ITEMS, function(c) suppressWarnings(as.numeric(raw[[c]])))
src_mean <- apply(X, 2, mean, na.rm = TRUE)
src_n    <- apply(X, 2, function(v) sum(!is.na(v)))

cat("=== stage 1: live item vs S1 Data column (n and mean) ===\n")
cat(sprintf("%-5s %6s %6s %9s %9s %9s\n", "item", "n_live", "n_src", "mean_live", "mean_src", "diff"))
for (it in ITEMS)
  cat(sprintf("%-5s %6d %6d %9.4f %9.4f %9.6f\n", it, live_n[it], src_n[it],
              live_mean[it], src_mean[it], live_mean[it] - src_mean[it]))
stage1 <- all(live_n == src_n) && max(abs(live_mean - src_mean)) < 1e-9
cat(sprintf("stage 1: n identical for all 25 = %s ; max |mean diff| = %.2e\n\n",
            all(live_n == src_n), max(abs(live_mean - src_mean))))

## ---- stage 2: S1 Data column -> Table 5 profile ------------------------------
ag <- toupper(trimws(as.character(raw[["AGE-GROUP"]])))
grp <- c("M15", "M16", "M17", "M18")
obs <- t(sapply(ITEMS, function(c) sapply(grp, function(g) mean(X[ag == g, c], na.rm = TRUE))))

pred <- PUB
for (r in rownames(pred)) if (as.integer(r) %in% REV) pred[r, ] <- 7 - pred[r, ]

# Distance = sum of the three SMALLEST |deviations| across the four age groups.
# The worst group is dropped because Table 5's M16 entry for item 19 is off by
# exactly 1.00 (4.31 printed vs 5.31 in the data) -- a single-cell misprint; the
# other three groups agree to 0.01/0.00/0.06.  Every other item matches on all
# four groups, so the robust metric costs nothing elsewhere.
dist <- function(p, o) sum(sort(abs(p - o))[1:3])

cat("=== stage 2: paper Table 5 profile vs per-column age-group means ===\n")
cat(sprintf("%-6s %-34s %-34s %8s %-14s\n", "paper", "predicted (raw scale)", "observed for own column",
            "d_own", "runner-up"))
allok <- TRUE
for (r in rownames(pred)) {
  own <- paste0("Q", r)
  ds  <- sapply(ITEMS, function(c) dist(pred[r, ], obs[c, ]))
  o   <- order(ds)
  best <- ITEMS[o[1]]; run <- ITEMS[o[2]]
  ok <- best == own && ds[run] > 3 * max(ds[own], 1e-3)
  allok <- allok && ok
  cat(sprintf("item %-2s %-34s %-34s %8.3f %-8s %6.3f  %s\n", r,
              paste(sprintf("%.2f", pred[r, ]), collapse = " "),
              paste(sprintf("%.2f", obs[own, ]), collapse = " "),
              ds[own], run, ds[run], if (ok) "ok" else "MISMATCH"))
}
left <- setdiff(ITEMS, paste0("Q", rownames(pred)))
cat(sprintf("\nunclaimed column (item with no Table 5 row): %s -- pinned by elimination\n",
            paste(left, collapse = ",")))

cat("\nWhat this does NOT establish: Q8's wording is fixed only by elimination (the\n",
    "paper dropped item 8 from the CFA and prints no statistics for it), and the\n",
    "response-anchor mapping (1 = strongly disagree ... 6 = strongly agree) comes\n",
    "from the Methods text, not from this comparison.\n", sep = "")

cat(if (stage1 && allok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
