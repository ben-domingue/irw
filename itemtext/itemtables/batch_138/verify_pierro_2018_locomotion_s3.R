# verify_pierro_2018_locomotion_s3.R
#
# CLAIM UNDER TEST (mapping_basis = reconstructed).
# The live item codes loc1..loc12 (with locr6, locr9) are the S3 File .sav's own
# column names, but that .sav carries NO variable labels, so the codes are bare
# positional indices into the RMQ Locomotion subscale. The shipped item_text
# assigns them the RMQ's locomotion items in the order its own scoring key lists
# them: Locomotion = [Q1 + Q3 + Q4 + Q5 + Q8 + (7-Q13) + Q16 + Q21 + (7-Q24) +
# Q25 + Q28 + Q29] / 12, i.e. within-subscale positions 1..12 = RMQ items
# 1,3,4,5,8,13R,16,21,24R,25,28,29.
#
# The falsifiable prediction: the two reverse-worded RMQ items sit at
# within-subscale positions 6 and 9 and NOWHERE ELSE, so in the LIVE data
# exactly loc r6 and locr9 -- and no other item -- must behave as reverse-keyed,
# and reversing exactly those two must reproduce the paper's published Study 3
# statistics. If item_text for, say, loc7 and locr9 had been swapped, the
# negative item-rest correlation would land on loc7 instead and this would fail.
#
# Published values, Pierro, Pica, Giannini, Higgins & Kruglanski (2018),
# PLOS ONE 13(3):e0193357, Study 3 Measures ("Locomotion and assessment
# orientations"): locomotion Cronbach's alpha = .83; the locomotion and
# assessment scales are uncorrelated, r = .12, p = .25.
#
# WHAT THIS DOES NOT ESTABLISH: it pins the two reverse-worded positions and the
# storage direction, not the order of the ten positively-worded items among
# themselves. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "pierro_2018_locomotion_s3"
PUB_ALPHA <- 0.83
PUB_R_LOC_ASS <- 0.12
REV <- c("locr6", "locr9")
ORDER <- c("loc1","loc2","loc3","loc4","loc5","locr6",
           "loc7","loc8","locr9","loc10","loc11","loc12")

alpha <- function(M) {
    M <- M[stats::complete.cases(M), , drop = FALSE]
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, stats::var)) / stats::var(rowSums(M)))
}

d <- irw::irw_fetch(TABLE)
W <- stats::reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id",
                    timevar = "item", direction = "wide")
colnames(W) <- sub("^resp\\.", "", colnames(W))
X <- as.matrix(W[, ORDER])
cat(sprintf("live data: %d respondents x %d items\n\n", nrow(X), ncol(X)))

# --- Route 6, keying polarity: item-rest r in the STORED direction ----------
cat("item-rest correlation, stored direction (negative => reverse-worded):\n")
ir <- sapply(ORDER, function(c) stats::cor(X[, c], rowSums(X[, setdiff(ORDER, c), drop = FALSE])))
for (c in ORDER)
    cat(sprintf("  %-7s %7.3f%s\n", c, ir[c], if (c %in% REV) "   <- code marks reverse" else ""))
neg <- names(ir)[ir < 0]
cat(sprintf("\nitems with negative item-rest r: %s\n", paste(sort(neg), collapse = ", ")))
cat(sprintf("codes carrying the 'r' reverse marker: %s\n", paste(sort(REV), collapse = ", ")))
ok_polarity <- setequal(neg, REV)
cat(sprintf("polarity class matches the code markers: %s\n\n", ok_polarity))

# --- Route 3, published statistics -----------------------------------------
Y <- X
Y[, REV] <- 7 - Y[, REV]
a_stored <- alpha(X); a_rev <- alpha(Y)
cat(sprintf("Cronbach's alpha, stored direction        : %.4f\n", a_stored))
cat(sprintf("Cronbach's alpha, reversing %s : %.4f   (published %.2f)\n",
            paste(REV, collapse = "+"), a_rev, PUB_ALPHA))
ok_alpha <- abs(a_rev - PUB_ALPHA) < 0.01 && a_rev - a_stored > 0.1

# alpha is symmetric to WHICH pair is reversed only if the pair is right; show
# that no other pair does as well.
best_other <- max(sapply(setdiff(ORDER, REV), function(c) {
    Z <- X; Z[, c] <- 7 - Z[, c]; Z[, REV[1]] <- 7 - Z[, REV[1]]
    alpha(Z)
}))
cat(sprintf("best alpha reversing locr6 + any OTHER single item: %.4f\n\n", best_other))

# --- Route 3 again, the cross-scale correlation the paper publishes ---------
a <- irw::irw_fetch("pierro_2018_assessment_s3")
WA <- stats::reshape(as.data.frame(a)[, c("id", "item", "resp")], idvar = "id",
                     timevar = "item", direction = "wide")
colnames(WA) <- sub("^resp\\.", "", colnames(WA))
AREV <- c("assr1", "assr5", "assr11")
AORD <- c("assr1","ass2","ass3","ass4","assr5","ass6",
          "ass7","ass8","ass9","ass10","assr11","ass12")
A <- as.matrix(WA[, AORD]); A[, AREV] <- 7 - A[, AREV]
m <- merge(data.frame(id = W$id, loc = rowMeans(Y)),
           data.frame(id = WA$id, ass = rowMeans(A)), by = "id")
r <- stats::cor(m$loc, m$ass)
cat(sprintf("r(locomotion, assessment) with these reversals: %.3f   (published %.2f)\n\n",
            r, PUB_R_LOC_ASS))
ok_r <- abs(r - PUB_R_LOC_ASS) < 0.02

cat("What this does NOT establish: the ten positively-worded items are\n")
cat("interchangeable under every statistic used here, so their order among\n")
cat("themselves rests on the RMQ scoring key alone. Status is PARTIAL.\n\n")

cat(if (ok_polarity && ok_alpha && ok_r) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
