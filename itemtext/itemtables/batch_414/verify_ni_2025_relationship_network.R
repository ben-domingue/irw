# verify_ni_2025_relationship_network.R
#
# CLAIM UNDER TEST: the wording shipped for SN1-1..SN1-4, SN2-1..SN2-4 is, in that
# order, the paper's enumeration (1)..(8) of the eight relationship-network items
# (Ni & Wang 2025, PLOS ONE 20(6) e0326490, section 3.2 paragraph (1)).
#
# Falsifiable prediction: Table 3 (t003, image-only) prints a principal-component
# loading per questionnaire item; PI-1..PI-8 are this scale's eight items. The
# loading is the first unrotated principal component of the 8x8 item correlation
# matrix scaled by sqrt(eigenvalue) (the "principal component method", sec. 4.1).
# Published values are rounded to 3dp, so the correct assignment must deviate by
# <= 0.0005 on every item. All 40320 permutations of the codes are scored, to show
# how many assignments are consistent with the published row order.
#
# A second, content-based check: items (1)-(4) are about members of "my department"
# and items (5)-(8) about partner firms in collaborative agreements. A two-component
# varimax solution must split SN1-* from SN2-* on those lines.

suppressMessages(library(irw))
TABLE <- "ni_2025_relationship_network"
ITEMS <- c("SN1-1","SN1-2","SN1-3","SN1-4","SN2-1","SN2-2","SN2-3","SN2-4")

PUB_LOADING <- c(0.827, 0.883, 0.873, 0.871, 0.850, 0.845, 0.862, 0.859)  # Table 3, PI-1..PI-8
PUB_ALPHA   <- 0.949    # Table 3, "The relationship network"
PUB_MEAN    <- 3.9328   # section 4.2 / Table 4
TOL         <- 0.0005 + 1e-9  # half a unit in the 3rd decimal, plus float slack

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, ITEMS]; w <- w[complete.cases(w), ]
cat("respondents used:", nrow(w), "\n\n")

R  <- cor(w); e <- eigen(R)
ld <- e$vectors[, 1] * sqrt(e$values[1]); if (sum(ld) < 0) ld <- -ld

cat(sprintf("%-8s %6s %10s %10s %9s\n", "item", "row", "published", "observed", "diff"))
for (i in seq_along(ITEMS))
  cat(sprintf("%-8s %6s %10.3f %10.4f %9.4f\n", ITEMS[i], paste0("PI-", i),
              PUB_LOADING[i], ld[i], ld[i] - PUB_LOADING[i]))
worst <- max(abs(ld - PUB_LOADING))
cat(sprintf("\nlargest loading deviation: %.4f (rounding tolerance %.4f)\n", worst, TOL))
cat("observed loadings rounded to 3dp equal the published values on all 8 items:", all(round(ld, 3) == PUB_LOADING), "\n")

perms <- function(v) if (length(v) == 1) matrix(v, 1) else
  do.call(rbind, lapply(seq_along(v), function(i) cbind(v[i], perms(v[-i]))))
P   <- perms(1:8)
dev <- apply(P, 1, function(p) max(abs(ld[p] - PUB_LOADING)))
ident <- which(apply(P, 1, function(p) all(p == 1:8)))
n_ok  <- sum(dev <= TOL)
cat(sprintf("permutations within rounding tolerance: %d of %d (identity dev %.4f; best non-identity dev %.4f)\n",
            n_ok, nrow(P), dev[ident], min(dev[-ident])))

k <- ncol(w)
alpha <- (k/(k-1)) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
cat(sprintf("Cronbach's alpha: published %.3f, observed %.4f\n", PUB_ALPHA, alpha))
cat(sprintf("scale mean:       published %.4f, observed %.4f\n", PUB_MEAN, mean(as.matrix(w))))

vm <- unclass(varimax(e$vectors[, 1:2] %*% diag(sqrt(e$values[1:2])))$loadings)
dom <- apply(abs(vm), 1, which.max)
cat("\nvarimax 2-component dominant factor:", paste(ITEMS, dom, sep = "=", collapse = " "), "\n")
block_ok <- length(unique(dom[1:4])) == 1 && length(unique(dom[5:8])) == 1 && dom[1] != dom[5]
cat("department block (SN1) vs partner-firm block (SN2) separate:", block_ok, "\n")

cat("\nWhat this does NOT establish: it pins each CODE to one PI row of Table 3\n",
    "(and only the identity assignment fits within rounding), plus the two content\n",
    "blocks. That the prose list (1)..(8) runs in the same order as PI-1..PI-8\n",
    "within each block is not keyed by any source.\n", sep = "")

ok <- worst <= TOL && n_ok == 1 && dev[ident] <= TOL && block_ok &&
      abs(alpha - PUB_ALPHA) < 0.0005 && abs(mean(as.matrix(w)) - PUB_MEAN) < 0.00005
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
