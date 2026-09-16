# verify_thanh_2025_environ_concern.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# IRW codes EC1..EC6 are the column names of the study's own S1 File
# (journal.pone.0320053.s002, .xlsx; data/thanh_2025_green_behavior.py selects
# ^EC\d+$ and melts with no rename). The xlsx has no text, so the wording was
# attached from S1 Appendix (s001.docx), whose rows "Environmental concern 1".."6"
# carry:
#   EC1 I worry about global warming
#   EC2 I worry about natural resource depletion
#   EC3 I worry about water pollution
#   EC4 I worry about wastewater
#   EC5 I am concerned about storms and floods
#   EC6 I worry about the greenhouse effect
#
# INDEPENDENT ROUTE: the article's Table 2 prints each RETAINED item's wording
# beside its SmartPLS outer loading (22 of 30 items survive; for Environmental
# concern the five above EC1..EC5, alpha = 0.934, loadings 0.877 / 0.882 / 0.853
# / 0.912 / 0.926 in that text order). So Table 2 ties TEXT -> number without
# going through the S1 Appendix numbering at all.
#
# (A) The live IRW table equals the S1 File's EC columns of the same name,
#     respondent by respondent (join on id == ID), so the codes are those columns.
# (B) A PLS-PM re-estimation (Mode A, path weighting scheme, the paper's model
#     EC->ATT, EC->PBC, EC->GK, EC->EGB, ATT/PBC/GK->EGB, on the 22 retained
#     indicators) reproduces Table 2's loadings from the S1 File. The claim
#     passes only if all 22 match to 3 decimals AND every one of the 119 other
#     orderings of EC1..EC5 misses at least one published EC loading.
# (C) EC6 is the dropped item: Table 2's EC alpha 0.934 is reproduced by
#     dropping EC6 and by no other single EC item.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "thanh_2025_environ_concern"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0320053.s002"

PUB <- list(EGB = c(0.774, 0.880, 0.831, 0.832, 0.758),
            ATT = c(0.817, 0.836, 0.834),
            EC  = c(0.877, 0.882, 0.853, 0.912, 0.926),
            PBC = c(0.831, 0.901, 0.888, 0.900, 0.826),
            GK  = c(0.908, 0.902, 0.922, 0.906))
PUB_ALPHA_EC <- 0.934

tmp <- tempfile(fileext = ".xlsx")
download.file(URL, tmp, mode = "wb", quiet = TRUE)
src <- as.data.frame(read_excel(tmp))
for (cn in names(src)) src[[cn]] <- as.numeric(src[[cn]])

ok <- TRUE

# ---- (A) live table vs source columns --------------------------------------
live <- irw::irw_fetch(TABLE)
ec <- paste0("EC", 1:6)
cat("(A) live vs S1 File, share of respondents agreeing (row = live code, col = source column)\n")
agree <- matrix(NA, 6, 6, dimnames = list(ec, ec))
for (a in ec) {
    l <- live[live$item == a, c("id", "resp")]
    m <- merge(l, src[, c("ID", ec)], by.x = "id", by.y = "ID")
    for (b in ec) agree[a, b] <- mean(m$resp == m[[b]])
}
print(round(agree, 3))
diag_ok <- all(diag(agree) == 1)
off_max <- max(agree[row(agree) != col(agree)])
cat(sprintf("diagonal all 1.000: %s; largest off-diagonal agreement %.3f\n\n", diag_ok, off_max))
ok <- ok && diag_ok && off_max < 0.9

# ---- (B) PLS-PM loadings ----------------------------------------------------
blocks <- list(EGB = paste0("EGB", 1:5), ATT = paste0("ATT", 1:3), EC = paste0("EC", 1:5),
               PBC = paste0("PBC", 1:5), GK = paste0("GK", 1:4))
paths <- rbind(c("EC", "ATT"), c("EC", "PBC"), c("EC", "GK"), c("EC", "EGB"),
               c("ATT", "EGB"), c("PBC", "EGB"), c("GK", "EGB"))
st <- function(v) (v - mean(v)) / sd(v)

