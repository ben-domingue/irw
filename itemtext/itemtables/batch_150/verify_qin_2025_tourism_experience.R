# verify_qin_2025_tourism_experience.R
#
# CLAIM: RCTE1..RCTE5 in the live IRW table carry the five rich-cultural-tourism-
# experience item texts that S1 Table of PLOS ONE 10.1371/journal.pone.0336220
# prints against exactly those codes (and that the article's own Table 2 reprints
# in the same order).
#
# Two independent links, neither of which is a count check:
#
#  (A) live code -> deposited column. The live table is joined to the study's own
#      S1 Data CSV (10.1371/journal.pone.0336220.s002) on id == "No.", and each
#      live item's responses are compared to the source column of the same name,
#      respondent by respondent. The cross-code comparisons are printed too, so
#      the reader can see the wrong pairings do NOT match. If the processing
#      script had permuted the five codes, this is where it breaks.
#
#  (B) deposited column -> paper code. The paper's Table 7 cross-loading matrix
#      gives, for each of RCTE1..RCTE5, its loading on the BI, CI, PCD and SA
#      constructs. Those 20 cells are recomputed from the source CSV as
#      correlations of the raw item with each construct's mean and compared with
#      the published values, and ALL 120 permutations of the five codes are
#      scored so the identity assignment's margin is visible. This is what ties
#      the paper's own codes -- hence its S1 Table wording -- to the deposit's
#      columns.

suppressMessages(library(irw))

TABLE <- "qin_2025_tourism_experience"
SRC   <- "https://doi.org/10.1371/journal.pone.0336220.s002"
ITEMS <- paste0("RCTE", 1:5)

# Paper Table 7 (Discriminant Validity Results, Cross-Loading Analysis), RCTE rows.
#                       BI     CI     PCD     SA
PUB <- rbind(RCTE1 = c(0.713, 0.800, 0.303, 0.766),
             RCTE2 = c(0.709, 0.757, 0.300, 0.716),
             RCTE3 = c(0.696, 0.790, 0.332, 0.742),
             RCTE4 = c(0.741, 0.802, 0.336, 0.762),
             RCTE5 = c(0.717, 0.772, 0.298, 0.747))
colnames(PUB) <- c("BI", "CI", "PCD", "SA")

d <- irw::irw_fetch(TABLE)
s <- read.csv(SRC, check.names = FALSE)

## ---- (A) live item code vs source column, per respondent -------------------
ids <- sort(unique(d$id))
L <- sapply(ITEMS, function(it) { x <- d[d$item == it, ]; x$resp[match(ids, x$id)] })
S <- as.matrix(s[match(ids, s[["No."]]), ITEMS])
cat(sprintf("joined respondents: %d (live ids x S1 Data 'No.'); NAs live=%s src=%s\n\n",
            length(ids), anyNA(L), anyNA(S)))

cat("(A) per-respondent agreement, live item x source column (% of 547):\n")
cat(sprintf("%-8s %8s %8s %8s %8s %8s\n", "live", ITEMS[1], ITEMS[2], ITEMS[3], ITEMS[4], ITEMS[5]))
agree <- matrix(NA_real_, 5, 5, dimnames = list(ITEMS, ITEMS))
for (i in 1:5) {
    for (j in 1:5) agree[i, j] <- 100 * mean(L[, i] == S[, j])
    cat(sprintf("%-8s %7.1f%% %7.1f%% %7.1f%% %7.1f%% %7.1f%%\n", ITEMS[i], agree[i,1], agree[i,2], agree[i,3], agree[i,4], agree[i,5]))
}
diag_ok     <- all(abs(diag(agree) - 100) < 1e-9)
offdiag_max <- max(agree[row(agree) != col(agree)])
cat(sprintf("\ndiagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n", diag_ok, offdiag_max))

## ---- (B) recomputed cross-loadings vs paper Table 7 ------------------------
cons <- list(BI = paste0("BI", 1:3), CI = paste0("CI", 1:3),
             PCD = paste0("PCD", 1:3), SA = paste0("SA", 1:3))
OBS <- t(sapply(ITEMS, function(it)
    sapply(cons, function(b) cor(s[[it]], rowMeans(s[, b])))))

cat("(B) paper Table 7 vs recomputed from S1 Data (r of item with construct mean):\n")
cat(sprintf("%-8s %18s %18s %18s %18s\n", "item", "BI", "CI", "PCD", "SA"))
for (i in 1:5)
    cat(sprintf("%-8s %8.3f/%-8.3f %8.3f/%-8.3f %8.3f/%-8.3f %8.3f/%-8.3f\n",
                ITEMS[i], PUB[i, 1], OBS[i, 1], PUB[i, 2], OBS[i, 2],
                PUB[i, 3], OBS[i, 3], PUB[i, 4], OBS[i, 4]))
ident <- max(abs(PUB - OBS))
cat(sprintf("\nlargest residual, identity assignment: %.4f\n", ident))

perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:5)
res <- sapply(P, function(p) max(abs(PUB - OBS[p, ])))
o <- order(res)
cat("best four of the 120 code assignments (max residual):\n")
for (k in o[1:4]) cat(sprintf("  %s  %.4f\n", paste(P[[k]], collapse = ""), res[k]))
runner <- res[o[2]]
cat(sprintf("identity is %.1fx better than the next-best permutation\n\n", runner / ident))

# Item-total correlations, ordered as the paper's Table 7 RCTE-column loadings.
LOAD <- c(0.919, 0.902, 0.925, 0.920, 0.892)
M <- as.matrix(s[, ITEMS]); tot <- rowSums(M)
itc <- sapply(1:5, function(i) cor(M[, i], tot))
cat("item-total r vs published RCTE loading:\n")
for (i in 1:5) cat(sprintf("  %-6s loading %.3f  item-total r %.3f\n", ITEMS[i], LOAD[i], itc[i]))
cat(sprintf("Spearman rank correlation: %.2f\n\n", cor(LOAD, itc, method = "spearman")))

cat("Note: (A) alone pins live code -> deposited column and nothing more; the tie from\n",
    "the deposited column to the printed wording comes from S1 Table's explicit code\n",
    "labels, corroborated by (B). The five RCTE loadings are close (0.892-0.925), so the\n",
    "item-total ranking is supporting evidence, not decisive on its own.\n", sep = "")

ok <- diag_ok && offdiag_max < 90 && ident <= 0.01 && runner / ident > 3
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
