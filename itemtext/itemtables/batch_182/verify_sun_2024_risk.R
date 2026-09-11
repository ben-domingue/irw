# verify_sun_2024_risk.R
#
# CLAIM: the live IRW table sun_2024_risk (codes Risk1..Risk3) carries the three
# "Perceived risk" items that Sun, Tohirovich Dedahanov, Li & Young Shin (2024,
# Heliyon 10:e36620, doi:10.1016/j.heliyon.2024.e36620, section 4.2) prints as
# "1. ...; 2. ...; 3. ..." -- i.e. that this 3-column block of the study's
# mmc1.xlsx deposit IS the construct the paper calls Perceived risk (PR), and that
# code RiskK carries the paper's item K.
#
# What is checked:
#
#  (A) live code -> deposited column. Live table joined to mmc1.xlsx (Europe PMC
#      supplementaryFiles for PMC11385760) on id == NO; each live item compared
#      respondent-by-respondent with the same-named deposit column and the other two.
#
#  (B) deposited block -> paper construct, three ways:
#      (B1) Table 7 HTMT, all 15 cells, recomputed under the processing script's
#           block assignment, and all 720 assignments of the six construct labels
#           to the six 3-column blocks scored; reports the best assignment in which
#           PR is NOT the Risk block.
#      (B2) Table 6 Cronbach's alpha for PR (0.963), and for contrast the alpha of
#           every other block (INN's 0.961 is close, so alpha alone is weak).
#      (B3) a PLS-PM re-estimate (mode A outer weights, path weighting scheme, the
#           paper's main-effects model INN/PR/PE/PV/TTF -> U) reproducing Table 6's
#           AVE for all six constructs, PR's CR, and Table 9's Fornell-Larcker matrix.
#           PR is the one construct where equal weighting does NOT reproduce the
#           paper (sum-score AVE 0.932 vs published 0.916) -- its outer weights are
#           very unequal because its link to U is weak -- so matching 0.916/0.970
#           here is specific to the Risk block's content.
#
#  NOT ESTABLISHED: the order of the three items WITHIN the PR block. HTMT, alpha,
#  AVE, CR and the Fornell-Larcker correlations are all invariant to permuting
#  Risk1..3 (the PLS algorithm is permutation-equivariant within a block). The only
#  item-specific published figure is Table 6's bootstrap SD of each loading,
#  0.153/0.173/0.155. Bootstrapping the model here (6 runs x 2000 resamples, done
#  during extraction, not repeated in this script because it is slow and random)
#  gave the Risk2 column the largest SD in 5 of 6 runs (ratio to the other two
#  0.995-1.198; published 1.123) and never separated Risk1 from Risk3. That is
#  consistent with the numbering but resampling-dependent, so it is NOT counted.
#  The tie RiskK <-> printed item K rests on the list numbers matching the digits.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "sun_2024_risk"
SUPPL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11385760/supplementaryFiles"
PRc   <- paste0("Risk", 1:3)

## ---- fetch (843-row table) ---------------------------------------------------
d <- irw::irw_fetch(TABLE)
tz <- tempfile(fileext = ".zip")
download.file(SUPPL, tz, mode = "wb", quiet = TRUE)   # no email / UA header sent
td <- tempfile(); dir.create(td)
unzip(tz, files = "mmc1.xlsx", exdir = td)
s <- as.data.frame(read_excel(file.path(td, "mmc1.xlsx")))
cat(sprintf("deposit mmc1.xlsx: %d rows x %d cols; live rows: %d\n\n", nrow(s), ncol(s), nrow(d)))

## ---- (A) live item vs deposit column ------------------------------------------
ids <- sort(unique(d$id))
L <- sapply(PRc, function(it) { x <- d[d$item == it, ]; x$resp[match(ids, x$id)] })
S <- as.matrix(s[match(ids, s$NO), PRc])
cat(sprintf("(A) joined respondents: %d of %d deposit rows; NA live=%s deposit=%s\n",
            sum(!is.na(match(ids, s$NO))), nrow(s), anyNA(L), anyNA(S)))
