# verify_ghanbari_2016_helma_access.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST
#   The live item codes access1..access11 are the columns of the PRE-FINAL 47-item
#   HELMA field-test form held in the paper's S3 File (.sav).  access1..access9 are
#   questionnaire items 1..9 of the published 44-item HELMA (S1 File English /
#   S2 File Persian); access10 and access11 are two of the three items dropped
#   during validation and their wording was never published (shipped blank).
#
#   The .sav item columns carry NO variable labels, so the code->text tie is an
#   inference.  What makes it falsifiable: the paper's Table 2 prints an 8-factor
#   varimax loading matrix for the 44 retained items, computed on all 47
#   (12.26/47 = 26.08%, the published explained variance).  Re-running that EFA on
#   the .sav gives each raw column an 8-vector that can be matched against the
#   published rows for items 1..9.
#
#   Independent second axis: Table 3's per-domain Cronbach alpha.  alpha is
#   order-invariant, so it pins BLOCK MEMBERSHIP (which raw columns became
#   self-efficacy vs access vs dropped) without using the loadings at all.
#
# WHAT THIS DOES NOT ESTABLISH
#   Nothing here recovers the wording of access10/access11 -- it only shows they
#   are the two columns with no counterpart in Table 2.  Nothing here checks the
#   option_text<->resp axis either; that comes from the .sav's own value labels
#   (1 = never ... 5 = always) and is data_labels, not inference.

suppressMessages(library(haven))

SAV_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0149202.s003"

# ---- Paper Table 2, rows for questionnaire items 1-9, in the paper's own factor
# order: 1 understanding, 2 communication, 3 reading, 4 appraisal, 5 access,
# 6 use, 7 self-efficacy, 8 numeracy.
PUB <- matrix(c(
  .109,.149,.201,.062,.011,.458,.521,-.099,
  .130,.110,.130,.111,.274,.044,.575,.039,
  .057,.126,.141,.080,.310,-.035,.578,.002,
  .203,.290,.004,-.016,.160,-.088,.499,.080,
  .098,.082,-.029,.059,.589,.260,.289,.097,
  .148,.067,-.187,.059,.549,.388,.151,.031,
  .027,.047,-.030,.078,.634,.092,.186,-.060,
  .082,.164,.154,.126,.598,.022,.177,-.043,
  .074,.208,.275,.063,.663,-.138,-.095,-.065),
  nrow = 9, byrow = TRUE)
rownames(PUB) <- paste0("q", 1:9)

PUB_EIGEN <- c(12.26, 2.72, 2.17, 2.08, 1.68, 1.54, 1.39, 1.26)   # Table 2 footer
PUB_ALPHA <- c(self_efficacy = 0.61, access = 0.71)               # Table 3

tmp <- file.path(tempdir(), "ghanbari_2016_helma_s3.sav")
if (!file.exists(tmp))
    utils::download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb",
                         headers = c("User-Agent" = "IRW-itemtext/1.0"))
d <- as.data.frame(haven::read_sav(tmp))

blocks <- c("access", "reading", "understand", "appraise", "use", "com", "num")
cols <- grep(paste0("^(", paste(blocks, collapse = "|"), ")[0-9]+$"), names(d), value = TRUE)
X <- d[stats::complete.cases(d[, cols]), cols]
cat(sprintf("S3 File: %d item columns, %d complete cases (paper analysed n = 582)\n\n",
            length(cols), nrow(X)))

## ---------- 1. reproduce the published EFA ----------
R <- stats::cor(X)
e <- eigen(R, symmetric = TRUE)
k <- 8
L0 <- e$vectors[, 1:k] %*% diag(sqrt(e$values[1:k]))
cat("unrotated eigenvalues vs paper Table 2 footer:\n")
cat(sprintf("  %-10s %s\n", "computed", paste(sprintf("%5.2f", e$values[1:k]), collapse = " ")))
cat(sprintf("  %-10s %s\n", "published", paste(sprintf("%5.2f", PUB_EIGEN), collapse = " ")))
eig_ok <- max(abs(e$values[1:k] - PUB_EIGEN)) < 0.06
cat(sprintf("  max |diff| = %.3f  -> %s\n\n", max(abs(e$values[1:k] - PUB_EIGEN)),
            if (eig_ok) "same analysis, same data" else "MISMATCH"))

