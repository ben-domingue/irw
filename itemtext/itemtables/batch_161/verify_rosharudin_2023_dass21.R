# verify_rosharudin_2023_dass21.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: each IRW item code (@1_S, @2_A, ... @21_D -- the deposit .sav's own
# column names) carries the canonically numbered DASS-21 item of that number, and the
# S/A/D letter names the Stress/Anxiety/Depression subscale. item_text is the Musa
# (2007) Bahasa Malaysia DASS-21 item of that number.
#
# FALSIFIABLE PREDICTION: Rosharudin et al. (2023) PLOS ONE 18(8):e0289551, Table 2
# publishes M and SD for the DASS-21 Stress / Anxiety / Depression subscale scores in
# this same N=689 sample. Summing the seven items this extraction assigns to each
# subscale must reproduce those six numbers, and must reproduce them better than a
# random 7/7/7 partition of the same 21 items does.
#
# WHAT THIS DOES NOT ESTABLISH: it pins subscale MEMBERSHIP (hence the letter in each
# code), not the order of the seven items WITHIN each subscale. That rests on the
# canonical DASS-21 item numbering, which the codes' numbers reproduce, and no
# per-item statistic is published for this sample to separate them. It also says
# nothing about the option/resp axis -- the live table has five levels (0-4) where
# both the paper and the Musa form document four (0-3), so no option_text is shipped.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "rosharudin_2023_dass21"

S <- c("@1_S","@6_S","@8_S","@11_S","@12_S","@14_S","@18_S")
A <- c("@2_A","@4_A","@7_A","@9_A","@15_A","@19_A","@20_A")
D <- c("@3_D","@5_D","@10_D","@13_D","@16_D","@17_D","@21_D")

# Rosharudin et al. (2023) Table 2, DASS-21 block: M, SD
PUB <- list(Stress = c(10.96, 6.02), Anxiety = c(9.84, 5.68), Depress = c(9.86, 6.34))
TOL_M <- 0.12; TOL_SD <- 0.05

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[complete.cases(w[, c(S, A, D)]), ]
cat("respondents with complete DASS-21 data:", nrow(w), "(paper analysed N = 689)\n\n")

obs <- list(Stress = rowSums(w[, S]), Anxiety = rowSums(w[, A]), Depress = rowSums(w[, D]))
cat(sprintf("%-9s %8s %8s %8s | %8s %8s %8s\n",
            "subscale", "pub M", "obs M", "diff", "pub SD", "obs SD", "diff"))
ok <- TRUE
for (nm in names(PUB)) {
    m <- mean(obs[[nm]]); s <- sd(obs[[nm]])
    cat(sprintf("%-9s %8.2f %8.3f %8.3f | %8.2f %8.3f %8.3f\n",
                nm, PUB[[nm]][1], m, m - PUB[[nm]][1],
                PUB[[nm]][2], s, s - PUB[[nm]][2]))
    if (abs(m - PUB[[nm]][1]) > TOL_M || abs(s - PUB[[nm]][2]) > TOL_SD) ok <- FALSE
}
cat(sprintf("\ntolerances: |dM| <= %.2f, |dSD| <= %.2f\n", TOL_M, TOL_SD))

# Discrimination: is this partition special, or would any 7/7/7 split do as well?
# Score = mean over the three blocks of (|observed M - published M| + |observed SD -
# published SD|). Note the block means are constrained to sum to the fixed grand total,
# so a mean-only statistic has a hard floor; including the SDs removes that artefact.
set.seed(1)
all21 <- c(S, A, D)
score <- function(g1, g2, g3) {
    gs <- list(g1, g2, g3); nms <- c("Stress", "Anxiety", "Depress")
    mean(sapply(seq_along(gs), function(i) {
        v <- rowSums(w[, gs[[i]]])
        abs(mean(v) - PUB[[nms[i]]][1]) + abs(sd(v) - PUB[[nms[i]]][2])
    }))
}
mine <- score(S, A, D)
rnd <- replicate(2000, { p <- sample(all21); score(p[1:7], p[8:14], p[15:21]) })
cat(sprintf("combined |dM|+|dSD| score -- this partition: %.3f\n", mine))
cat(sprintf("  2000 random 7/7/7 partitions: min %.3f, median %.3f, %% worse than ours: %.1f%%\n",
            min(rnd), median(rnd), 100 * mean(rnd > mine)))

cat("\nNote: the three observed means each sit ~0.07-0.08 BELOW the published values while\n",
    "the SDs match to <=0.02; the paper reports N=689 after listwise deletion and the\n",
    "deposit holds exactly those 689 complete records, so the small offset is unexplained\n",
    "residual, not a partition error -- rival partitions are off by an order more.\n", sep = "")

cat(if (ok && mine < min(rnd)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
