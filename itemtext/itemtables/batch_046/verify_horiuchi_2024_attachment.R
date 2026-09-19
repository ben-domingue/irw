# verify_horiuchi_2024_attachment.R
#
# CLAIM UNDER TEST. The IRW item codes attach1..attach20 are the raw column names
# of the study's own Survey 1 file (S7 Table, journal.pone.0298214.s008), so the
# code is not in question; what is inferred is WHICH published item wording sits
# on each column. The paper's item list (S2 Table, .s003) is NOT in column order:
# its 20 wordings cannot even be reconciled at the SET level with the 13
# attachment items the paper says survived selection. The shipped mapping was
# rebuilt instead from two other supplements:
#   S4 Table (.s005) -- rotated factor matrix, keyed to the authors' item NUMBERS
#   S3 Table (.s004) -- the final 20 RS-MSM items, with wording, grouped by factor
# Step 1 below shows S4's "Attachment k" IS raw column attach<k> (its published
# loadings are reproduced column by column). Step 2 shows the RS-MSM item order
# used to carry wording onto those columns reproduces the Survey 2 (S8 Table,
# .s009) item means far better than chance.
#
# This is a PARTIAL check by construction: 7 of 20 columns ship blank item_text
# (they were dropped before any statistic was published about them), and step 3
# lists the single swaps among the 13 that the route does NOT exclude.

suppressMessages({library(psych); library(GPArotation); library(readxl); library(irw)})

TABLE <- "horiuchi_2024_attachment"
base  <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0298214."
get <- function(id, skip) {
    f <- file.path(tempdir(), paste0(id, ".xlsx"))
    if (!file.exists(f)) download.file(paste0(base, id), f, quiet = TRUE, mode = "wb")
    as.data.frame(read_excel(f, skip = skip))
}
s1 <- get("s008", 2)   # Survey 1 raw data -- the source of the IRW table
s2 <- get("s009", 1)   # Survey 2 raw data -- the RS-MSM readministration

# ---- 0. the raw file is the live table (linkage, not evidence) -----------------
ts <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(ts$per_item)
raw_n   <- sapply(paste0("attach", 1:20), function(v) sum(!is.na(suppressWarnings(as.numeric(s1[[v]])))))
raw_max <- sapply(paste0("attach", 1:20), function(v) max(suppressWarnings(as.numeric(s1[[v]])), na.rm = TRUE))
live_n   <- pi$n[match(paste0("attach", 1:20), pi$item)]
live_max <- pi$resp_max[match(paste0("attach", 1:20), pi$item)]
cat("0. raw S7 vs live: n identical for all 20 items:", all(raw_n == live_n),
    "| resp_max identical:", all(raw_max == live_max),
    sprintf("(attach4 max = %d in both, every other item 2)\n\n", as.integer(raw_max[["attach4"]])))

# ---- 1. published S4 loadings reproduce, column by column ----------------------
sel  <- c(paste0("attach", c(1,2,3,17,18)), paste0("dissoc", c(3,4,5,7,8,11,15)),
          paste0("attach", c(5,6,7,8,10,11,13,15)))
PUB  <- matrix(c(0.513,0.345, 0.697,0.316, 0.632,0.276, 0.744,0.267, 0.732,0.256,
                 0.678,0.205, 0.856,-0.025, 0.933,-0.165, 0.828,0.001, 0.717,0.265,
                 0.875,-0.057, 0.649,0.038,
                 0.234,0.572, 0.267,0.758, -0.036,1.004, 0.146,0.839, 0.005,0.897,
                 0.244,0.708, -0.014,0.860, 0.357,0.566),
               ncol = 2, byrow = TRUE, dimnames = list(sel, c("F1", "F2")))
X <- s1[, sel]; X[] <- lapply(X, function(v) suppressWarnings(as.numeric(v)))
X <- X[complete.cases(X), ]
rho <- suppressWarnings(psych::polychoric(X)$rho)
fit <- suppressWarnings(psych::fa(rho, nfactors = 2, rotate = "geominQ",
                                  n.obs = nrow(X), fm = "ml"))
L <- unclass(fit$loadings)[, 1:2]
# orient: the factor loading dissoc5 highest is the published F1
if (which.max(abs(L["dissoc5", ])) == 2) L <- L[, c(2, 1)]
colnames(L) <- c("F1", "F2")
cat(sprintf("%-9s %14s %14s\n", "column", "published F1/F2", "recomputed"))
for (v in sel)
    cat(sprintf("%-9s %6.3f %6.3f   %6.3f %6.3f\n", v, PUB[v,1], PUB[v,2], L[v,1], L[v,2]))
agree <- sum((PUB[,1] > PUB[,2]) == (L[,1] > L[,2]))
rL <- cor(as.vector(PUB), as.vector(L))
cat(sprintf("\ndominant-factor agreement: %d/20 columns | r(published, recomputed loadings) = %.3f\n",
            agree, rL))
cat("(the one column that can flip is attach15, near-tied in both: published .357/.566,\n",
    " recomputed .456/.447 -- this rerun is psych/polychoric ML+geominQ, the authors ran\n",
    " Mplus, so a marginal item's dominant factor is not expected to be stable.)\n\n", sep = "")

# ---- 2. cross-survey item means under the shipped RS-MSM order -----------------
ord <- sel   # RS-MSM item 1..20 in S3 Table order == ascending column number per factor
m1 <- sapply(ord, function(v) mean(suppressWarnings(as.numeric(s1[[v]])), na.rm = TRUE))
m2 <- sapply(paste0("MSM", 1:20), function(v) mean(suppressWarnings(as.numeric(s2[[v]])), na.rm = TRUE))
obs <- suppressWarnings(cor(m1, m2, method = "spearman"))
Apos <- which(grepl("^attach", ord))          # the 13 inferred positions
set.seed(1); N <- 20000; null <- numeric(N)
for (i in seq_len(N)) { p <- seq_along(ord); p[Apos] <- sample(p[Apos])
                        null[i] <- suppressWarnings(cor(m1[p], m2, method = "spearman")) }
cat(sprintf("Survey1 (mapped) vs Survey2 MSM item means: Spearman = %.3f\n", obs))
cat(sprintf("permuting only the 13 attachment positions: null mean %.3f, p(null >= obs) = %.5f\n\n",
            mean(null), mean(null >= obs)))

# ---- 3. what this does NOT establish ------------------------------------------
pairs <- t(combn(Apos, 2)); nt <- 0
for (k in seq_len(nrow(pairs))) {
    p <- seq_along(ord); p[pairs[k,]] <- rev(p[pairs[k,]])
    if (suppressWarnings(cor(m1[p], m2, method = "spearman")) >= obs - 1e-12) nt <- nt + 1
}
cat(sprintf("single swaps among the 13 that the means route does NOT exclude: %d of %d\n",
            nt, nrow(pairs)))
cat("Also not established: the 7 columns attach4/9/12/14/16/19/20, which ship blank\n",
    "item_text -- they were dropped before any per-item statistic was published.\n",
    "Hence status PARTIAL, not VERIFIED.\n\n", sep = "")

ok <- agree >= 19 && rL > 0.9 && obs > 0.85 && mean(null >= obs) < 0.001 &&
      all(raw_n == live_n) && all(raw_max == live_max)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