agree <- matrix(NA_real_, 3, 3, dimnames = list(paste0("live:", PRc), PRc))
for (i in 1:3) for (j in 1:3) agree[i, j] <- 100 * mean(L[, i] == S[, j])
print(round(agree, 1))
offmax <- max(agree[row(agree) != col(agree)])
A_ok <- !anyNA(L) && !anyNA(S) && all(abs(diag(agree) - 100) < 1e-9) && offmax < 100
cat(sprintf("diagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n",
            all(abs(diag(agree) - 100) < 1e-9), offmax))

BLK <- list(PV  = paste0("Pricevalue", 1:3),  PR = PRc,
            PE  = paste0("PerformanceE", 1:3), INN = paste0("innovation", 1:3),
            TTF = paste0("TTF", 1:3),          U  = paste0("Usage", 1:3))

## ---- (B1) HTMT, paper Table 7 ---------------------------------------------------
PUB <- c("PR-PV" = 0.128, "PE-PV" = 0.534, "PE-PR" = 0.269,
         "INN-PV" = 0.558, "INN-PR" = 0.027, "INN-PE" = 0.446,
         "TTF-PV" = 0.435, "TTF-PR" = 0.178, "TTF-PE" = 0.308, "TTF-INN" = 0.353,
         "U-PV" = 0.408, "U-PR" = 0.055, "U-PE" = 0.338, "U-INN" = 0.343, "U-TTF" = 0.274)
R <- abs(cor(s[, unlist(BLK)]))
mono <- function(a) { r <- R[a, a]; mean(r[upper.tri(r)]) }
htmt <- function(a, b) mean(R[a, b]) / sqrt(mono(a) * mono(b))
score <- function(blk) {
    obs <- sapply(names(PUB), function(n) { p <- strsplit(n, "-")[[1]]; htmt(blk[[p[1]]], blk[[p[2]]]) })
    list(obs = obs, resid = max(abs(obs - PUB)))
}
id <- score(BLK)
cat("(B1) paper Table 7 HTMT vs recomputed (PR cells):\n")
for (n in grep("PR", names(PUB), value = TRUE))
    cat(sprintf("  %-7s published %.3f  observed %.4f  diff %+.4f\n", n, PUB[n], id$obs[n], id$obs[n] - PUB[n]))
cat(sprintf("largest residual over all 15 cells, identity assignment: %.4f\n", id$resid))
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:6)
res <- sapply(P, function(p) { b <- BLK[p]; names(b) <- names(BLK); score(b)$resid })
ord <- order(res)
pr_alt <- sapply(P, function(p) names(BLK)[p][2])   # which block the PR label lands on
cat(sprintf("all %d label->block assignments: best %.4f (identity=%s), second-best %.4f; best with PR NOT on the Risk block %.4f\n\n",
            length(P), res[ord[1]], identical(P[[ord[1]]], 1:6), res[ord[2]], min(res[pr_alt != "PR"])))
B1_ok <- id$resid <= 0.001 && identical(P[[ord[1]]], 1:6) && min(res[pr_alt != "PR"]) > 10 * id$resid

## ---- (B2) alpha, Table 6 ----------------------------------------------------------
alpha <- sapply(BLK, function(b) { x <- s[, b]; 3 / 2 * (1 - sum(apply(x, 2, var)) / var(rowSums(x))) })
cat("(B2) Cronbach alpha by block (published PR 0.963):", paste(sprintf("%s %.4f", names(alpha), alpha), collapse = "  "), "\n")
B2_ok <- abs(alpha["PR"] - 0.963) <= 0.0005
cat("\n")

