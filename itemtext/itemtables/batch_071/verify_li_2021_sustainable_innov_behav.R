# verify_li_2021_sustainable_innov_behav.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST (mapping_basis = paper_explicit): the six sentences shipped as
# item_text are the S1 Appendix's "Sustainable innovation behavior" block, items 1-6,
# assigned to live columns SIB1..SIB6 in that order.
#
# ROUTE 1 (published per-item statistics). Li, Wu & Xiong (2021) PLOS ONE 16(5):e0250878
# Table 2 (t002, an IMAGE -- the numbers are in no machine-readable form) reports a
# one-factor CFA of the SIB construct on the FOUR retained items SIB1, SIB2, SIB3, SIB6,
# with standardized loadings and R-SQUARE. Refitting that model on the live IRW data must
# reproduce those numbers, and -- because the four published loadings are well separated
# (closest pair 0.754 vs 0.775) -- no permutation of the labels can. The script sweeps all
# 360 ways of assigning 4 of the 6 live items to the 4 published values and checks the
# identity assignment is the unique minimum.
#
# ROUTE 8 (semantic coherence). The article states the two SIB items were deleted because
# "the residual error values of some measurement items were not independent and were
# strongly correlated". The pair excluded from Table 2 is {SIB4, SIB5}. The shipped text
# for appendix items 4 and 5 is the block's only implementation pair ("get the resources I
# need to implement my new ideas" / "make proper long-term plans to implement my new
# ideas"), so a correct mapping predicts SIB4-SIB5 is the tightest pair in the data. The
# script checks it is both the largest raw correlation and the largest one-factor residual.
#
# WHAT THIS DOES NOT ESTABLISH: it does not order appendix items 1 vs 3 against SIB1 vs
# SIB3 (no content prediction separates "looking for new techniques" from "communicate and
# recommend my new ideas"), and it does not order SIB4 vs SIB5 within the implementation
# pair. Those rest on the appendix's own numbering. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(lavaan))

TABLE <- "li_2021_sustainable_innov_behav"

# Li, Wu & Xiong (2021) PLOS ONE 16(5):e0250878, Table 2, SIB block.
PUB_ITEMS <- c("SIB1", "SIB2", "SIB3", "SIB6")
PUB_LOAD  <- c(0.707, 0.903, 0.775, 0.754)
PUB_R2    <- c(0.500, 0.815, 0.601, 0.569)
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", paste0("SIB", 1:6))]
w <- w[complete.cases(w), ]
cat(sprintf("live data: %d respondents x 6 items\n\n", nrow(w)))

fit_load <- function(vars, dat) {
    f <- lavaan::cfa(paste("F =~", paste(vars, collapse = " + ")),
                     data = dat, std.lv = TRUE)
    p <- lavaan::parameterEstimates(f, standardized = TRUE)
    p <- p[p$op == "=~", ]
    list(load = setNames(p$std.all, p$rhs), r2 = lavaan::inspect(f, "r2")[vars])
}

fit <- fit_load(PUB_ITEMS, w)
cat("ROUTE 1 -- one-factor CFA on the four items Table 2 retained\n")
cat(sprintf("%-6s %10s %10s %9s %10s %10s %9s\n",
            "item", "pub.load", "obs.load", "diff", "pub.R2", "obs.R2", "diff"))
for (i in seq_along(PUB_ITEMS))
    cat(sprintf("%-6s %10.3f %10.4f %9.4f %10.3f %10.4f %9.4f\n",
                PUB_ITEMS[i], PUB_LOAD[i], fit$load[i], fit$load[i] - PUB_LOAD[i],
                PUB_R2[i], fit$r2[i], fit$r2[i] - PUB_R2[i]))
worst <- max(abs(c(fit$load - PUB_LOAD, fit$r2 - PUB_R2)))
cat(sprintf("largest deviation: %.4f (tolerance %.2f)\n\n", worst, TOL))

# Rival sweep: every ordered choice of 4 of the 6 live items against the published vector.
cat("ROUTE 1 rival sweep -- all 360 ordered 4-of-6 assignments, SSD to the published loadings\n")
all_items <- paste0("SIB", 1:6)
combn4 <- combn(6, 4, simplify = FALSE)
perm <- function(v) if (length(v) <= 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perm(v[-i]), function(p) c(v[i], p))))
res <- list()
for (cc in combn4) {
    f <- fit_load(all_items[cc], w)
    for (p in perm(seq_along(cc))) {
        lab <- all_items[cc][p]
        ssd <- sum((unname(f$load[lab]) - PUB_LOAD)^2)
        res[[length(res) + 1]] <- list(lab = paste(lab, collapse = ","), ssd = ssd)
    }
}
ssd <- vapply(res, function(x) x$ssd, 0)
lab <- vapply(res, function(x) x$lab, "")
o <- order(ssd)
for (i in 1:5) cat(sprintf("  %-24s SSD = %.6f\n", lab[o[i]], ssd[o[i]]))
identity_lab <- paste(PUB_ITEMS, collapse = ",")
best_ok <- lab[o[1]] == identity_lab
gap <- ssd[o[2]] / max(ssd[o[1]], 1e-12)
cat(sprintf("best assignment is the shipped one: %s; runner-up is %.0fx worse\n\n",
            best_ok, gap))

cat("ROUTE 8 -- the pair Table 2 dropped should be the shipped implementation pair {SIB4,SIB5}\n")
R <- cor(w[, all_items])
Ro <- R; diag(Ro) <- NA
mx <- which(Ro == max(Ro, na.rm = TRUE), arr.ind = TRUE)[1, ]
cat(sprintf("  largest raw correlation: %s-%s r = %.3f\n",
            all_items[mx[1]], all_items[mx[2]], R[mx[1], mx[2]]))
f6 <- lavaan::cfa(paste("F =~", paste(all_items, collapse = " + ")), data = w, std.lv = TRUE)
RR <- lavaan::residuals(f6, type = "cor")$cov
RRo <- RR; diag(RRo) <- NA
mr <- which(abs(RRo) == max(abs(RRo), na.rm = TRUE), arr.ind = TRUE)[1, ]
others <- sort(abs(RRo[upper.tri(RRo)]), decreasing = TRUE)
cat(sprintf("  largest one-factor residual correlation: %s-%s = %.3f (next largest %.3f)\n",
            rownames(RR)[mr[1]], colnames(RR)[mr[2]], RR[mr[1], mr[2]], others[2]))
pair_ok <- setequal(c(all_items[mx[1]], all_items[mx[2]]), c("SIB4", "SIB5")) &&
           setequal(c(rownames(RR)[mr[1]], colnames(RR)[mr[2]]), c("SIB4", "SIB5"))
cat(sprintf("  dropped pair is the tightest pair on both measures: %s\n\n", pair_ok))

cat("SCOPE. Route 1 pins the LIVE COLUMNS to the paper's own codes SIB1/SIB2/SIB3/SIB6\n")
cat("uniquely; route 8 corroborates the TEXT-to-code link for the excluded pair, since the\n")
cat("sentences shipped for SIB4 and SIB5 are the block's only implementation pair and that\n")
cat("pair is empirically the tightest. NOT established: which of the two implementation\n")
cat("sentences is SIB4 and which is SIB5, and which sentence goes with SIB1 vs SIB3 (no\n")
cat("content prediction separates 'looking for new techniques' from 'communicate and\n")
cat("recommend my new ideas'). Both rest on the S1 Appendix's own 1-6 numbering. PARTIAL.\n")

cat(if (worst <= TOL && best_ok && pair_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
