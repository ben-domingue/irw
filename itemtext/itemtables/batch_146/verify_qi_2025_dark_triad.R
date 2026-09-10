# Step 5b verification for qi_2025_dark_triad (batch_146).
#
# CLAIM UNDER TEST: DT_1..DT_27 are the SD3's 27 items in canonical order --
# Machiavellianism 1-9 = DT_1..DT_9, Narcissism 1-9 = DT_10..DT_18,
# Psychopathy 1-9 = DT_19..DT_27 -- stored RAW (the processing script reverses
# nothing), so the SD3's five reverse-keyed items (N2, N6, N8, P2, P7) must sit
# at DT_11, DT_15, DT_17, DT_20, DT_25.
#
# FALSIFIABLE PREDICTION: the source paper (Qi et al. 2025, Sci Data 12:1755)
# reports Cronbach's alpha for THIS sample as .71 / .75 / .64 for
# Machiavellianism / Narcissism / Psychopathy. Alpha depends on both the block
# membership and the reversal set, so if the blocks or the reverse positions
# were wrong the three published values would not reproduce. Rival reversal
# sets are printed alongside to show how far off they land.

suppressMessages(library(irw))

TABLE     <- "qi_2025_dark_triad"
PUBLISHED <- c(Machiavellianism = 0.71, Narcissism = 0.75, Psychopathy = 0.64)
TOL       <- 0.005

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, paste0("DT_", 1:27)]

alpha <- function(X) { k <- ncol(X); v <- var(X); (k / (k - 1)) * (1 - sum(diag(v)) / sum(v)) }
rev5  <- function(X, cols) { for (cc in cols) X[, cc] <- 6 - X[, cc]; X }

M <- w[,  1:9 ]   # DT_1 .. DT_9
N <- w[, 10:18]   # DT_10 .. DT_18
P <- w[, 19:27]   # DT_19 .. DT_27

obs <- c(Machiavellianism = alpha(M),
         Narcissism       = alpha(rev5(N, c(2, 6, 8))),   # DT_11, DT_15, DT_17
         Psychopathy      = alpha(rev5(P, c(2, 7))))      # DT_20, DT_25

cat(sprintf("%-18s %10s %10s %8s\n", "subscale", "published", "observed", "diff"))
for (i in seq_along(obs))
    cat(sprintf("%-18s %10.2f %10.3f %8.3f\n",
                names(obs)[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i]))

cat("\nrival reversal sets (these are what a wrong keying would give):\n")
cat(sprintf("  Narcissism, no reversal          : %.3f\n", alpha(N)))
cat(sprintf("  Psychopathy, no reversal         : %.3f\n", alpha(P)))
cat(sprintf("  Psychopathy, DT_25 reversed only : %.3f\n", alpha(rev5(P, 7))))
cat(sprintf("  Psychopathy, DT_20 reversed only : %.3f\n", alpha(rev5(P, 2))))

cat("\nitem-rest correlations within each block (raw, unreversed):\n")
for (nm in c("M", "N", "P")) {
    X  <- get(nm)
    ir <- sapply(seq_len(ncol(X)), function(j) cor(X[, j], rowSums(X[, -j])))
    cat(sprintf("  %s: %s\n", nm,
        paste(sprintf("%s=%.2f", names(X), ir), collapse = "  ")))
}

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation from published alpha: %.4f (tolerance %.3f)\n", worst, TOL))

cat("Note: this pins subscale MEMBERSHIP (which nine codes form each block) and the\n",
    "five reverse-keyed POSITIONS exactly. It does NOT distinguish the non-reversed\n",
    "items within a block from one another -- e.g. nothing here would break if the\n",
    "text of DT_2 and DT_3 were swapped. That is why the recorded status is PARTIAL.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
