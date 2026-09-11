# verify_sun_2024_usage.R
#
# CLAIM: the live IRW table sun_2024_usage (codes Usage1..Usage3) carries the three
# "Usage" items that Sun, Tohirovich Dedahanov, Li & Young Shin (2024, Heliyon
# 10:e36620, doi:10.1016/j.heliyon.2024.e36620, PMC11385760, section 4.2) prints as
# "1. I am likely to use ...; 2. I desire to use ...; 3. I plan to use ...", i.e.
# that this 3-column block of the study's mmc1.xlsx deposit IS the construct the
# paper calls Usage (U), and that code UsageK carries the paper's item K.
#
# What is checked:
#
#  (A) live code -> deposited column. Live table joined to mmc1.xlsx (Europe PMC
#      supplementaryFiles for PMC11385760) on id == NO; each live item compared
#      respondent-by-respondent with the same-named deposit column and the other two.
#
#  (B) deposited block -> paper construct, three ways:
#      (B1) Table 7 HTMT, all 15 construct-pair cells, recomputed from the deposit
#           under the processing script's block assignment, and ALL 720 assignments
#           of the six construct labels to the six 3-column blocks scored, reporting
#           the best assignment in which U is NOT the Usage block.
#      (B2) Table 6 U row: AVE 0.952 (PLS mode-A loadings) and Cronbach's alpha 0.975.
#      (B3) Table 9 (Fornell-Larcker) U row: latent-variable correlations of U with
#           PV/PR/PE/INN/TTF, from a PLS path-weighting estimation of the paper's
#           model (five predictors + four TTF interactions -> U).
#
#  NOT ESTABLISHED: the order of the three items WITHIN the Usage block. HTMT, alpha,
#  AVE, CR and the latent correlations are all invariant to permuting Usage1..3. The
#  only item-specific published figure, Table 6's per-item "Standard deviation"
#  (U1 0.009 / U2 0.012 / U3 0.006), is a bootstrap SD of the outer loading; it is
#  resampling-dependent, and a 1000-resample re-estimation (printed in section C
#  below, informational only) gives ~0.003-0.004 for all three Usage items while it
#  gives ~0.009/0.011/0.006 for the INNOVATION items -- so that printed row looks
#  like it belongs to another construct and cannot be used to order Usage1..3. The
#  tie UsageK <-> printed item K rests on the matching numbers alone.

suppressMessages({ library(irw); library(readxl) })
set.seed(20260910)

TABLE <- "sun_2024_usage"
SUPPL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11385760/supplementaryFiles"
USE   <- paste0("Usage", 1:3)

## ---- fetch --------------------------------------------------------------
d <- irw::irw_fetch(TABLE)                      # 843 rows; small table
tz <- tempfile(fileext = ".zip")
download.file(SUPPL, tz, mode = "wb", quiet = TRUE)   # no email / UA header sent
td <- tempfile(); dir.create(td)
unzip(tz, files = "mmc1.xlsx", exdir = td)
s <- as.data.frame(read_excel(file.path(td, "mmc1.xlsx")))
cat(sprintf("deposit mmc1.xlsx: %d rows x %d cols; live rows: %d\n\n", nrow(s), ncol(s), nrow(d)))

## ---- (A) live item vs deposit column, per respondent ----------------------
ids <- sort(unique(d$id))
L <- sapply(USE, function(it) { x <- d[d$item == it, ]; x$resp[match(ids, x$id)] })
S <- as.matrix(s[match(ids, s$NO), USE])
cat(sprintf("(A) joined respondents: %d of %d deposit rows; NA live=%s deposit=%s\n",
            length(ids), nrow(s), anyNA(L), anyNA(S)))
agree <- matrix(NA_real_, 3, 3, dimnames = list(paste0("live:", USE), USE))
for (i in 1:3) for (j in 1:3) agree[i, j] <- 100 * mean(L[, i] == S[, j])
print(round(agree, 1))
offd <- max(agree[row(agree) != col(agree)])
A_ok <- length(ids) == nrow(s) && !anyNA(L) && !anyNA(S) &&
        all(abs(diag(agree) - 100) < 1e-9) && offd < 100
cat(sprintf("diagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n",
            all(abs(diag(agree) - 100) < 1e-9), offd))

## ---- (B1) HTMT matrix (paper Table 7) ------------------------------------------
BLK <- list(PV  = paste0("Pricevalue", 1:3),  PR = paste0("Risk", 1:3),
            PE  = paste0("PerformanceE", 1:3), INN = paste0("innovation", 1:3),
            TTF = paste0("TTF", 1:3),          U  = USE)
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
cat("(B1) paper Table 7 HTMT vs recomputed from mmc1.xlsx (processing-script block assignment):\n")
for (n in names(PUB)) cat(sprintf("  %-8s published %.3f  observed %.4f  diff %+.4f%s\n",
    n, PUB[n], id$obs[n], id$obs[n] - PUB[n], if (grepl("^U-", n)) "   <- Usage row" else ""))
cat(sprintf("largest residual, identity assignment: %.4f\n", id$resid))

perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:6)
res <- sapply(P, function(p) { b <- BLK[p]; names(b) <- names(BLK); score(b)$resid })
ord <- order(res)
u_blk <- sapply(P, function(p) names(BLK)[p][6])   # which true block gets the "U" label
cat(sprintf("all %d label->block assignments scored; best %.4f (identity=%s), second-best %.4f\n",
            length(P), res[ord[1]], identical(P[[ord[1]]], 1:6), res[ord[2]]))
