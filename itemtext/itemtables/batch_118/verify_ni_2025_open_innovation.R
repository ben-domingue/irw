# verify_ni_2025_open_innovation.R
#
# CLAIM UNDER TEST: the wording shipped for item code OI1-1..OI1-5, OI2-1..OI2-4
# is, in that order, the paper's own enumeration (1)..(9) of the nine open
# innovation behaviour items (Ni et al. 2025, PLOS ONE 20(7) e0326490,
# section 3.2 item (3)).
#
# The falsifiable prediction: the paper's Table 3 (t003, an image-only table)
# prints a principal-component factor loading for every one of the 24
# questionnaire items under generic codes PI-1..PI-24, with PI-16..PI-24 being
# the nine open innovation items in questionnaire order. If the shipped order
# were permuted in any way, the loadings computed from the live table would
# land on the wrong published rows. The nine published values are all distinct
# (0.714 .. 0.870), so this pins EVERY item, not just a block.
#
# The loading is the first unrotated principal component of the 9x9 item
# correlation matrix, scaled by sqrt(eigenvalue) -- the "principal component
# method" the paper names in section 4.1.

suppressMessages(library(irw))
TABLE <- "ni_2025_open_innovation"
ITEMS <- c("OI1-1","OI1-2","OI1-3","OI1-4","OI1-5","OI2-1","OI2-2","OI2-3","OI2-4")

# --- published values, hard-coded from Table 3 (t003 PNG), rows PI-16..PI-24 ---
PUB_LOADING <- c(0.841, 0.865, 0.850, 0.870, 0.843, 0.864, 0.834, 0.714, 0.804)
PUB_ALPHA   <- 0.944   # Table 3, "Open innovation behavior of SMEs"
PUB_MEAN    <- 3.3131  # section 4.2, scale mean over all 9 items
TOL         <- 0.005

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, ITEMS]
w <- w[complete.cases(w), ]
cat("respondents used:", nrow(w), "\n\n")

R  <- cor(w)
e  <- eigen(R)
ld <- e$vectors[, 1] * sqrt(e$values[1])
if (sum(ld) < 0) ld <- -ld

cat(sprintf("%-8s %10s %10s %9s\n", "item", "published", "observed", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-8s %10.3f %10.3f %9.4f\n",
                ITEMS[i], PUB_LOADING[i], ld[i], ld[i] - PUB_LOADING[i]))
worst <- max(abs(ld - PUB_LOADING))
cat(sprintf("\nlargest loading deviation: %.4f (tolerance %.3f)\n", worst, TOL))

# Rank agreement -- a permutation of the shipped order would break this even if
# the loadings were close in absolute value.
rho <- cor(ld, PUB_LOADING, method = "spearman")
cat(sprintf("Spearman rank correlation of the 9 loadings: %.3f\n", rho))

# Corroborating scale-level statistics.
k <- ncol(w)
alpha <- (k/(k-1)) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
cat(sprintf("Cronbach's alpha: published %.3f, observed %.3f\n", PUB_ALPHA, alpha))
cat(sprintf("scale mean:       published %.4f, observed %.4f\n",
            PUB_MEAN, mean(as.matrix(w))))

cat("\nWhat this does NOT establish: it fixes each item code to its ordinal\n",
    "position in the paper's numbering of this scale. That the prose list (1)..(9)\n",
    "in section 3.2 runs in the same order as Table 3's PI-16..PI-24 is the\n",
    "paper's own single enumeration of one instrument; it is corroborated by the\n",
    "content split -- items (1)-(5) are inbound and carry the OI1 prefix (5 items),\n",
    "(6)-(9) are outbound and carry the OI2 prefix (4 items) -- and by the same\n",
    "block/prefix agreement in the sibling relationship-network scale (SN1 = the\n",
    "four intra-department items, SN2 = the four inter-firm items).\n", sep = "")

ok <- worst <= TOL && abs(rho - 1) < 1e-9
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
