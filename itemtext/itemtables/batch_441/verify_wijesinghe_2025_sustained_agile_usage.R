# verify_wijesinghe_2025_sustained_agile_usage.R
#
# Claim: live item codes SAU01..SAU08 carry the wording printed against the SAME
# codes in the paper's S1 Table (journal.pone.0316538.s002, "Questionnaire items").
# The response file (S1 Data) has no labels; its column headers are the codes
# SAU01..SAU08 and the processing script keeps them verbatim as `item`.
#
# The falsifiable prediction: the paper's Table 2 prints PLS outer loadings per
# item code (SAU01 .764 ... SAU08 .660) and CA = 0.890. If the live data's
# columns were permuted relative to the paper's codes, the per-item loading
# profile computed from the live data would not track the published one.
# Loadings are approximated here by each item's correlation with the
# unit-weighted SAU composite and by first-principal-component loadings (the
# paper's PLS composite also includes inner-model weighting, so exact equality
# is not expected -- order/profile is the signal).

suppressMessages(library(irw))
TABLE <- "wijesinghe_2025_sustained_agile_usage"
ITEMS <- sprintf("SAU%02d", 1:8)
PUBLISHED <- c(0.764, 0.852, 0.827, 0.763, 0.799, 0.709, 0.634, 0.660)
PUB_CA <- 0.890

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, ITEMS])
X <- X[complete.cases(X), ]
cat("complete cases:", nrow(X), "\n")

comp <- rowSums(X)
r_tot <- apply(X, 2, function(v) cor(v, comp))
pc <- prcomp(X, scale. = TRUE)
pcl <- abs(pc$rotation[, 1] * pc$sdev[1])
k <- ncol(X)
ca <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(comp))

cat(sprintf("%-6s %9s %9s %9s %6s\n", "item", "published", "r_total", "PC1", "mean"))
for (i in seq_len(k))
  cat(sprintf("%-6s %9.3f %9.3f %9.3f %6.2f\n", ITEMS[i], PUBLISHED[i],
              r_tot[i], pcl[i], mean(X[, i])))
rho_tot <- cor(PUBLISHED, r_tot, method = "spearman")
rho_pc  <- cor(PUBLISHED, pcl, method = "spearman")
maxdiff <- max(abs(pcl - PUBLISHED))
cat(sprintf("\nCronbach alpha: live %.3f vs published %.3f\n", ca, PUB_CA))
cat(sprintf("Spearman(published, r_total) = %.3f; Spearman(published, PC1) = %.3f\n",
            rho_tot, rho_pc))
cat(sprintf("max |PC1 loading - published| = %.3f\n", maxdiff))
cat("Does NOT establish: loadings on a one-factor scale separate items only by\n",
    "profile; near-tied pairs (SAU01 .764 vs SAU04 .763) are not distinguished by\n",
    "this route. The code-to-text tie itself is the S1 Table printing each item\n",
    "against the very code used as the data column header.\n", sep = "")

ok <- abs(ca - PUB_CA) <= 0.01 && rho_pc >= 0.8 && maxdiff <= 0.06
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
