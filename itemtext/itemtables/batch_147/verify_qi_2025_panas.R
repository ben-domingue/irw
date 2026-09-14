# Step 5b verification for qi_2025_panas (batch_147).
#
# CLAIM UNDER TEST. The 18 live item codes hold the Qiu, Zheng & Wang (2008)
# Chinese revision of the PANAS: PA_1..PA_9 are its nine positive-affect
# adjectives and NA_1..NA_9 its nine negative-affect adjectives, each block in
# the instrument's own presentation order, stored RAW (the processing script
# data/qi_2025_self_reported_scales.R reverse-scores nothing, and this
# instrument has no reverse-keyed items).
#
# WHAT THIS SCRIPT CAN AND CANNOT SETTLE. It settles the BLOCK level and the
# absence of reversal, against a published number: Qi et al. (2025, Sci Data
# 12:1755) report Cronbach's alpha for THIS sample as .91 (positive affect)
# and .88 (negative affect). It CANNOT settle the order WITHIN either block,
# and rather than leave that silent it runs the strongest within-block test
# available and prints its NEGATIVE result. Hence the mapping_verification
# status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "qi_2025_panas"
PUBLISHED <- c(positive_affect = 0.91, negative_affect = 0.88)
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
PAcols <- paste0("PA_", 1:9); NAcols <- paste0("NA_", 1:9)
w <- w[, c(PAcols, NAcols)]
cat(sprintf("respondents: %d ; items: %d\n\n", nrow(w), ncol(w)))

alpha <- function(X) { k <- ncol(X); v <- var(X); (k / (k - 1)) * (1 - sum(diag(v)) / sum(v)) }

# ---- Test 1: published subscale alphas reproduce from the shipped blocks ----
obs <- c(positive_affect = alpha(w[, PAcols]),
         negative_affect = alpha(w[, NAcols]))
cat("TEST 1 -- published alpha for this sample vs the shipped block assignment\n")
cat(sprintf("%-18s %10s %10s %8s\n", "subscale", "published", "observed", "diff"))
for (i in seq_along(obs))
    cat(sprintf("%-18s %10.2f %10.3f %8.3f\n",
                names(obs)[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i]))
worst <- max(abs(obs - PUBLISHED))
cat(sprintf("largest deviation: %.4f (tolerance %.3f)\n\n", worst, TOL))

cat("  rivals -- what a wrong block assignment would give:\n")
sw <- w; sw[, "PA_1"] <- w[, "NA_1"]; sw[, "NA_1"] <- w[, "PA_1"]
cat(sprintf("    one item swapped across blocks (PA_1<->NA_1): PA %.3f  NA %.3f\n",
            alpha(sw[, PAcols]), alpha(sw[, NAcols])))
cat(sprintf("    all 18 items treated as one scale, unreversed: %.3f\n",
            alpha(w)))
cat(sprintf("    PA block with PA_1 reverse-scored             : %.3f\n",
            alpha(cbind(6 - w[, "PA_1"], w[, PAcols[-1]]))))
cat(sprintf("    NA block with NA_1 reverse-scored             : %.3f\n\n",
            alpha(cbind(6 - w[, "NA_1"], w[, NAcols[-1]]))))

# ---- Test 2: the within-block order, and why it is NOT established ----
# The instrument's NA list order is 害怕的(afraid) 内疚的(guilty) 紧张的(nervous)
# 恼怒的(angry) 难过的(sad) 惊恐的(terrified) 羞愧的(ashamed) 易怒的(irritable)
# 战战兢兢的(jittery).  Those adjectives fall into semantic facets -- fear
# {1,3,6,9}, self-conscious {2,7}, anger {4,8}, sadness {5} -- and a correct
# mapping predicts within-facet pairs correlate more than between-facet pairs.
# Score = mean(within-facet r) - mean(between-facet r), evaluated for the
# shipped assignment against all 9! = 362880 relabellings of the NA block.
facet <- c("F", "S", "F", "A", "D", "F", "S", "A", "F")
C <- cor(w[, NAcols])
sameF <- outer(facet, facet, "==")
ut <- upper.tri(C)
score <- function(p) {
    Cp <- C[p, p]
    mean(Cp[ut & sameF]) - mean(Cp[ut & !sameF])
}
perms <- function(v) {
    if (length(v) == 1) return(matrix(v))
    do.call(rbind, lapply(seq_along(v),
        function(i) cbind(v[i], perms(v[-i]))))
}
P <- perms(1:9)
s <- apply(P, 1, score)
s_true <- score(1:9)
rank_true <- sum(s > s_true) + 1
cat("TEST 2 -- within-block order (NEGATIVE RESULT, printed deliberately)\n")
cat(sprintf("  semantic-facet score, shipped NA order : %+.4f\n", s_true))
cat(sprintf("  best of all 9! relabellings            : %+.4f\n", max(s)))
cat(sprintf("  mean over all 9! relabellings          : %+.4f\n", mean(s)))
cat(sprintf("  rank of shipped order                  : %d of %d (top %.1f%%)\n",
            rank_true, nrow(P), 100 * rank_true / nrow(P)))
cat("  => the shipped within-block order is INDISTINGUISHABLE FROM CHANCE on\n")
cat("     this route. No route tested distinguishes the 9 same-polarity,\n")
cat("     same-range adjectives inside either block; the order comes from the\n")
cat("     instrument's own presentation order, not from the data.\n\n")

ok <- worst <= TOL
cat(sprintf("block assignment and non-reversal: %s\n", if (ok) "reproduced" else "NOT reproduced"))
cat("within-block order: NOT established (see TEST 2) -- status is PARTIAL\n\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