## ---- (B3) PLS-PM re-estimate, Table 6 AVE/CR and Table 9 ------------------------
pls <- function(X, blk, dep = "U") {
    Xs <- scale(X); n <- nrow(Xs); W <- lapply(blk, function(b) rep(1, length(b)))
    for (it in 1:500) {
        Y <- sapply(names(blk), function(j) as.vector(scale(Xs[, blk[[j]]] %*% W[[j]])))
        ex <- setdiff(names(blk), dep); Z <- Y * 0
        Z[, dep] <- Y[, ex] %*% solve(cor(Y[, ex]), cor(Y[, ex], Y[, dep]))   # path scheme: predecessors
        for (j in ex) Z[, j] <- cor(Y[, j], Y[, dep]) * Y[, dep]              # path scheme: successor
        Wn <- lapply(names(blk), function(j) { w <- as.vector(crossprod(Xs[, blk[[j]]], Z[, j]) / n)
                                               w / sd(Xs[, blk[[j]]] %*% w) })
        names(Wn) <- names(blk)
        dlt <- max(abs(unlist(Wn) - unlist(W))); W <- Wn
        if (dlt < 1e-10) break
    }
    Y <- sapply(names(blk), function(j) as.vector(scale(Xs[, blk[[j]]] %*% W[[j]])))
    Ld <- lapply(names(blk), function(j) as.vector(cor(Xs[, blk[[j]]], Y[, j]))); names(Ld) <- names(blk)
    list(W = W, L = Ld, Y = Y)
}
f <- pls(s, BLK)
AVE <- sapply(f$L, function(l) mean(l^2)); CR <- sapply(f$L, function(l) sum(l)^2 / (sum(l)^2 + sum(1 - l^2)))
PUB_AVE <- c(PV = 0.967, PR = 0.916, PE = 0.963, INN = 0.927, TTF = 0.968, U = 0.952)
PUB_CR  <- c(PV = 0.984, PR = 0.970, PE = 0.987, INN = 0.975, TTF = 0.985, U = 0.978)
cat("(B3) Table 6 AVE / CR, published vs PLS re-estimate:\n")
for (b in names(BLK)) cat(sprintf("  %-4s AVE %.3f / %.4f   CR %.3f / %.4f\n", b, PUB_AVE[b], AVE[b], PUB_CR[b], CR[b]))
ssAVE <- { z <- scale(s[, PRc]); l <- as.vector(cor(z, rowSums(z))); mean(l^2) }
cat(sprintf("  PR outer weights %s; equal-weight sum-score AVE would be %.4f (published 0.916)\n",
            paste(sprintf("%.3f", f$W$PR), collapse = "/"), ssAVE))
FL_PUB <- c("PR-PV" = 0.107, "PE-PV" = 0.524, "PE-PR" = 0.246, "INN-PV" = 0.543, "INN-PR" = -0.026,
            "INN-PE" = 0.433, "TTF-PV" = 0.428, "TTF-PR" = 0.162, "TTF-PE" = 0.303, "TTF-INN" = 0.346,
            "U-PV" = 0.401, "U-PR" = -0.075, "U-PE" = 0.332, "U-INN" = 0.335, "U-TTF" = 0.268)
C <- cor(f$Y)
fl <- sapply(names(FL_PUB), function(n) { p <- strsplit(n, "-")[[1]]; C[p[1], p[2]] })
cat("  Table 9 Fornell-Larcker PR cells, published vs re-estimate:\n")
for (n in grep("PR", names(FL_PUB), value = TRUE)) cat(sprintf("    %-7s %.3f / %.4f\n", n, FL_PUB[n], fl[n]))
cat(sprintf("  largest |diff|: AVE %.4f, CR (PR) %.4f, Table 9 all 15 cells %.4f\n",
            max(abs(AVE - PUB_AVE)), abs(CR["PR"] - PUB_CR["PR"]), max(abs(fl - FL_PUB))))
# note: CR for the other blocks is printed for context only. This formula reproduces PR, PE and INN
# (|diff| <= 0.0005) but runs 0.004-0.006 above the printed value for PV, TTF and U, which this
# script does not explain; only PR's CR enters the verdict.
B3_ok <- max(abs(AVE - PUB_AVE)) <= 0.0006 && abs(CR["PR"] - PUB_CR["PR"]) <= 0.0006 &&
         max(abs(fl - FL_PUB)) <= 0.0006 && abs(ssAVE - 0.916) > 0.01

cat("\nNOT ESTABLISHED: order within the PR block. Every statistic above is invariant to\n",
    "permuting Risk1..3. Table 6's per-item bootstrap SDs (0.153/0.173/0.155) are resampling-\n",
    "dependent; a local bootstrap put Risk2 highest in 5 of 6 runs and never separated\n",
    "Risk1 from Risk3, so it is not counted. Status PARTIAL.\n", sep = "")
cat(sprintf("checks: A=%s B1=%s B2=%s B3=%s\n", A_ok, B1_ok, B2_ok, B3_ok))
cat(if (A_ok && B1_ok && B2_ok && B3_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
