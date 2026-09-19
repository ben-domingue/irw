# verify_zeng_2026_gai_role_adapt.R -- Step 5b mapping check (batch_248)
#
# Claim: IRW item RA<k> is S1 File column Q<9+k>, which the paper's Table 2 prints as
# "RA<k>(Q<9+k>)" beside its item wording (Role Adaptation block, Q10-Q14).
# The processing script (data/zeng_2026_gai_learning.py) renames Q10..Q14 -> RA1..RA5
# BY NAME (dict(zip(q_cols, item_names))), not by spreadsheet position. This block IS one
# of the permuted ones in S1: the sheet's physical column order is Q10,Q11,Q14,Q12,Q13, so
# a positional rename would have put Q14 under RA3, Q12 under RA4 and Q13 under RA5.
# Route A below is what shows the live data followed the names, not the positions.
#
# Route A (decisive for code -> S1 column): for every live RA item, count id-level exact
#   agreement with EVERY Q5..Q39 column of S1. The mapping holds iff each item agrees
#   207/207 with its claimed column and with no other column.
# Route B (corroboration of S1 column -> paper's analysis): one-factor CFA on the live
#   items vs the paper's Table 3 standardized loadings for Q10..Q14. Q11 (0.667) and
#   Q14 (0.733) are distinctive; Q10/Q12/Q13 (0.934/0.899/0.903) are not separable by it.
# What neither route establishes: that Table 2's printed wording is what sits beside each
#   Q code -- that tie is the paper's own explicit "RAk(Qn)" label (paper_explicit). Also,
#   that S1's header names themselves are correct is taken from the deposit; Route B
#   shows only that the paper's own Table 3 analysis agrees with those names.
#
# Note: this fetches the live table (1,035 rows) with irw_fetch -- a deliberate, tiny export,
# because an id-level comparison cannot be done from server-side set aggregates.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "zeng_2026_gai_role_adapt"
CLAIM <- setNames(paste0("Q", 10:14), paste0("RA", 1:5))
PUB_LOAD <- c(Q10 = 0.934, Q11 = 0.667, Q12 = 0.899, Q13 = 0.903, Q14 = 0.733)  # Table 3, Std. (Q10 row also carries CR 0.918 / AVE 0.695; its SMC 0.872 = 0.934^2)

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]

tf <- tempfile(fileext = ".xlsx")
download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346696.s001",
              tf, mode = "wb", quiet = TRUE)
s1 <- as.data.frame(read_excel(tf))
qcols <- paste0("Q", 5:39)
cat(sprintf("S1: %d rows; live: %d ids, %d rows\n", nrow(s1), length(unique(d$id)), nrow(d)))
cat("S1 physical order of the RA block:", paste(names(s1)[names(s1) %in% CLAIM], collapse = ","), "\n")

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
    fit <- lavaan::cfa("F =~ RA1 + RA2 + RA3 + RA4 + RA5", data = w)
    std <- lavaan::standardizedSolution(fit)
    std <- std[std$op == "=~", ]
    for (i in seq_len(nrow(std)))
        cat(sprintf("  %-4s (%s)  published %.3f  live %.3f\n", std$rhs[i], CLAIM[[std$rhs[i]]],
                    PUB_LOAD[[CLAIM[[std$rhs[i]]]]], std$est.std[i]))
    cat("  (paper's loadings come from the full 7-factor model, so small residuals are expected;\n",
        "   Route B corroborates the two low-loading items Q11 and Q14 but does not separate Q10/Q12/Q13.)\n", sep = "")
} else cat("  lavaan not installed -- Route B skipped (Route A is decisive on its own)\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
