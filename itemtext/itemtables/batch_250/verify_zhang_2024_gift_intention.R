# verify_zhang_2024_gift_intention.R -- Step 5b mapping check (batch_250)
# (adapted from references/verify_template.R)
#
# Claim: IRW item INT<k> is S1 Dataset (pone.0296908.s002) column INT<k>, which is the
# paper's Table 2 item INT<k>, whose wording is item k under "Gift-giving intention" in
# S1 Appendix (pone.0296908.s001).
# The processing script (data/zhang_2024_giftgiving.py) melts the S1 columns BY NAME
# (value_vars=["INT1","INT2","INT3"]), so the IRW code IS the source column name.
#
# Route A (code -> S1 column): id-level exact agreement of each live INT item with every
#   one of the 23 S1 item columns. Holds iff each item agrees n/n with its own column only.
# Route B (S1 column -> paper Table 2 code): standardized loadings of the paper's
#   6-factor CFA, recomputed from S1, vs Table 2 (INT1 0.831, INT2 0.797, INT3 0.934).
#   The three published loadings are well separated, so this distinguishes every
#   Table 2 code from every other.
# What neither route establishes: that Appendix item k is Table 2's INT<k>. The Appendix
#   numbers its three items 1-3 under the construct heading without printing the INT codes;
#   that tie is by the paper's numbering (paper_order), and the three items' content does
#   not predict any statistic that could test it. Nor that the English is what the
#   Chinese-language respondents read.
#
# Note: fetches the live table (975 rows) with irw_fetch -- a deliberate, tiny export,
# because an id-level comparison cannot be done from server-side set aggregates.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "zhang_2024_gift_intention"
PUB_LOAD <- c(INT1 = 0.831, INT2 = 0.797, INT3 = 0.934)   # paper Table 2
TOL <- 0.01

d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
tf <- tempfile(fileext = ".xlsx")
download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0296908.s002",
              tf, mode = "wb", quiet = TRUE)
s1 <- as.data.frame(read_excel(tf))
icols <- setdiff(names(s1), c("Number", "Gender", "Age", "Income", "TotalSpend"))
cat(sprintf("S1: %d rows, %d item columns; live: %d ids, %d rows\n",
            nrow(s1), length(icols), length(unique(d$id)), nrow(d)))

ok <- TRUE
cat("\nRoute A: id-level exact agreement of each live item with every S1 item column\n")
for (it in names(PUB_LOAD)) {
    x <- d[d$item == it, ]
    m <- match(x$id, s1$Number)
    if (anyNA(m)) ok <- FALSE
    agree <- sapply(icols, function(q) sum(s1[[q]][m] == x$resp, na.rm = TRUE))
    full <- names(agree)[agree == nrow(x)]
    runner <- sort(agree[names(agree) != it], decreasing = TRUE)[1]
    cat(sprintf("  %-4s n=%d  own column: %d/%d   full agreement: %s   best other: %s %d/%d\n",
                it, nrow(x), agree[[it]], nrow(x), paste(full, collapse = ","),
                names(runner), runner, nrow(x)))
    if (!identical(full, it)) ok <- FALSE
}

cat("\nRoute B: 6-factor CFA standardized loadings (from S1) vs paper Table 2\n")
if (requireNamespace("lavaan", quietly = TRUE)) {
    mod <- "ATR=~ATR1+ATR2+ATR3+ATR4\nEXP=~EXP1+EXP2+EXP3\nPSI=~PSI1+PSI2+PSI3
VDSP=~VDSP1+VDSP2+VDSP3+VDSP4+VDSP5+VDSP6\nSDSP=~SDSP1+SDSP2+SDSP3+SDSP4\nINT=~INT1+INT2+INT3"
    std <- lavaan::standardizedSolution(lavaan::cfa(mod, data = s1, std.lv = TRUE))
    std <- std[std$op == "=~" & std$lhs == "INT", ]
    for (i in seq_len(nrow(std))) {
        dif <- std$est.std[i] - PUB_LOAD[[std$rhs[i]]]
        cat(sprintf("  %-4s published %.3f  recomputed %.3f  diff %+.3f\n",
                    std$rhs[i], PUB_LOAD[[std$rhs[i]]], std$est.std[i], dif))
        if (abs(dif) > TOL) ok <- FALSE
    }
    # a swap of any two codes would move a loading by >= 0.034 (0.831 vs 0.797)
} else { cat("  lavaan not installed -- Route B cannot run\n"); ok <- FALSE }

sc <- rowMeans(s1[, names(PUB_LOAD)])
cat(sprintf("\nScale mean/SD from S1: %.3f / %.3f (paper Table 3 INT: 3.716 / 1.022)\n", mean(sc), sd(sc)))
cat("Not established: Appendix item k -> INT<k> (numbering only), nor Chinese administered wording.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
