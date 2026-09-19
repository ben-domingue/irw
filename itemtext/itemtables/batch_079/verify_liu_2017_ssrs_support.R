# verify_liu_2017_ssrs_support.R
#
# CLAIM UNDER TEST -- live item "Sk" carries SSRS item k's wording.
#
# The IRW codes S1..S10 are the .sav's own column names (data/liu_2017_cancer_exercise.py
# melts them by literal name), so there is no positional step; what still has to be shown
# is that the .sav's column NUMBERING is the SSRS's own item numbering, since the file
# carries no variable labels and no value labels at all.
#
# Two independent, falsifiable predictions of the canonical SSRS (Xiao 1994):
#   (a) Subscale composition -- Objective = items 2,6,7; Subjective = items 1,3,4,5;
#       Utilization = items 8,9,10. The deposit ships its OWN precomputed subscale
#       columns (SObjective/SSubjective/SUtilization/Stotal), so this is an exact
#       arithmetic identity, not a correlation.
#   (b) Response format -- items 1-4 and 8-10 are single-choice 1-4; item 5 is a sum
#       over 5 family sources each 1-4 (5-20); items 6 and 7 are counts of sources.
#       The source paper states exactly this: "a four-point Likert scale (except
#       items 5-7)" (Liu et al. 2017, PLOS ONE, Methods).
#
# A swap of item_text between two items in DIFFERENT subscales breaks (a);
# a swap involving 5, 6 or 7 breaks (b).
#
# Fetches its own data: the study's S1 File .sav from PLOS (not Redivis), plus the
# item/resp SETS server-side via irw::irw_table_sets() (no table export).

suppressMessages({library(haven); library(irw)})

TABLE <- "liu_2017_ssrs_support"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0169375.s001")
f <- file.path(tempdir(), "liu2017_s001.sav")
if (!file.exists(f)) download.file(URL, f, quiet = TRUE, mode = "wb")
d <- as.data.frame(haven::read_sav(f))
S <- paste0("S", 1:10)

ok <- TRUE

cat("=== (a) subscale identities: deposit's own totals vs canonical SSRS composition ===\n")
checks <- list(
  list("SObjective  = S2+S6+S7        ", c("S2","S6","S7"),        "SObjective"),
  list("SSubjective = S1+S3+S4+S5     ", c("S1","S3","S4","S5"),   "SSubjective"),
  list("SUtilization= S8+S9+S10       ", c("S8","S9","S10"),       "SUtilization"),
  list("Stotal      = S1..S10         ", S,                        "Stotal"))
for (ch in checks) {
  calc <- rowSums(d[, ch[[2]], drop = FALSE])
  obs  <- d[[ch[[3]]]]
  keep <- !is.na(obs) & !is.na(calc)
  md   <- max(abs(calc[keep] - obs[keep]))
  n    <- sum(keep); m <- sum(abs(calc[keep] - obs[keep]) < 1e-9)
  cat(sprintf("%s  exact %3d/%3d   max|diff| = %g\n", ch[[1]], m, n, md))
  if (m != n) ok <- FALSE
}

cat("\n  falsification control -- the same identities under a swap of S1 and S2\n")
d2 <- d; d2$S1 <- d$S2; d2$S2 <- d$S1
c1 <- rowSums(d2[, c("S2","S6","S7")]); k <- !is.na(d$SObjective)
cat(sprintf("  swapped SObjective exact: %d/%d (must be far below %d)\n",
            sum(abs(c1[k] - d$SObjective[k]) < 1e-9), sum(k), sum(k)))

cat("\n=== (b) per-item response format vs the paper's '4-point except items 5-7' ===\n")
expect <- c(S1="1-4", S2="1-4", S3="1-4", S4="1-4",
            S5="composite 5-20", S6="count", S7="count",
            S8="1-4", S9="1-4", S10="1-4")
for (v in S) {
  u <- sort(unique(na.omit(d[[v]])))
  cat(sprintf("%-4s observed %2.0f-%2.0f  (%2d levels)   expected: %s\n",
              v, min(u), max(u), length(u), expect[[v]]))
}
lik <- c("S1","S2","S3","S4","S8","S9","S10")
in14 <- all(sapply(lik, function(v) all(na.omit(d[[v]]) %in% 1:4)))
s5   <- all(na.omit(d$S5) >= 5) && max(na.omit(d$S5)) > 4 && max(na.omit(d$S5)) <= 20
s67  <- max(na.omit(d$S6)) > 4 && max(na.omit(d$S7)) > 4
cat(sprintf("\n  7 four-point items all within 1-4: %s | S5 inside 5-20 and >4: %s | S6,S7 exceed 4: %s\n",
            in14, s5, s67))
if (!(in14 && s5 && s67)) ok <- FALSE

cat("\n=== live IRW sets (server-side, no export) ===\n")
ts <- irw::irw_table_sets(TABLE)
li <- sort(unlist(ts$item)); lr <- sort(as.numeric(unlist(ts$resp)))
cat("live items:", paste(li, collapse = ", "), "\n")
cat("live resp :", paste(lr, collapse = ", "), "\n")
sav_r <- sort(unique(na.omit(unlist(d[, S]))))
cat("sav  resp :", paste(sav_r, collapse = ", "), "\n")
if (!setequal(li, S)) ok <- FALSE
if (!setequal(lr, sav_r)) ok <- FALSE

cat("\nWHAT THIS DOES NOT ESTABLISH: S1/S3/S4 are all Subjective and all 1-4, so their\n",
    "wordings are interchangeable under both routes; likewise S8/S9/S10 within\n",
    "Utilization; and S6 vs S7 (both Objective source-counts) are separated only by\n",
    "content plausibility (mean 2.89 for financial/practical help vs 4.56 for comfort\n",
    "and concern), not by structure. Status is PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
