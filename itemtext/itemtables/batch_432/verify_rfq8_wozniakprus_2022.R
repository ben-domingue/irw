# verify_rfq8_wozniakprus_2022.R -- Step 5b mapping check (batch_432).
#
# Claim: live RFQ1..RFQ8 are canonical RFQ-8 items 1..8 (Fonagy et al. 2016 numbering,
# as listed in Horvath et al. 2023 PLOS ONE Table 2), all stored RAW and ascending
# (1 = strongly disagree ... 7 = strongly agree), including RFQ8, whose .sav value labels
# say the opposite.
#
# Routes: (A) the deposit's OWN derived scoring columns (RFQc*, RFQu*, RFQ7R) reproduce
# the canonical, asymmetric RFQ-8 key applied to the live columns -- this pins which
# items are certainty-only {1,3}, uncertainty-only {7,8}, shared {2,4,5,6}, that RFQ7 is
# the reverse-keyed item, and that RFQ8 is scored ascending; (B) keying polarity: RFQ7 is
# the only item negatively correlated with every other item; (C) the two near-duplicate
# pairs (items 2/6 and 3/4) are the two highest inter-item correlations; (D) item 1 has
# the lowest item-total, matching its published loading (0.513/0.343 vs >=0.753 for the
# rest, Horvath 2023 Table 2).
# NOT established: RFQ2 vs RFQ6 (same key class, near-synonym text, near-identical
# item-totals). That pair rests on the published numbering alone -> PARTIAL.

suppressMessages({library(irw); library(haven)})
TABLE <- "rfq8_wozniakprus_2022"
ok <- TRUE

d <- irw::irw_fetch(TABLE)
w <- as.data.frame(tidyr::pivot_wider(d[, c("id", "item", "resp")],
                                      names_from = item, values_from = resp))
w <- w[order(w$id), ]
it <- paste0("RFQ", 1:8)

sav <- file.path(tempdir(), "rfq_bmcc4c.sav")
if (!file.exists(sav))
    download.file("https://dataverse.harvard.edu/api/access/datafile/4289254?format=original",
                  sav, mode = "wb", quiet = TRUE)
s <- as.data.frame(zap_labels(read_sav(sav)))

# Live ids are row_number() of the deposit (data/rfq8_wozniakprus_2022.R); confirm alignment.
same <- sapply(it, function(v) isTRUE(all.equal(as.numeric(s[[v]]), as.numeric(w[[v]]))))
cat("live == deposit row-for-row:", paste(names(same), same, collapse = " "), "\n")
ok <- ok && all(same)

cert <- function(x) ifelse(x <= 3, 4 - x, 0)   # 1,2,3 -> 3,2,1 ; 4..7 -> 0
unc  <- function(x) ifelse(x >= 5, x - 4, 0)   # 5,6,7 -> 1,2,3 ; 1..4 -> 0

cat("\n(A) deposit derived columns vs canonical key applied to LIVE columns (538 rows)\n")
chk <- list(
    RFQc1 = cert(w$RFQ1), RFQc2 = cert(w$RFQ2), RFQc3 = cert(w$RFQ3),
    RFQc4 = cert(w$RFQ4), RFQc5 = cert(w$RFQ5), RFQc6 = cert(w$RFQ6),
    RFQu2 = unc(w$RFQ2), RFQu4 = unc(w$RFQ4), RFQu5 = unc(w$RFQ5),
    RFQu6 = unc(w$RFQ6), RFQu8 = unc(w$RFQ8),
    RFQ7R = 8 - w$RFQ7, RFQu7 = unc(8 - w$RFQ7))
for (k in names(chk)) {
    m <- sum(as.numeric(s[[k]]) == chk[[k]], na.rm = TRUE)
    cat(sprintf("  %-6s matches %d / %d\n", k, m, nrow(w)))
    ok <- ok && m == nrow(w)
}
# RFQ8 scored DESCENDING would give unc(8 - RFQ8) instead:
m8 <- sum(as.numeric(s$RFQu8) == unc(8 - w$RFQ8))
cat(sprintf("  RFQu8 vs DESCENDING reading of RFQ8: %d / %d (should be far from 538)\n", m8, nrow(w)))
ok <- ok && m8 < nrow(w) / 2
cat("  derived columns absent by design:",
    paste(setdiff(c("RFQc7", "RFQc8", "RFQu1", "RFQu3"), names(s)), collapse = ","), "\n")

R <- cor(w[, it], use = "pairwise.complete.obs")
cat("\n(B) sign of each item's correlations with the other seven\n")
negall <- sapply(it, function(v) all(R[v, setdiff(it, v)] < 0))
for (v in it) cat(sprintf("  %s: %s\n", v, paste(sprintf("%+.3f", R[v, setdiff(it, v)]), collapse = " ")))
cat("  items negative with all others:", names(negall)[negall], "\n")
ok <- ok && identical(names(negall)[negall], "RFQ7")

cat("\n(C) top inter-item correlations\n")
pr <- which(upper.tri(R), arr.ind = TRUE)
top <- pr[order(-R[pr]), ][1:3, ]
for (i in 1:3) cat(sprintf("  r(%s,%s) = %.3f\n", it[top[i, 1]], it[top[i, 2]], R[top[i, 1], top[i, 2]]))
pairs <- apply(top[1:2, ], 1, function(z) paste(sort(it[z]), collapse = "-"))
ok <- ok && setequal(pairs, c("RFQ2-RFQ6", "RFQ3-RFQ4"))

cat("\n(D) corrected item-total correlations (RFQ7 reversed)\n")
x <- w[, it]; x$RFQ7 <- 8 - x$RFQ7
itc <- sapply(it, function(v) cor(x[[v]], rowSums(x[, setdiff(it, v)]), use = "complete.obs"))
cat(" ", paste(sprintf("%s=%.3f", it, itc), collapse = " "), "\n")
nr <- setdiff(it, "RFQ7")
ok <- ok && names(which.min(itc[nr])) == "RFQ1"
cat(sprintf("  lowest non-reversed item: %s (published loading 0.513 / 0.343, lowest of all)\n",
            names(which.min(itc[nr]))))

cat("\nNot established: RFQ2 vs RFQ6 -- same key class, item-totals",
    sprintf("%.4f vs %.4f;", itc["RFQ2"], itc["RFQ6"]),
    "a swap between them is undetectable in these data.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