pls_loadings <- function(dat) {
    L <- names(blocks)
    X <- lapply(blocks, function(b) apply(as.matrix(dat[, b]), 2, st))
    w <- lapply(blocks, function(b) rep(1, length(b)))
    for (it in 1:500) {
        Y <- lapply(L, function(j) st(drop(X[[j]] %*% w[[j]]))); names(Y) <- L
        Z <- list()
        for (j in L) {
            z <- rep(0, nrow(dat))
            preds <- paths[paths[, 2] == j, 1]
            if (length(preds)) {
                P <- sapply(preds, function(i) Y[[i]])
                beta <- qr.solve(P, Y[[j]])
                for (k in seq_along(preds)) z <- z + beta[k] * Y[[preds[k]]]
            }
            for (s in paths[paths[, 1] == j, 2]) z <- z + cor(Y[[j]], Y[[s]]) * Y[[s]]
            Z[[j]] <- st(z)
        }
        wn <- lapply(L, function(j) {
            v <- drop(crossprod(X[[j]], Z[[j]])) / (nrow(dat) - 1)
            v / sd(drop(X[[j]] %*% v))
        }); names(wn) <- L
        d <- max(sapply(L, function(j) max(abs(wn[[j]] - w[[j]]))))
        w <- wn
        if (d < 1e-10) break
    }
    Y <- lapply(L, function(j) st(drop(X[[j]] %*% w[[j]]))); names(Y) <- L
    lapply(setNames(L, L), function(j) round(apply(X[[j]], 2, function(x) cor(x, Y[[j]])), 3))
}

est <- pls_loadings(src)
cat("(B) Table 2 loadings, published vs re-estimated from the S1 File\n")
all22 <- TRUE
for (j in names(blocks)) {
    for (k in seq_along(blocks[[j]]))
        cat(sprintf("  %-5s %-6s published %.3f  observed %.3f\n", j, blocks[[j]][k], PUB[[j]][k], est[[j]][k]))
    all22 <- all22 && all(abs(est[[j]] - PUB[[j]]) < 0.0005)
}
cat(sprintf("all 22 loadings reproduced to 3 dp: %s\n", all22))
ok <- ok && all22

perms <- function(v) if (length(v) <= 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:5)
n_wrong_match <- 0; best_wrong <- Inf
for (p in P) {
    if (identical(p, 1:5)) next
    dat <- src
    dat[, paste0("EC", 1:5)] <- src[, paste0("EC", p)]   # text i attached to column EC<p[i]>
    e <- pls_loadings(dat)$EC
    dev <- max(abs(e - PUB$EC))
    best_wrong <- min(best_wrong, dev)
    if (dev < 0.0005) n_wrong_match <- n_wrong_match + 1
}
cat(sprintf("other orderings of EC1..EC5 tested: %d; matching Table 2: %d; smallest max deviation among them %.3f (correct ordering: %.3f)\n\n",
            length(P) - 1, n_wrong_match, best_wrong, max(abs(est$EC - PUB$EC))))
ok <- ok && n_wrong_match == 0

# ---- (C) EC6 is the dropped item --------------------------------------------
alpha <- function(M) { k <- ncol(M); k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M))) }
cat("(C) alpha of the five EC items left after dropping each one (published 0.934)\n")
al <- sapply(ec, function(dr) alpha(as.matrix(src[, setdiff(ec, dr)])))
for (dr in ec) cat(sprintf("  drop %-4s alpha %.4f\n", dr, al[dr]))
hits <- names(al)[round(al, 3) == PUB_ALPHA_EC]
cat("drops reproducing 0.934:", paste(hits, collapse = ", "), "\n\n")
ok <- ok && identical(hits, "EC6")

cat("Establishes: every EC item distinguished -- EC1..EC5 each pinned to its Table 2 wording\n",
    "by loading (no other ordering reproduces), EC6 pinned as the one item Table 2 omits.\n",
    "EC6's wording itself rests on S1 Appendix row 'Environmental concern 6' (it is not in Table 2).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