vm <- stats::varimax(L0, normalize = TRUE)   # SPSS default: Kaiser normalisation
L <- unclass(vm$loadings)
ss <- colSums(L^2)
L <- L[, order(ss, decreasing = TRUE), drop = FALSE]
for (j in seq_len(k)) if (sum(L[, j]) < 0) L[, j] <- -L[, j]
rownames(L) <- cols

## ---------- 2. label the rotated factors ----------
# Six factors are named by the raw block that dominates them; this uses no
# information about the access block's internal ordering, which is what is on trial.
lab <- sapply(c("understand", "com", "reading", "appraise", "use", "num"), function(b) {
    rows <- grep(paste0("^", b, "[0-9]+$"), cols)
    which.max(colSums(L[rows, , drop = FALSE]^2))
})
rem <- setdiff(seq_len(k), lab)
acc <- paste0("access", 1:11)
dist_to_pub <- function(ord) {
    M <- L[acc, ord, drop = FALSE]
    outer(seq_len(9), seq_len(11), Vectorize(function(i, j) sqrt(sum((PUB[i, ] - M[j, ])^2))))
}
cand <- list(c(lab["understand"], lab["com"], lab["reading"], lab["appraise"],
               rem[1], lab["use"], rem[2], lab["num"]),
             c(lab["understand"], lab["com"], lab["reading"], lab["appraise"],
               rem[2], lab["use"], rem[1], lab["num"]))
costs <- sapply(cand, function(o) sum(apply(dist_to_pub(o), 1, min)))
cat(sprintf("two possible labellings of the residual access/self-efficacy pair: total cost %.3f vs %.3f\n",
            costs[1], costs[2]))
ord <- cand[[which.min(costs)]]
D <- dist_to_pub(ord)
dimnames(D) <- list(paste0("q", 1:9), acc)

## ---------- 3. the actual mapping test ----------
cat("\nEuclidean distance, published 8-loading vector vs recomputed vector\n")
cat(sprintf("%-4s %s\n", "", paste(sprintf("%8s", acc), collapse = "")))
for (i in 1:9) cat(sprintf("%-4s %s\n", rownames(D)[i], paste(sprintf("%8.3f", D[i, ]), collapse = "")))

nearest <- acc[apply(D, 1, which.min)]
runner  <- apply(D, 1, function(r) acc[order(r)[2]])
cat("\nnearest raw column for each published item (expected: the identity map)\n")
ok <- TRUE
for (i in 1:9) {
    exp_i <- paste0("access", i)
    hit <- nearest[i] == exp_i
    ok <- ok && hit
    cat(sprintf("  q%-2d -> %-9s d=%.3f   (runner-up %-9s d=%.3f)  %s\n",
                i, nearest[i], min(D[i, ]), runner[i], sort(D[i, ])[2],
                if (hit) "ok" else "*** WRONG ***"))
}
orphan <- !any(c("access10", "access11") %in% nearest)
cat(sprintf("\naccess10 / access11 are the nearest column for no published item: %s\n",
            if (orphan) "TRUE (consistent with both being dropped items)" else "FALSE"))

## ---------- 4. independent, order-free check: Table 3 alphas ----------
alpha <- function(M) { M <- as.matrix(M); kk <- ncol(M)
    kk/(kk-1) * (1 - sum(apply(M, 2, stats::var))/stats::var(rowSums(M))) }
a_se  <- alpha(X[, paste0("access", 1:4)])
a_acc <- alpha(X[, paste0("access", 5:9)])
cat(sprintf("\nCronbach alpha (order-free, pins block membership only)\n"))
cat(sprintf("  access1-4  = %.3f   paper 'self-efficacy' (4 items) = %.2f\n", a_se,  PUB_ALPHA["self_efficacy"]))
cat(sprintf("  access5-9  = %.3f   paper 'access'        (5 items) = %.2f\n", a_acc, PUB_ALPHA["access"]))
alpha_ok <- abs(a_se - 0.61) < 0.02 && abs(a_acc - 0.71) < 0.02

cat("\nWhat this does NOT establish: alpha fixes only which columns form each block,\n",
    "not the order inside it; the loading match is what orders them, and q5's margin\n",
    "over its runner-up is the narrowest in the table. The two are independent, and\n",
    "the wording of access10/access11 is not recovered by either.\n", sep = "")

cat(if (eig_ok && ok && orphan && alpha_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
