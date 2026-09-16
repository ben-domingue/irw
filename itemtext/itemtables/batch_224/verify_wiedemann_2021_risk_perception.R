# verify_wiedemann_2021_risk_perception.R
#
# Claim under test: the five .sav variable labels (F01 comprehensibility,
# F02 clarity, F03 doubts about the assessors' qualification, F04 risk
# magnitude, F06 fear) are attached to the right item codes, and the 7-point
# scale runs 1 = low anchor .. 7 = high anchor (so option_text's endpoints are
# on the right ends).
#
# Falsifiable prediction: Wiedemann et al. (2021) PLoS ONE 16(7):e0253762
# Table 3 publishes the five dependent variables' means in experiment R1
# (hazard identification) for each of the four 2x2 treatment cells U0E0, U0E1,
# U1E0, U1E1. The live IRW table carries cov_risk_type (1 = R1) and
# cov_factor1 / cov_factor2 (the U and E factors, 0/1). Re-deriving those 20
# cell means from the live data and matching them to the published grid pins
# every item against every other item (no two rows of Table 3 have the same
# four-cell profile), and pins the direction: the table's own caption states
# "the higher the scores, the higher the value on the variables".
#
# What it does NOT establish: the exact German wording at each end of the
# scale (the deposit publishes only the study's English rendering of the
# anchors), or the within-item anchor text beyond its polarity.

suppressMessages(library(irw))

TABLE <- "wiedemann_2021_risk_perception"
ITEMS <- c("F01", "F02", "F03", "F04", "F06")
CELLS <- c("U0E0", "U0E1", "U1E0", "U1E1")
TOL <- 0.01   # the paper truncates to 2dp; complete cases reproduce it exactly

# Paper Table 3 (R1), rows in the order: text understandability, clarity of
# risk information, doubts in the professional competencies, risk perception,
# fear arousal -- i.e. the claimed F01, F02, F03, F04, F06.
PUBLISHED <- matrix(c(
    6.66, 6.51, 6.34, 6.18,
    5.85, 5.92, 4.65, 4.66,
    4.37, 3.55, 4.84, 5.03,
    3.55, 4.14, 3.38, 3.77,
    2.81, 3.63, 3.27, 2.67),
    nrow = 5, byrow = TRUE, dimnames = list(ITEMS, CELLS))

d <- irw::irw_fetch(TABLE)
d <- d[d$cov_risk_type == "Hazard-Identifikation", ]   # experiment R1 only
# The MANOVA is listwise, so restrict to respondents with all five items, as
# the paper did: 2 of 109 R1 respondents are missing one item apiece.
complete <- names(which(table(d$id) == length(ITEMS)))
cat(sprintf("R1 respondents: %d total, %d complete on all five items\n",
            length(unique(d$id)), length(complete)))
d <- d[d$id %in% as.integer(complete), ]
cell <- paste0(d$cov_factor1, "E", substr(d$cov_factor2, 2, 2))
obs <- tapply(d$resp, list(d$item, cell), mean)
obs <- obs[ITEMS, CELLS]

cat(sprintf("%-5s %-6s %10s %10s %8s\n", "item", "cell", "published", "observed", "diff"))
worst <- 0
for (i in ITEMS) for (j in CELLS) {
    df <- obs[i, j] - PUBLISHED[i, j]
    worst <- max(worst, abs(df))
    cat(sprintf("%-5s %-6s %10.2f %10.2f %8.3f\n", i, j, PUBLISHED[i, j], obs[i, j], df))
}
cat(sprintf("\nlargest deviation: %.3f (tolerance %.2f)\n", worst, TOL))

# Cross-item falsification: is the claimed assignment the best one? Score every
# permutation of the five item codes against the published grid.
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
scores <- sapply(perms(ITEMS), function(p) max(abs(obs[p, CELLS] - PUBLISHED)))
cat(sprintf("permutation check: claimed assignment max-dev %.3f; best of the other %d permutations %.3f\n",
            worst, length(scores) - 1, min(scores[scores > worst + 1e-9])))

cat("Direction: Table 3's caption reads \"the higher the scores, the higher the value\n",
    "on the variables\", which is what places each item's low anchor at resp=1.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
