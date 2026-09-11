# verify_singleton_2021_carbon_reduction.R
#
# CLAIMS UNDER TEST
#  (A) item axis: live IRW item Qk holds column Qk of the study's S5 File (raw
#      SPSS export), and the study's S6 File (SPSS coding manual) labels Qk
#      "NEP Scale Question k" -- i.e. statement k of the study's S1 File NEP
#      questionnaire. Code -> text is a label match (code IS the source column
#      name; data/singleton_2021_carbon_reduction.py melts Q1..Q15 by name).
#      Falsifiable half tested here: per-item response-level count vectors, live
#      vs S5, must match on the diagonal and be mutually distinct.
#  (B) option axis: resp is stored SCORED, not raw -- odd items SA=5..SD=1,
#      even items SA=1..SD=5 (paper Methods + S1 File p.2). Tested by:
#      per-person sum of live Q1..Q15 == S5 NEP_Tot; published total mean/SD
#      (combined 54.4/6.57, Australia 54.58/6.91, UK 54.10/6.04) and alpha
#      (combined 0.787, Australia 0.815, UK 0.734) reproduce from the stored
#      values, and do NOT reproduce if the seven even items are re-reversed.
#
# WHAT THIS DOES NOT ESTABLISH: that the study's SPSS column Qk truly recorded
# questionnaire statement k -- that link rests on the study's own coding manual.
# The statistics pin each item's stored direction (polarity) and the S5<->live
# identity for every item, not the wording-to-column tie within a polarity class.
#
# Source: PLOS ONE 16(8):e0255445, doi:10.1371/journal.pone.0255445, S5 File (.s013), CC BY 4.0.

suppressMessages({library(irw); library(readxl)})

TABLE <- "singleton_2021_carbon_reduction"
ITEMS <- paste0("Q", 1:15)
SRC   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0255445.s013"

tmp <- tempfile(fileext = ".xlsx")
ok_dl <- tryCatch({download.file(SRC, tmp, mode = "wb", quiet = TRUE); TRUE}, error = function(e) FALSE)
if (!ok_dl) { cat("Could not download S5 File.\nVERDICT: FAIL\n"); quit(status = 0) }
src <- as.data.frame(read_excel(tmp))
src <- src[!is.na(src$ID), ]

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)

# ---- (A) route 9: per-item count vectors, S5 vs live ----
cnt <- function(x) as.integer(table(factor(x, levels = 1:5)))
S <- t(sapply(ITEMS, function(i) cnt(src[[i]])))
L <- t(sapply(ITEMS, function(i) cnt(d$resp[d$item == i])))
cat("(A) Per-item resp 1..5 counts: S5 column vs live item\n")
okA <- logical(15)
for (k in 1:15) {
    okA[k] <- identical(S[k, ], L[k, ])
    cat(sprintf("%-4s S5 %-18s live %-18s %s\n", ITEMS[k], paste(S[k, ], collapse = "/"),
                paste(L[k, ], collapse = "/"), if (okA[k]) "OK" else "MISMATCH"))
}
D <- matrix(0L, 15, 15)
for (a in 1:15) for (b in 1:15) D[a, b] <- sum(abs(S[a, ] - L[b, ]))
diag_hits <- sum(diag(D) == 0); off_hits <- sum(D == 0) - diag_hits
min_off <- min(D[row(D) != col(D)])
cat(sprintf("diagonal exact hits %d/15, off-diagonal exact hits %d, min off-diagonal L1 %d\n\n",
            diag_hits, off_hits, min_off))

# ---- (B) stored direction ----
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", ITEMS)]
tot <- rowSums(w[, ITEMS])
m <- merge(data.frame(id = w$id, live_tot = tot), src[, c("ID", "NEP_Tot", "Country")],
           by.x = "id", by.y = "ID")
n_eq <- sum(m$live_tot == m$NEP_Tot)
cat(sprintf("(B) persons: %d; live sum(Q1..Q15) == S5 NEP_Tot for %d\n", nrow(m), n_eq))

alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
W <- merge(w, src[, c("ID", "Country")], by.x = "id", by.y = "ID")
rev_even <- function(X) { for (i in seq(2, 14, 2)) X[[paste0("Q", i)]] <- 6 - X[[paste0("Q", i)]]; X }
grp <- list(combined = rep(TRUE, nrow(W)), Australia = W$Country == 0, UK = W$Country == 1)
pub <- list(combined = c(54.40, 6.57, 0.787), Australia = c(54.58, 6.91, 0.815), UK = c(54.10, 6.04, 0.734))
okB <- TRUE
cat(sprintf("%-10s %22s %26s %26s\n", "group", "published M/SD/alpha", "stored M/SD/alpha", "even re-reversed M/SD/alpha"))
for (g in names(grp)) {
    X  <- W[grp[[g]], ITEMS]; Xr <- rev_even(X)
    s  <- c(mean(rowSums(X)), sd(rowSums(X)), alpha(X))
    sr <- c(mean(rowSums(Xr)), sd(rowSums(Xr)), alpha(Xr))
    cat(sprintf("%-10s %8.2f/%5.2f/%5.3f %12.2f/%5.2f/%5.3f %14.2f/%5.2f/%5.3f\n",
                g, pub[[g]][1], pub[[g]][2], pub[[g]][3], s[1], s[2], s[3], sr[1], sr[2], sr[3]))
    if (abs(s[1] - pub[[g]][1]) > 0.01 || abs(s[2] - pub[[g]][2]) > 0.01 || abs(s[3] - pub[[g]][3]) > 0.001) okB <- FALSE
    if (abs(sr[1] - pub[[g]][1]) < 0.5) okB <- FALSE   # the raw reading must NOT reproduce
}

# Per-item polarity: flipping any single stored item must lower combined alpha.
a0 <- alpha(W[, ITEMS])
flip <- sapply(ITEMS, function(i) { X <- W[, ITEMS]; X[[i]] <- 6 - X[[i]]; alpha(X) })
cat(sprintf("\ncombined alpha stored %.3f; alpha after flipping each single item:\n", a0))
print(round(flip, 3))
okP <- all(flip < a0)
cat(sprintf("every single-item flip lowers alpha: %s\n", okP))
cat("Not established: wording-to-column order within a polarity class (rests on S6 coding manual labels).\n")

cat(if (all(okA) && diag_hits == 15 && off_hits == 0 && n_eq == nrow(m) && nrow(m) == 106 && okB && okP)
    "VERDICT: PASS\n" else "VERDICT: FAIL\n")
