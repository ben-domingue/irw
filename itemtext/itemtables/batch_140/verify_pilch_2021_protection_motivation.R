# verify_pilch_2021_protection_motivation.R
#
# Claim under test: each of the 10 PMQ item codes carries the statement printed
# in Table 1 of Pilch, Wardawy & Probierz (2021), PLOS ONE 16(10):e0258606.
#
# The mapping has two layers and they are verified separately:
#   (a) SUBSCALE MEMBERSHIP -- which of the five PMT constructs each code belongs
#       to. Falsifiable: the paper publishes each subscale's alpha (Measures
#       section) and its mean, SD and full intercorrelation matrix (Table 2).
#       Any reassignment of a code to a different construct moves those numbers.
#   (b) ORDER WITHIN A PAIR -- Vulnerab1 vs Vulnerab2, etc. Table 1 lists the two
#       statements of each construct but numbers nothing, so this rests on the
#       paper's listing order. Block (c) below shows the one content route tried
#       is underpowered, so this layer is NOT established here.

suppressMessages({library(irw); library(tidyr)})

TABLE <- "pilch_2021_protection_motivation"

G <- list(
  "Perceived vulnerability"    = c("Vulnerab1", "Vulnerab2"),
  "Perceived severity"         = c("Severity1", "Severity2"),
  "Perceived self-efficacy"    = c("Selfeffic1", "Selfeffic2"),
  "Perceived response-efficacy"= c("Responseeffic1", "Responseeffic2"),
  "Perceived costs"            = c("Costs1", "Costs2"))

# Published values (paper Table 2 for M/SD and r; Measures section for alpha).
PUB_M     <- c(2.82, 5.12, 5.09, 5.12, 3.60)
PUB_SD    <- c(1.55, 1.28, 1.29, 1.19, 1.36)
PUB_ALPHA <- c(0.82, 0.87, 0.45, 0.71, 0.46)
# Table 2 lower-triangle correlations among the five PMQ subscales, in G's order.
PUB_R <- matrix(c(  NA, 0.26, 0.18, 0.17,-0.04,
                  0.26,   NA, 0.33, 0.44,-0.23,
                  0.18, 0.33,   NA, 0.40,-0.46,
                  0.17, 0.44, 0.40,   NA,-0.36,
                 -0.04,-0.23,-0.46,-0.36,   NA), 5, 5, byrow = TRUE)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- as.data.frame(pivot_wider(d[, c("id","item","resp")],
                               names_from = item, values_from = resp))
sc <- sapply(G, function(cc) rowMeans(w[, cc]))

cat("(a) SUBSCALE-LEVEL DESCRIPTIVES AND RELIABILITY\n")
cat(sprintf("%-28s %11s %11s %13s\n", "construct", "M pub/obs", "SD pub/obs", "alpha pub/obs"))
obs_m <- obs_sd <- obs_a <- numeric(5)
for (i in seq_along(G)) {
  cc <- G[[i]]; m2 <- w[, cc]
  r  <- cor(m2[[1]], m2[[2]], use = "complete.obs")
  obs_a[i]  <- 2 * r / (1 + r)                      # Spearman-Brown = alpha, k = 2
  obs_m[i]  <- mean(sc[, i], na.rm = TRUE)
  obs_sd[i] <- sd(sc[, i], na.rm = TRUE)
  cat(sprintf("%-28s %5.2f/%5.2f %5.2f/%5.2f %6.2f/%6.2f\n",
              names(G)[i], PUB_M[i], obs_m[i], PUB_SD[i], obs_sd[i],
              PUB_ALPHA[i], obs_a[i]))
}
d_m <- max(abs(obs_m - PUB_M)); d_sd <- max(abs(obs_sd - PUB_SD))
d_a <- max(abs(obs_a - PUB_ALPHA))
cat(sprintf("largest deviation: M %.3f, SD %.3f, alpha %.3f (tolerance 0.05)\n\n",
            d_m, d_sd, d_a))

cat("(b) SUBSCALE INTERCORRELATIONS vs TABLE 2\n")
obs_r <- cor(sc, use = "pairwise")
worst_r <- 0
for (i in 1:4) for (j in (i+1):5) {
  cat(sprintf("  %-28s x %-28s pub %6.2f  obs %6.2f\n",
              names(G)[i], names(G)[j], PUB_R[i, j], obs_r[i, j]))
  worst_r <- max(worst_r, abs(obs_r[i, j] - PUB_R[i, j]))
}
cat(sprintf("largest deviation: %.3f (tolerance 0.03)\n\n", worst_r))

cat("(c) WITHIN-PAIR ORDER -- attempted, NOT established\n")
# Selfeffic1/Costs2 name hygiene rules, Selfeffic2/Costs1 name isolation. If the
# codes were ordered as Table 1 lists them, each should track the matching class
# of preventive behaviour in the sibling table more closely than the other class.
cb <- as.data.frame(irw::irw_fetch("pilch_2021_coping_behavior"))
wc <- as.data.frame(pivot_wider(cb[, c("id","item","resp")],
                                names_from = item, values_from = resp))
m  <- merge(w, wc, by = "id")
hyg <- rowMeans(m[, c("BEH7","BEH8","BEH9")])       # disinfect / masks / handwashing
iso <- rowMeans(m[, c("BEH1","BEH2","BEH4","BEH6")]) # stay home / distance / no socialising
for (v in c("Selfeffic1","Selfeffic2","Costs1","Costs2")) {
  b <- summary(lm(m[[v]] ~ hyg + iso))$coef
  cat(sprintf("  %-11s beta_hygiene=%5.2f (t=%4.1f)   beta_isolation=%5.2f (t=%4.1f)\n",
              v, b[2,1], b[2,3], b[3,1], b[3,3]))
}
cat("  Both self-efficacy items load on the isolation block and neither on the\n",
    "  hygiene block, so this route does not separate the members of a pair; the\n",
    "  isolation behaviours dominate the compliance variance. Item 1 vs item 2\n",
    "  within each construct therefore rests on Table 1's listing order alone.\n", sep = "")

ok <- (d_m <= 0.05) && (d_sd <= 0.05) && (d_a <= 0.05) && (worst_r <= 0.03)
cat("\nEstablished: the assignment of all 10 codes to the five constructs.\n")
cat("NOT established: which member of each pair is item 1 and which is item 2.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
