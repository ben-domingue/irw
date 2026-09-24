# verify_arzamoncunill_2023_epq_admin.R -- Step 5b mapping check, batch_379.
#
# Claim: E-code -> item text follows supplement S5 (item number -> descriptor), and the
# 14 retained items' Spanish (Appendix S3) is tied to its descriptor by content, in the
# same order as the paper's Table 3. Falsifiable predictions checked against live data:
#  (1) Paper Table 3 (varimax PCA, 5 components, 14 retained admin items) is reproduced
#      item by item, and each live item's loading row is closest to the published row of
#      the descriptor we assigned it, out of all 14 published rows (distinguishes every
#      retained item from every other).
#  (2) The paper's step-1 PCA over all 21 admin items flags exactly two "issuance of
#      routine documents" items (range 0.434-0.627) and two "billing and accounting" items
#      (0.416-0.621) as cross-loading >0.40 -> should be S5's E5/E6 and E45/E46.
#  (3) The paper's step-3 correlations (0.610/0.556 and 0.541/0.501 with Data security vs
#      Issuance of routine documents) for the two items dropped last.
# Does NOT establish: which of E5/E6 or E45/E46 is which descriptor (pairs only), or E38's
# descriptor beyond its being one of the step-3 pair. E37/E39 are shipped with blank
# item_text because (3) plus the step-2 result contradict S5's subtheme labels for them.
suppressMessages({library(irw); library(psych)})
TABLE <- "arzamoncunill_2023_epq_admin"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
ok <- TRUE

# ---- (1) Table 3 loadings. Columns: 1 billing, 2 documents, 3 security, 4 marketing, 5 stock
pub <- rbind(
  E7  = c(0.186, 0.859, 0.217, 0.145, 0.079),  # Templates for common documents
  E8  = c(0.224, 0.829, 0.211, 0.116, 0.076),  # Automate the issuance of routine documents
  E9  = c(0.059, 0.594, 0.332, 0.105, 0.246),  # Easily fill in and sign documents
  E35 = c(0.229, 0.329, 0.779, 0.077, 0.118),  # Saving and backup copies
  E36 = c(0.302, 0.257, 0.757, 0.099, 0.069),  # Security measures against computer threats
  E34 = c(0.019, 0.145, 0.756, 0.214, 0.203),  # Configuration of users and access permissions
  E43 = c(0.843, 0.197, 0.194, 0.172, 0.185),  # Fees configuration
  E44 = c(0.807, 0.082, 0.121, 0.239, 0.075),  # Flexibility in the application of fees
  E42 = c(0.723, 0.279, 0.191, 0.177, 0.314),  # Allow different payment methods
  E29 = c(0.252, 0.138, 0.196, 0.811, 0.060),  # Repository of standard messages
  E30 = c(0.094, -0.049, 0.205, 0.752, 0.287), # Allows mass mailings of communications
  E28 = c(0.235, 0.349, -0.016, 0.736, -0.021),# Links to external communication apps
  E47 = c(0.202, 0.145, 0.143, 0.117, 0.907),  # Stock reports
  E48 = c(0.189, 0.131, 0.170, 0.127, 0.901))  # Notifications to replenish consumables
it <- rownames(pub)
p <- principal(w[, it], nfactors = 5, rotate = "varimax")
L <- unclass(p$loadings)[it, ]
# align observed components to published columns by congruence
cong <- abs(t(L) %*% pub) / sqrt(outer(colSums(L^2), colSums(pub^2)))
perm <- apply(cong, 2, which.max); stopifnot(length(unique(perm)) == 5)
L <- L[, perm]; L <- sweep(L, 2, sign(colSums(L * pub)), `*`)
D <- as.matrix(dist(rbind(L, pub)))[1:14, 15:28]  # observed item x published row
cat(sprintf("%-4s %8s %8s %-5s %8s\n", "item", "own_dist", "next", "near", "maxdiff"))
for (i in seq_along(it)) {
  own <- D[i, i]; nxt <- min(D[i, -i]); near <- it[which.min(D[i, ])]
  cat(sprintf("%-4s %8.3f %8.3f %-5s %8.3f\n", it[i], own, nxt, near, max(abs(L[i, ] - pub[i, ]))))
  if (near != it[i]) ok <- FALSE
}
cat(sprintf("largest single-loading deviation: %.3f\n", max(abs(L - pub))))
if (max(abs(L - pub)) > 0.04) ok <- FALSE  # residuals: paper n and missing-data handling unstated (2 ids incomplete)

# ---- (2) step-1 PCA, all 21 items, 5 components
it21 <- c("E5","E6","E7","E8","E9","E28","E29","E30","E34","E35","E36","E37","E38","E39",
          "E42","E43","E44","E45","E46","E47","E48")
L21 <- unclass(principal(w[, it21], nfactors = 5, rotate = "varimax")$loadings)
top2 <- t(apply(abs(L21), 1, function(v) sort(v, decreasing = TRUE)[1:2]))
cross <- rownames(top2)[top2[, 2] > 0.40]
cat("\nstep 1 cross-loaders (>0.40 on 2 comps):\n"); print(round(top2[cross, ], 3))
cat(sprintf("E37 second loading (not flagged by paper): %.4f\n", top2["E37", 2]))
rng <- function(x) range(top2[x, ])
cat(sprintf("E5/E6 range %.3f-%.3f (paper 0.434-0.627); E45/E46 range %.3f-%.3f (paper 0.416-0.621)\n",
            rng(c("E5","E6"))[1], rng(c("E5","E6"))[2], rng(c("E45","E46"))[1], rng(c("E45","E46"))[2]))
if (!all(c("E5","E6","E45","E46") %in% cross)) ok <- FALSE
if (max(abs(c(rng(c("E5","E6")), rng(c("E45","E46"))) - c(0.434, 0.627, 0.416, 0.621))) > 0.01) ok <- FALSE

# ---- (3) step-3 correlations with scale sums
sec  <- rowSums(w[, c("E34","E35","E36")]); docs <- rowSums(w[, c("E7","E8","E9")])
r <- sapply(c("E37","E38","E39"), function(i) c(sec = cor(w[[i]], sec, use = "pair"),
                                                 docs = cor(w[[i]], docs, use = "pair")))
cat("\nstep 3 correlations (paper: 0.610/0.556 and 0.541/0.501):\n"); print(round(r, 3))
if (max(abs(c(r[, "E38"], r[, "E39"]) - c(0.610, 0.556, 0.541, 0.501))) > 0.01) ok <- FALSE
cat("=> step-3 pair is E38+E39 (the paper calls both 'interoperability'), while S5 files E37\n",
    "   under interoperability and E39 under data security: E37/E39 descriptors unresolved,\n",
    "   shipped with blank item_text.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
