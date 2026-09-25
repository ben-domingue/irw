# verify_ni_2025_knowledge_transfer.R
#
# CLAIM UNDER TEST: item codes KT-1..KT-4 carry, in that order, the paper's
# enumeration (1)..(4) of the knowledge-transfer items (Ni & Wang 2025, PLOS ONE
# e0326490, section 3.2 paragraph (2)).
#
# Falsifiable prediction: Table 3 (t003, image-only) prints a principal-component
# loading per questionnaire item; PI-12..PI-15 are the four knowledge-transfer
# items (0.919 / 0.925 / 0.951 / 0.931). The loading is the first unrotated
# principal component of the 4x4 item correlation matrix, scaled by
# sqrt(eigenvalue). All 24 assignments of codes to published rows are scored;
# the shipped order must be the unique best fit.

suppressMessages(library(irw))
TABLE <- "ni_2025_knowledge_transfer"
ITEMS <- c("KT-1","KT-2","KT-3","KT-4")
PUB_LOADING <- c(0.919, 0.925, 0.951, 0.931)   # Table 3, PI-12..PI-15
PUB_ALPHA   <- 0.949                            # Table 3
PUB_MEAN    <- 3.2409                           # section 4.2 / Table 4
TOL         <- 0.005

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[complete.cases(w[, ITEMS]), ITEMS]
cat("respondents used:", nrow(w), "\n\n")

R  <- cor(w)
e  <- eigen(R)
ld <- e$vectors[, 1] * sqrt(e$values[1])
if (sum(ld) < 0) ld <- -ld

cat(sprintf("%-6s %10s %10s %9s\n", "item", "published", "observed", "diff"))
for (i in seq_along(ITEMS))
  cat(sprintf("%-6s %10.3f %10.4f %9.4f\n", ITEMS[i], PUB_LOADING[i], ld[i],
              ld[i] - PUB_LOADING[i]))
worst <- max(abs(ld - PUB_LOADING))
cat(sprintf("\nlargest loading deviation: %.4f (tolerance %.3f)\n", worst, TOL))

perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:4)
score <- sapply(P, function(p) sum(abs(ld[p] - PUB_LOADING)))
names(score) <- sapply(P, function(p) paste(ITEMS[p], collapse = ","))
score <- sort(score)
cat("\nsum |observed - published| over all 24 assignments (best 6):\n")
print(round(head(score, 6), 4))
ident <- paste(ITEMS, collapse = ",")
unique_best <- names(score)[1] == ident && score[2] - score[1] > 0.005

k <- ncol(w)
alpha <- (k/(k-1)) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
cat(sprintf("\nCronbach's alpha: published %.3f, observed %.4f\n", PUB_ALPHA, alpha))
cat(sprintf("scale mean:       published %.4f, observed %.4f\n", PUB_MEAN, mean(as.matrix(w))))

cat("\nWhat this does NOT establish: it pins each code to one of Table 3's PI-12..PI-15\n",
    "rows. That the prose list (1)..(4) runs in the same order as PI-12..PI-15 is an\n",
    "assumption no source keys. Content offers no independent check: items (1),(3) are\n",
    "first-person sharing and (2),(4) are firm-level cooperation, but the observed\n",
    "correlations do not split that way (r13 and r24 are not the largest pair).\n", sep = "")
cat(sprintf("r(KT-1,KT-3)=%.3f  r(KT-2,KT-4)=%.3f  r(KT-3,KT-4)=%.3f\n",
            R[1,3], R[2,4], R[3,4]))

ok <- worst <= TOL && unique_best && abs(alpha - PUB_ALPHA) < 0.001 &&
      abs(mean(as.matrix(w)) - PUB_MEAN) < 0.0001
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
