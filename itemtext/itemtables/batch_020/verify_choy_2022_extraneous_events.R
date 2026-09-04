# verify_choy_2022_extraneous_events.R
#
# Claim under test: the four item_text strings shipped for Extraneous1..Extraneous4
# are attached to the right codes. The tie has two links:
#   (a) paper Table 4 prints a standardised factor loading for "Item 1".."Item 4" of
#       the Extraneous factor -- a falsifiable prediction about which live column is
#       which NUMBER;
#   (b) paper Table 1 lists the four item wordings, in order, with no numbering --
#       so the text->number link is presentation order (mapping_basis=paper_order).
# This script tests (a). It cannot test (b); see the note printed at the end.
#
# Published values, Choy & Yeung (2022) PLOS ONE 17(12):e0279411, Table 4,
# "Extran" column: loadings .67 / .76 / .83 / .85, alpha .86, composite M 4.31 (1.06).

suppressMessages(library(irw))
suppressMessages(library(lavaan))

TABLE <- "choy_2022_extraneous_events"
ITEMS <- paste0("Extraneous", 1:4)
PUB_LOAD  <- c(.67, .76, .83, .85)
PUB_ALPHA <- .86
PUB_M     <- 4.31
PUB_SD    <- 1.06
TOL_LOAD  <- 0.03

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, ITEMS]

fit <- lavaan::cfa(paste("E =~", paste(ITEMS, collapse = " + ")),
                   data = w, missing = "fiml")
obs <- as.numeric(lavaan::inspect(fit, "std")$lambda[ITEMS, 1])

cat(sprintf("%-12s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-12s %10.2f %10.2f %8.3f\n",
                ITEMS[i], PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
worst <- max(abs(obs - PUB_LOAD))
cat(sprintf("\nlargest loading deviation: %.3f (tolerance %.2f)\n", worst, TOL_LOAD))

# Corroborating scale-level numbers (do not discriminate items, but confirm the
# same 4 columns are the ones the paper analysed).
cc <- w[complete.cases(w), ]
comp <- rowMeans(cc)
k <- ncol(w)
alpha <- {
    cv <- cov(cc); k * (1 - sum(diag(cv)) / sum(cv)) / (k - 1)
}
cat(sprintf("composite mean %.3f (published %.2f), SD %.3f (published %.2f), alpha %.3f (published %.2f)\n",
            mean(comp), PUB_M, sd(comp), PUB_SD, alpha, PUB_ALPHA))

ok <- worst <= TOL_LOAD &&
      abs(mean(comp) - PUB_M) <= 0.05 &&
      abs(sd(comp) - PUB_SD) <= 0.05 &&
      abs(alpha - PUB_ALPHA) <= 0.02

cat("Note: this pins the live columns Extraneous1..4 to the paper's Item 1..4 numbering.\n",
    "It does NOT establish that Table 1's unnumbered list of four wordings is in item order,\n",
    "which is the remaining inference; and items 3 vs 4 differ by only .02 in published\n",
    "loading, so a 3<->4 swap is the weakest-separated case even for the part it does test.\n",
    sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
