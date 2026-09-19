# verify_zeng_2026_gai_ttf.R -- Step 5b mapping check (batch_249)
#
# Claim: IRW item TTF<k> is S1 File column Q<4+k>, which the paper's Table 2 prints as
# "TTF<k>(Q<4+k>)" beside its item wording (Task-Technology Fit block, Q5-Q9).
# The processing script (data/zeng_2026_gai_learning.py) renames Q5..Q9 -> TTF1..TTF5
# BY NAME (dict(zip(q_cols, item_names))), not by spreadsheet position. This block IS one
# of the permuted ones in S1: the sheet's physical column order is Q5,Q6,Q9,Q7,Q8, so
# a positional rename would have put Q9 under TTF3, Q7 under TTF4 and Q8 under TTF5.
# Route A below is what shows the live data followed the names, not the positions.
#
# Route A (decisive for code -> S1 column): for every live TTF item, count id-level exact
#   agreement with EVERY Q5..Q39 column of S1. The mapping holds iff each item agrees
#   207/207 with its claimed column and with no other column.
# Route B (corroboration of S1 column -> paper's analysis): one-factor CFA on the live
#   items vs the paper's Table 3 standardized loadings for Q5..Q9. Q5 (0.974) and
#   Q6 (0.777) are distinctive; Q9 (0.849) vs Q7/Q8 (0.894/0.912) is only loosely separated.
# What neither route establishes: that Table 2's printed wording is what sits beside each
#   Q code -- that tie is the paper's own explicit "TTFk(Qn)" label (paper_explicit). Also,
#   that S1's header names themselves are correct is taken from the deposit; Route B
#   shows only that the paper's own Table 3 analysis agrees with those names.
#
# Note: this fetches the live table (1,035 rows) with irw_fetch -- a deliberate, tiny export,
# because an id-level comparison cannot be done from server-side set aggregates.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "zeng_2026_gai_ttf"
CLAIM <- setNames(paste0("Q", 5:9), paste0("TTF", 1:5))
PUB_LOAD <- c(Q5 = 0.974, Q6 = 0.777, Q7 = 0.894, Q8 = 0.912, Q9 = 0.849)  # Table 3, Std. (Q5 row also carries SMC 0.949, CR 0.947, AVE 0.781)

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]

tf <- tempfile(fileext = ".xlsx")
download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346696.s001",
              tf, mode = "wb", quiet = TRUE)
s1 <- as.data.frame(read_excel(tf))
qcols <- paste0("Q", 5:39)
cat(sprintf("S1: %d rows; live: %d ids, %d rows\n", nrow(s1), length(unique(d$id)), nrow(d)))
cat("S1 physical order of the TTF block:", paste(names(s1)[names(s1) %in% CLAIM], collapse = ","), "\n")

ok <- TRUE
cat("\nRoute A: id-level exact agreement of each live item with every S1 Q column\n")
for (it in names(CLAIM)) {
    x <- d[d$item == it, ]
    src <- s1[match(x$id, s1$Code), qcols]
    if (any(is.na(match(x$id, s1$Code)))) ok <- FALSE
    agree <- sapply(qcols, function(q) sum(src[[q]] == x$resp, na.rm = TRUE))
    full <- names(agree)[agree == nrow(x)]
    runner <- sort(agree[names(agree) != CLAIM[[it]]], decreasing = TRUE)[1]
    cat(sprintf("  %-4s n=%d  claimed %s: %d/%d   columns at full agreement: %s   best other: %s %d/%d\n",
                it, nrow(x), CLAIM[[it]], agree[[CLAIM[[it]]]], nrow(x),
                paste(full, collapse = ","), names(runner), runner, nrow(x)))
    if (!identical(full, CLAIM[[it]]) || nrow(x) != nrow(s1)) ok <- FALSE
}

cat("\nRoute B: one-factor CFA standardized loadings vs paper Table 3\n")
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
if (requireNamespace("lavaan", quietly = TRUE)) {
    fit <- lavaan::cfa("F =~ TTF1 + TTF2 + TTF3 + TTF4 + TTF5", data = w)
    std <- lavaan::standardizedSolution(fit)
    std <- std[std$op == "=~", ]
    for (i in seq_len(nrow(std)))
        cat(sprintf("  %-4s (%s)  published %.3f  live %.3f\n", std$rhs[i], CLAIM[[std$rhs[i]]],
                    PUB_LOAD[[CLAIM[[std$rhs[i]]]]], std$est.std[i]))
    cat("  (paper's loadings come from the full 7-factor model, so small residuals are expected;\n",
        "   Route B corroborates Q5 (highest) and Q6 (lowest); Q7/Q8/Q9 are close.)\n", sep = "")
} else cat("  lavaan not installed -- Route B skipped (Route A is decisive on its own)\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
