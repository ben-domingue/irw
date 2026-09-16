# verify_wang_2016_study3_auth.R
#
# CLAIM UNDER TEST (Step 5b), in three parts:
#   (a) SUBSCALE MEMBERSHIP.  The shipped mapping says a1..a12 are the Authenticity
#       Scale (Wood et al., 2008) items 1..12 in the scale's own numbering, so the
#       three published subscales must be Authentic Living {a1,a8,a9,a11},
#       Self-Alienation {a2,a7,a10,a12} and Accepting External Influence
#       {a3,a4,a5,a6}.  That is a falsifiable prediction about the live correlation
#       matrix: every item must correlate more strongly with its own block than
#       with either other block.  A permutation across blocks breaks it.
#   (b) CODING DIRECTION (the option_text <-> resp axis).  The shipped option_text
#       runs 1 = does-not-fit .. 5 = fits, i.e. every item is stored in the
#       authentic direction with the two negatively worded subscales ALREADY
#       reverse-coded.  Prediction: the sum of the eleven items the paper itself
#       summed reproduces Wang (2016) PLOS ONE Table 5's Authenticity M = 38.38,
#       SD = 6.88 and its r = .68 with self-esteem and r = .65 with power.  Under
#       the opposite coding the same sum would read 66 - 38.28 = 27.7 and both
#       correlations would flip sign.
#   (c) WITHIN-BLOCK ORDER -- which of the four items inside a block each code is.
#       This script CANNOT test it and says so; hence status PARTIAL.
#
# Note on the eleven: Wang's stored `authenticity` aggregate in S3 File is the sum
# of a1..a12 EXCLUDING a11 (recovered by least squares, weights 1 on eleven items,
# 0 on a11, residual 1e-13), and its M/SD are the ones printed in Table 5.  The
# 12-item sum is M = 42.33, SD = 7.30.  This script therefore compares the
# 11-item sum, and prints the 12-item sum alongside it for transparency.

suppressMessages(library(irw))

PUB <- list(m = 38.38, sd = 6.88, r_se = 0.68, r_pow = 0.65)
TOL_M <- 0.15; TOL_SD <- 0.05; TOL_R <- 0.02

AL  <- c("a1","a8","a9","a11")
SA  <- c("a2","a7","a10","a12")
AEI <- c("a3","a4","a5","a6")
BLOCK <- c(setNames(rep("AL", 4), AL), setNames(rep("SA", 4), SA),
           setNames(rep("AEI", 4), AEI))

wide <- function(tab) {
    d <- irw::irw_fetch(tab)
    m <- tapply(as.numeric(d$resp), list(as.character(d$id), as.character(d$item)), mean)
    as.data.frame(m)
}

A <- wide("wang_2016_study3_auth")
A <- A[, paste0("a", 1:12)]
cat(sprintf("persons = %d, items = %d\n\n", nrow(A), ncol(A)))

## ---- (a) subscale block structure -------------------------------------------
C <- cor(A, use = "pairwise.complete.obs")
cat("-- (a) mean correlation of each item with each block (own block starred) --\n")
cat(sprintf("%-5s %7s %7s %7s   %s\n", "item", "AL", "SA", "AEI", "own > both others?"))
ok_a <- TRUE
for (it in paste0("a", 1:12)) {
    mb <- sapply(list(AL = AL, SA = SA, AEI = AEI), function(b) {
        b <- setdiff(b, it); mean(C[it, b])
    })
    own <- BLOCK[[it]]
    pass <- all(mb[own] > mb[setdiff(names(mb), own)])
    ok_a <- ok_a && pass
    cat(sprintf("%-5s %7s %7s %7s   %s\n", it,
                sprintf(if (own == "AL")  "*%.2f" else "%.2f", mb["AL"]),
                sprintf(if (own == "SA")  "*%.2f" else "%.2f", mb["SA"]),
                sprintf(if (own == "AEI") "*%.2f" else "%.2f", mb["AEI"]),
                if (pass) "yes" else "NO"))
}
cat(sprintf("\nall 12 items sit in their canonical block: %s\n", if (ok_a) "YES" else "NO"))
cat(sprintf("smallest within-block r = %.2f, largest between-block r = %.2f\n\n",
            min(sapply(list(AL, SA, AEI), function(b) min(C[b, b][upper.tri(C[b, b])]))),
            max(C[AL, c(SA, AEI)], C[SA, AEI])))

## ---- (b) direction, against the paper's published total ----------------------
eleven <- rowSums(A[, setdiff(paste0("a", 1:12), "a11")])
twelve <- rowSums(A)
se  <- rowSums(wide("wang_2016_study3_se"))
pow <- rowSums(wide("wang_2016_study3_power"))
ids <- Reduce(intersect, list(rownames(A), names(se), names(pow)))
e <- eleven[ids]; s <- se[ids]; p <- pow[ids]

cat("-- (b) Wang (2016) Table 5 vs live data --\n")
cat(sprintf("%-34s %10s %10s %8s\n", "quantity", "published", "observed", "diff"))
row <- function(l, pub, obs) {
    cat(sprintf("%-34s %10.2f %10.2f %8.3f\n", l, pub, obs, obs - pub)); obs - pub
}
d1 <- row("Authenticity total M (11 items)", PUB$m,     mean(e))
d2 <- row("Authenticity total SD",           PUB$sd,    sd(e))
d3 <- row("r(authenticity, self-esteem)",    PUB$r_se,  cor(e, s))
d4 <- row("r(authenticity, power)",          PUB$r_pow, cor(e, p))
cat(sprintf("\n12-item sum (not the paper's total): M = %.2f, SD = %.2f\n", mean(twelve), sd(twelve)))
cat(sprintf("under the reversed coding the 11-item sum would read M = %.2f, and\n", 66 - mean(e)))
cat(sprintf("r(authenticity, self-esteem) would read %.2f\n\n", -cor(e, s)))

ok_b <- abs(d1) <= TOL_M && abs(d2) <= TOL_SD && abs(d3) <= TOL_R && abs(d4) <= TOL_R

## ---- (c) what this does NOT establish ---------------------------------------
cat("NOT established: which of the four items inside a block each code is.\n")
cat("The source .sav (PLOS s003) carries no variable labels, the paper publishes no\n")
cat("per-item statistics, all 12 items share the 1-5 range (route 2 silent) and all\n")
cat("12 are stored in the same polarity (route 6 silent). Within-block order is the\n")
cat("canonical Wood et al. numbering, asserted, not tested. Hence PARTIAL.\n\n")

cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