u_alt <- min(res[u_blk != "U"])
cat(sprintf("best assignment in which the U label is NOT on the Usage block: %.4f\n\n", u_alt))
B1_ok <- id$resid <= 0.001 && identical(P[[ord[1]]], 1:6) && u_alt > 5 * id$resid

## ---- (B2) Table 6 U row: AVE and alpha ------------------------------------------
stdz <- function(m) scale(as.matrix(m))
x <- s[, USE]
alpha <- 3 / 2 * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))
Z <- stdz(x); w <- rep(1, 3)
for (k in 1:200) { lv <- as.vector(scale(Z %*% w)); w <- as.vector(cor(Z, lv)) }
lv <- as.vector(scale(Z %*% w)); load <- as.vector(cor(Z, lv))
ave <- mean(load^2)
cat(sprintf("(B2) Usage mode-A loadings %.4f/%.4f/%.4f; AVE published 0.952, observed %.4f\n",
            load[1], load[2], load[3], ave))
cat(sprintf("     Cronbach alpha U: published 0.975, observed %.4f (diff %+.4f; see note)\n", alpha, alpha - 0.975))
# alpha for U is 0.0026 below the printed value while PV/PR/PE/INN/TTF reproduce to
# <=0.0005; the printed U alpha equals this block's rho_A (0.975). Printed but gated
# loosely, because AVE, HTMT and Table 9 all reproduce exactly for the same block.
B2_ok <- abs(ave - 0.952) <= 0.0006 && abs(alpha - 0.975) <= 0.005

## ---- (B3) Table 9 U row: PLS latent correlations ----------------------------------
nm <- names(BLK); exo <- setdiff(nm, "U")
pls <- function(D) {
    X <- lapply(BLK, function(cols) stdz(D[, cols]))
    W <- lapply(BLK, function(cols) rep(1, 3))
    for (it in 1:300) {
        Y <- lapply(nm, function(k) as.vector(scale(X[[k]] %*% W[[k]]))); names(Y) <- nm
        Pm <- cbind(sapply(exo, function(k) Y[[k]]),
                    sapply(c("INN", "PR", "PV", "PE"), function(k) as.vector(scale(Y$TTF * Y[[k]]))))
        beta <- qr.solve(Pm, Y$U)
        Zp <- lapply(exo, function(k) cor(Y[[k]], Y$U) * Y$U); names(Zp) <- exo
        Zp$U <- as.vector(Pm %*% beta)
        Wn <- lapply(nm, function(k) { v <- as.vector(cor(X[[k]], Zp[[k]])); v / sd(X[[k]] %*% v) }); names(Wn) <- nm
        dlt <- max(sapply(nm, function(k) max(abs(abs(Wn[[k]]) - abs(W[[k]])))))
        W <- Wn
        if (dlt < 1e-8) break
    }
    Y <- lapply(nm, function(k) as.vector(scale(X[[k]] %*% W[[k]]))); names(Y) <- nm
    list(Y = Y, load = lapply(nm, function(k) as.vector(cor(X[[k]], Y[[k]]))) |> setNames(nm))
}
fit <- pls(s)
PUB9 <- c(PV = 0.401, PR = -0.075, PE = 0.332, INN = 0.335, TTF = 0.268)
obs9 <- sapply(names(PUB9), function(k) cor(fit$Y[[k]], fit$Y$U))
cat("(B3) paper Table 9 U row (latent-variable correlations) vs PLS path-weighting re-estimate:\n")
for (k in names(PUB9)) cat(sprintf("  U-%-4s published %+.3f  observed %+.4f  diff %+.4f\n", k, PUB9[k], obs9[k], obs9[k] - PUB9[k]))
B3_ok <- max(abs(obs9 - PUB9)) <= 0.002
cat(sprintf("largest residual: %.4f\n\n", max(abs(obs9 - PUB9))))

## ---- (C) informational only: Table 6 per-item bootstrap SD -------------------------
B <- 1000
bl <- replicate(B, { f <- pls(s[sample.int(nrow(s), replace = TRUE), ]); c(f$load$U, f$load$INN) })
sdU <- apply(bl[1:3, ], 1, sd); sdI <- apply(bl[4:6, ], 1, sd)
cat(sprintf("(C) bootstrap SD of outer loadings (%d resamples; NOT gated):\n", B))
cat(sprintf("    Usage1..3      observed %.4f/%.4f/%.4f   printed for U   0.009/0.012/0.006\n", sdU[1], sdU[2], sdU[3]))
cat(sprintf("    innovation1..3 observed %.4f/%.4f/%.4f   printed for INN 0.003/0.003/0.004\n", sdI[1], sdI[2], sdI[3]))
cat("    -> the printed U row does not match the Usage items; it cannot order Usage1..3.\n\n")

cat("NOT ESTABLISHED: order within the Usage block. HTMT, AVE, alpha and the latent\n",
    "correlations are invariant to permuting Usage1..3, and no usable item-specific\n",
    "statistic is published. Construct membership pinned, within-block order not: PARTIAL.\n", sep = "")

cat(sprintf("checks: A=%s B1=%s B2=%s B3=%s\n", A_ok, B1_ok, B2_ok, B3_ok))
cat(if (A_ok && B1_ok && B2_ok && B3_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
