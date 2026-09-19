# verify_ptacek2023_dass21.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: each IRW item code (S1, A2, D3, ... D21 -- the source CSV's own
# column names) carries the canonically numbered DASS-21 item of that number, and the
# S/A/D letter in the code names the Stress/Anxiety/Depression subscale.
#
# FALSIFIABLE PREDICTION: Ptacek & Jelinek (2024), Ceskoslovenska psychologie 68(1),
# 30-48, Table 4 publishes Mean/SD/Skewness/Kurtosis for the DASS-21 Depression,
# Anxiety and Stress raw subscale sums in this exact N=299 sample. Summing the seven
# items this extraction assigns to each subscale must reproduce all twelve moments.
# A wrong subscale partition moves those numbers (random 7/7/7 partitions of the same
# 21 items give first-block means of 6.33-7.33 against a published 7.02), and a
# reverse-scored or mis-anchored resp mapping would move them further still.
#
# WHAT THIS DOES NOT ESTABLISH: it pins subscale MEMBERSHIP (and hence the letters in
# the codes), not the order of the seven items WITHIN each subscale. That rests on the
# instrument's published item numbering, which the source column names reproduce.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "ptacek2023_dass21"

D <- c("D3","D5","D10","D13","D16","D17","D21")
A <- c("A2","A4","A7","A9","A15","A19","A20")
S <- c("S1","S6","S8","S11","S12","S14","S18")

# Ptacek & Jelinek (2024) Table 4: Mean, SD, Skewness, Kurtosis
PUB <- list(Depression = c(7.02, 5.76,  0.74, -0.45),
            Anxiety    = c(5.05, 5.03,  1.20,  0.75),
            Stress     = c(9.41, 4.96,  0.29, -0.63))
TOL <- c(0.02, 0.02, 0.02, 0.02)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

skew <- function(x) { n<-length(x); m<-mean(x); s<-sd(x); sum(((x-m)/s)^3)*n/((n-1)*(n-2)) }
kurt <- function(x) { n<-length(x); m<-mean(x); s<-sd(x)
                      (n*(n+1)/((n-1)*(n-2)*(n-3)))*sum(((x-m)/s)^4) - 3*(n-1)^2/((n-2)*(n-3)) }

blocks <- list(Depression = D, Anxiety = A, Stress = S)
worst <- 0
cat(sprintf("%-11s %-9s %10s %10s %8s\n", "subscale", "moment", "published", "observed", "diff"))
for (nm in names(blocks)) {
    tot <- rowSums(w[, blocks[[nm]]])
    obs <- c(mean(tot), sd(tot), skew(tot), kurt(tot))
    for (i in seq_along(obs)) {
        dif <- obs[i] - PUB[[nm]][i]
        worst <- max(worst, abs(dif) / TOL[i])
        cat(sprintf("%-11s %-9s %10.2f %10.3f %8.3f\n", nm,
                    c("mean","sd","skew","kurt")[i], PUB[[nm]][i], obs[i], dif))
    }
}
cat(sprintf("\nN with complete DASS-21 = %d (paper: 299)\n", sum(complete.cases(w[, c(D,A,S)]))))

# Discriminative power of the check: how far off is a wrong partition?
set.seed(20260910)
allc <- c(D, A, S)
devs <- replicate(2000, {
    p <- sample(allc)
    max(abs(c(mean(rowSums(w[, p[1:7]]))  - PUB$Depression[1],
              mean(rowSums(w[, p[8:14]])) - PUB$Anxiety[1],
              mean(rowSums(w[, p[15:21]]))- PUB$Stress[1])))
})
cat(sprintf("2000 random 7/7/7 partitions: worst-block mean deviation min %.2f, median %.2f\n",
            min(devs), median(devs)))
cat(sprintf("  (this mapping's worst mean deviation: %.3f)\n",
            max(abs(c(mean(rowSums(w[, D])) - PUB$Depression[1],
                      mean(rowSums(w[, A])) - PUB$Anxiety[1],
                      mean(rowSums(w[, S])) - PUB$Stress[1])))))

cat("\nNote: this route pins the D/A/S subscale partition (12/12 published moments to 2 dp)\n",
    "and the raw 0-3 scoring direction. It does NOT separate the seven items within a\n",
    "subscale from one another; that rests on the DASS-21's published item numbering,\n",
    "which the source CSV's column names (S1, A2, D3, ...) reproduce. Status: PARTIAL.\n", sep = "")

cat(if (worst <= 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
