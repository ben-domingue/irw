# Mapping check for rogowska_2023_maia2 (10.1038/s41598-023-48536-0, PMC10693589).
#
# Usage: Rscript verify_rogowska_2023_maia2.R [path/to/response.csv]
#
# Claim, in two links:
#   (a) IRW item MAIA2_NN is the item the paper reports as MAIA-2_NN. The paper's
#       Table 1 prints, for all 37 codes, the unstandardised and standardised
#       loading from an eight-factor ML CFA (factor variances fixed at 1, AMOS) on
#       these 323 respondents. Refitting that model on the shipped data must put
#       each published pair on the same code. Within every subscale the published
#       (Estimate, Std.Est) pairs are distinct, so a swap of any two codes inside a
#       subscale moves a pair; a swap across subscales breaks the model itself.
#   (b) Paper code MAIA-2_NN is stem NN of the deposit's "MAIA-2 (Polish)" sheet.
#       Table 1 hash-marks the 24 codes kept in the Brief MAIA-2, and the deposit's
#       "Brief MAIA-2 (Polish)" sheet prints 24 stems. Those 24 stems are,
#       verbatim, full-sheet stems with exactly the hash-marked numbers (checked in
#       the item text build and hard-coded below), so the numbering of the text and
#       the numbering of the codes agree on 24 of 37 items.
#
# What this does NOT establish: (a) cannot separate MAIA-2_19 from _20, whose
# published pairs are identical (1.09 / 0.82). (b) cannot separate two non-Brief stems within a
# subscale (05/07/08, 13/14, 16/18/21/22, 23/24, 28, 01). For those the tie from
# code to stem rests on the shared 1-37 numbering of questionnaire and codes, which
# is also the canonical MAIA-2 order (Mehling et al. 2018). Hence PARTIAL, not
# VERIFIED. Nor does a CFA sign anything about scoring direction: it cannot tell
# whether items 5-12 and 15 were stored reverse-scored, which is why those items
# ship without anchors.
#
# The deposit's two fractional (imputed) cells are dropped in IRW, so the refit
# uses FIML over 11,949 of the paper's 11,951 cells; tolerance allows for that.

suppressMessages(library(lavaan))

args <- commandArgs(trailingOnly = TRUE)
path <- if (length(args)) args[1] else "irw_output/rogowska_2023_maia2.csv"
d <- read.csv(path)

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cat(sprintf("respondents: %d (paper: 323)\n", nrow(w)))

code <- function(i) sprintf("MAIA2_%02d", i)
scales <- list(NOT = 1:4, ND = 5:10, NW = 11:15, AR = 16:22, EA = 23:27,
               SR = 28:31, BL = 32:34, TR = 35:37)
model <- paste(sprintf("%s =~ %s", names(scales),
                       sapply(scales, function(s) paste(code(s), collapse = " + "))),
               collapse = "\n")

# Table 1: Estimate, Std.Est for MAIA-2_01..37.
pub_est <- c(0.94, 0.88, 1.01, 0.96, 0.74, 0.83, 0.63, 0.89, 1.05, 1.06,
             1.20, 1.13, 0.13, 0.03, 0.84, 1.04, 1.10, 0.99, 1.09, 1.09,
             1.00, 1.10, 0.98, 0.98, 1.17, 1.12, 1.15, 1.13, 1.12, 1.18,
             1.18, 0.95, 1.08, 1.16, 1.40, 1.35, 1.13)
pub_std <- c(0.60, 0.63, 0.65, 0.66, 0.54, 0.61, 0.51, 0.61, 0.82, 0.79,
             0.84, 0.82, 0.09, 0.02, 0.65, 0.72, 0.81, 0.73, 0.82, 0.82,
             0.78, 0.76, 0.66, 0.68, 0.82, 0.79, 0.79, 0.78, 0.80, 0.79,
             0.83, 0.71, 0.71, 0.83, 0.92, 0.89, 0.77)
# Items whose published pair ties another in the same subscale cannot be separated
# by this route; they are reported and left out of the nearest-code test.
# (MAIA-2_19 and _20 both print 1.09 / 0.82.)
key <- paste(pub_est, pub_std)
tied <- integer(0)
for (s in scales) tied <- c(tied, s[duplicated(key[s]) | duplicated(key[s], fromLast = TRUE)])
cat(sprintf("tied published pairs (not separable here): %s\n",
            if (length(tied)) paste(code(tied), collapse = ", ") else "none"))

fit <- cfa(model, data = w, std.lv = TRUE, estimator = "ML", missing = "fiml")
pe <- standardizedSolution(fit)
pe <- pe[pe$op == "=~", ]
raw <- parameterEstimates(fit)
raw <- raw[raw$op == "=~", ]
obs_est <- setNames(raw$est, raw$rhs)[code(1:37)]
obs_std <- setNames(pe$est.std, pe$rhs)[code(1:37)]

res <- data.frame(item = code(1:37),
                  pub_est = pub_est, obs_est = round(obs_est, 3),
                  pub_std = pub_std, obs_std = round(obs_std, 3))
print(res, row.names = FALSE)

TOL <- 0.015
dev <- pmax(abs(obs_est - pub_est), abs(obs_std - pub_std))
cat(sprintf("\nlargest deviation: %.3f (tolerance %.3f; paper prints 2 dp)\n",
            max(dev), TOL))

# Within each subscale, is the published pair nearest to its own code? A swap
# inside a subscale would make some other code's observed pair the nearest one.
nearest_ok <- TRUE
for (s in scales) {
  for (i in setdiff(s, tied)) {
    dist <- sqrt((obs_est[s] - pub_est[i])^2 + (obs_std[s] - pub_std[i])^2)
    if (s[which.min(dist)] != i) {
      nearest_ok <- FALSE
      cat(sprintf("  published %s is nearest to %s\n", code(i), code(s[which.min(dist)])))
    }
  }
}
cat(sprintf("every published pair lands nearest its own code: %s\n", nearest_ok))

# Link (b): Table 1's hash-marked Brief codes vs. the full-sheet numbers of the
# 24 stems printed on the deposit's Brief sheet (matched verbatim at build time).
brief_hash  <- c(2, 3, 4, 6, 9, 10, 11, 12, 15, 17, 19, 20, 25, 26, 27, 29, 30, 31,
                 32, 33, 34, 35, 36, 37)
brief_sheet <- c(2, 3, 4, 6, 9, 10, 11, 12, 15, 17, 19, 20, 25, 26, 27, 29, 30, 31,
                 32, 33, 34, 35, 36, 37)
brief_ok <- identical(brief_hash, brief_sheet)
cat(sprintf("Brief subset: Table 1 hash marks == Brief sheet stems: %s\n", brief_ok))

cat("Not established: MAIA2_19 vs MAIA2_20 (tied in Table 1); order of the 13\n",
    "non-Brief stems within their subscales beyond the shared 1-37 numbering;\n",
    "scoring direction of items 5-12 and 15.\n", sep = "")

cat(if (max(dev) <= TOL && nearest_ok && brief_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
