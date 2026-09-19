# verify_gan_2015_ucla_loneliness.R
#
# Claim under test: the live item codes UCLA1..UCLA8 carry the canonical ULS-8
# (Hays & DiMatteo, 1987) numbering, the stored resp values are the SCORED
# values (i.e. the two reverse-worded items were already reversed before
# storage), and the reverse-worded pair is {UCLA3, UCLA6} -- which is what
# licenses the flipped option_text (1 = Always ... 4 = Never) shipped for those
# two items only.
#
# Falsifiable predictions, from the source paper (PLOS ONE 10(9):e0137176):
#   P1  Cronbach's alpha of the eight columns AS STORED = .71 (paper, Measurements).
#   P2  no item has a negative item-rest correlation (all stored in the
#       loneliness direction; a raw positively-worded item would be negative).
#   P3  the paper says "Two of the eight items were reverse-coded"; after
#       reversal those two carry a residual method factor, so the pair whose
#       re-flipping does LEAST damage to alpha should be exactly {3, 6}, and
#       they should be each other's strongest correlate.
#
# What this does NOT establish: which of the six negatively-worded ULS-8 stems
# belongs to each of UCLA1, UCLA2, UCLA4, UCLA5, UCLA7, UCLA8, nor which of
# UCLA3 / UCLA6 is "I am an outgoing person" vs "I can find companionship when
# I want it". Those rest on the canonical ULS-8 numbering, not on these numbers.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE      <- "gan_2015_ucla_loneliness"
PUB_ALPHA  <- 0.71          # paper, Measurements: "Cronbach's alpha ... is .71"
TOL_ALPHA  <- 0.005
REV_PAIR   <- c(3, 6)       # canonical ULS-8 reverse-scored items

d <- irw::irw_fetch(TABLE)
items <- paste0("UCLA", 1:8)
w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, items])
X <- X[complete.cases(X), , drop = FALSE]
cat(sprintf("respondents with complete ULS-8 data: %d\n\n", nrow(X)))

alpha <- function(M) {
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}

# ---- P1 -------------------------------------------------------------------
a0 <- alpha(X)
cat(sprintf("P1  alpha as stored = %.4f   published = %.2f   diff = %.4f\n\n",
            a0, PUB_ALPHA, a0 - PUB_ALPHA))
p1 <- abs(a0 - PUB_ALPHA) <= TOL_ALPHA

# ---- P2 -------------------------------------------------------------------
tot <- rowSums(X)
ir  <- sapply(items, function(v) cor(X[, v], tot - X[, v]))
cat("P2  item-rest correlations (stored direction):\n")
for (v in items) cat(sprintf("      %-6s %6.3f\n", v, ir[v]))
cat(sprintf("    minimum = %.3f (%s)\n\n", min(ir), items[which.min(ir)]))
p2 <- all(ir > 0)

# ---- P3 -------------------------------------------------------------------
C <- cor(X)
cat("P3a strongest correlate of each item:\n")
for (v in items) {
    s <- C[v, setdiff(items, v)]
    cat(sprintf("      %-6s -> %-6s r = %.3f\n", v, names(which.max(s)), max(s)))
}
mutual <- names(which.max(C["UCLA3", setdiff(items, "UCLA3")])) == "UCLA6" &&
          names(which.max(C["UCLA6", setdiff(items, "UCLA6")])) == "UCLA3"
cat(sprintf("    UCLA3 and UCLA6 are each other's strongest correlate: %s (r = %.3f)\n\n",
            mutual, C["UCLA3", "UCLA6"]))

res <- do.call(rbind, lapply(combn(8, 2, simplify = FALSE), function(p) {
    Y <- X; Y[, p] <- 5 - Y[, p]
    data.frame(a = p[1], b = p[2], alpha = alpha(Y))
}))
res <- res[order(-res$alpha), ]
cat("P3b alpha after re-flipping each candidate reverse pair (top 4 of 28):\n")
for (i in 1:4)
    cat(sprintf("      {%d,%d}  %.4f\n", res$a[i], res$b[i], res$alpha[i]))
cat(sprintf("      ...\n      worst {%d,%d}  %.4f\n\n",
            res$a[nrow(res)], res$b[nrow(res)], res$alpha[nrow(res)]))
best <- c(res$a[1], res$b[1])
p3 <- mutual && identical(as.integer(best), as.integer(REV_PAIR))

cat(sprintf("P1 alpha reproduces published .71 : %s\n", p1))
cat(sprintf("P2 all item-rest correlations > 0 : %s\n", p2))
cat(sprintf("P3 reverse pair identified as {3,6}: %s\n", p3))
cat("\nNot established by this script: the stem assigned to each of UCLA1/2/4/5/7/8,\n",
    "and which of UCLA3 / UCLA6 is which. Those come from canonical ULS-8 numbering.\n", sep = "")

cat(if (p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
