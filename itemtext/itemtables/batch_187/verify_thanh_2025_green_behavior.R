# verify_thanh_2025_green_behavior.R
#
# Claim: live items EGB1..EGB8 are S1 Appendix (journal.pone.0320053.s001) items
# "Employee green behavior 1".."Employee green behavior 8", in that order.
# The IRW code IS the S1 File xlsx column header (data/thanh_2025_green_behavior.py
# keeps columns matching ^EGB\d+$ and melts with var_name='item'), but the xlsx has
# no labels, so the code->wording tie rests on the appendix numbering (paper_explicit).
#
# Published values to test against, article Table 2 (t002, image):
#   - retained EGB items, listed in appendix order 1-5, outer loadings
#     .774 / .880 / .831 / .832 / .758 ; alpha .874
#   - the text: "of the original 30 measurement items, only 22 met the factor
#     loading score threshold of 0.5" -> appendix items 6, 7, 8 were dropped.
#
# Predictions if the mapping is right:
#   (a) EGB1-5 are the coherent block and EGB6-8 load < 0.5 on it;
#   (b) alpha(EGB1-5) reproduces .874;
#   (c) item-construct correlations for EGB1-5 reproduce the published loadings
#       in order (approximation: correlation with the standardised sum of EGB1-5;
#       SmartPLS mode-A weights differ slightly, so tolerance 0.02).
# What this does NOT establish: EGB3 vs EGB4 (published .831 vs .832 -- a swap also
# fits), and the order among EGB6/7/8 (all three are uncorrelated noise-like columns
# that carry no signal to tell them apart). Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "thanh_2025_green_behavior"
PUB_LOAD <- c(EGB1 = .774, EGB2 = .880, EGB3 = .831, EGB4 = .832, EGB5 = .758)
PUB_ALPHA <- .874
TOL <- 0.02

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[complete.cases(w[, paste0("EGB", 1:8)]), ]
cat("complete cases:", nrow(w), "\n\n")

ret <- paste0("EGB", 1:5)
z <- scale(w[, ret])
comp <- rowSums(z)
load_all <- sapply(paste0("EGB", 1:8), function(i) cor(w[[i]], comp))

alpha <- function(x) { k <- ncol(x); k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x))) }
a5 <- alpha(w[, ret]); a8 <- alpha(w[, paste0("EGB", 1:8)])

cat(sprintf("%-5s %9s %9s %8s\n", "item", "published", "observed", "diff"))
for (i in names(load_all)) {
  p <- if (i %in% names(PUB_LOAD)) PUB_LOAD[[i]] else NA
  cat(sprintf("%-5s %9s %9.3f %8s\n", i, ifelse(is.na(p), "dropped", sprintf("%.3f", p)),
              load_all[[i]], ifelse(is.na(p), "", sprintf("%.3f", load_all[[i]] - p))))
}
cat(sprintf("\nalpha EGB1-5: published %.3f, observed %.3f ; alpha EGB1-8 observed %.3f\n",
            PUB_ALPHA, a5, a8))

# Permutation test over the 5 retained items: how many assignments of the published
# loadings to EGB1-5 fit within TOL, and is the identity the best fit?
perms <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:5)
dev <- sapply(P, function(p) max(abs(load_all[ret] - PUB_LOAD[p])))
ident <- max(abs(load_all[ret] - PUB_LOAD))
ok_perms <- P[dev <= TOL]
cat(sprintf("identity max |dev| = %.3f ; best of 120 permutations = %.3f\n", ident, min(dev)))
cat("permutations within tolerance:",
    paste(sapply(ok_perms, function(p) paste0("(", paste(p, collapse = ","), ")")), collapse = " "), "\n")

max_r_678 <- max(abs(cor(w[, paste0("EGB", 6:8)], w[, ret])))
cat(sprintf("max |r| of EGB6-8 with any of EGB1-5: %.3f\n", max_r_678))

pass <- ident <= TOL &&
  abs(a5 - PUB_ALPHA) < 0.002 &&
  all(load_all[ret] > 0.5) && all(abs(load_all[paste0("EGB", 6:8)]) < 0.5) &&
  all(sapply(ok_perms, function(p) all(p[c(1, 2, 5)] == c(1, 2, 5))))
cat("Not established: EGB3 vs EGB4 (published .831/.832), order within EGB6-8.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
