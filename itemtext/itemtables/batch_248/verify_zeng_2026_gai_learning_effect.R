# verify_zeng_2026_gai_learning_effect.R -- Step 5b mapping check (batch_248)
#
# Claim: IRW item LE<k> is S1 File column Q<34+k>, which the paper's Table 2 prints as
# "LE<k>(Q<34+k>)" beside its item wording (Learning Effect block, Q35-Q39).
# The processing script (data/zeng_2026_gai_learning.py) renames Q35..Q39 -> LE1..LE5 BY
# NAME (dict(zip(q_cols, item_names))), not by spreadsheet position. The S1 sheet's
# physical column order is permuted elsewhere (Q5,Q6,Q9,Q7,Q8; Q10,Q11,Q14,Q12,Q13) but
# Q35..Q39 sit in order at the end of the sheet; Route A would catch it either way.
#
# Route A (decisive for code -> Q column): for every live LE item, count id-level exact
#   agreement with EVERY Q5..Q39 column of S1. The mapping holds iff each item agrees
#   207/207 with its claimed column and with no other column. Needed because per-item
#   means cannot separate Q38 (4.556) from Q39 (4.551) or Q35 (4.575).
# Route B (corroboration only): one-factor CFA loadings vs paper Table 3 (Q35..Q39 Std.
#   0.906/0.894/0.900/0.917/0.906) -- too close together to separate items on its own.
# What neither route establishes: that Table 2's printed wording is what sits beside each
#   Q code -- that tie is the paper's own explicit "LEk(Qn)" label (paper_explicit).
#
# Note: irw_fetch() exports the live table (207 ids x 5 items = 1035 rows; tiny).

suppressMessages({ library(irw); library(readxl) })

TABLE <- "zeng_2026_gai_learning_effect"
CLAIM <- setNames(paste0("Q", 35:39), paste0("LE", 1:5))
PUB_LOAD <- c(Q35 = 0.906, Q36 = 0.894, Q37 = 0.900, Q38 = 0.917, Q39 = 0.906)  # Table 3, Std.

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]

tf <- tempfile(fileext = ".xlsx")
download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346696.s001",
              tf, mode = "wb", quiet = TRUE)
s1 <- as.data.frame(read_excel(tf))
qcols <- paste0("Q", 5:39)
cat(sprintf("S1: %d rows; live: %d ids, %d rows\n", nrow(s1), length(unique(d$id)), nrow(d)))

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
    if (!identical(full, CLAIM[[it]])) ok <- FALSE
}

cat("\nRoute B: one-factor CFA standardized loadings vs paper Table 3 (corroboration only)\n")
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
if (requireNamespace("lavaan", quietly = TRUE)) {
    fit <- lavaan::cfa("F =~ LE1 + LE2 + LE3 + LE4 + LE5", data = w)
    std <- lavaan::standardizedSolution(fit)
    std <- std[std$op == "=~", ]
    for (i in seq_len(nrow(std)))
        cat(sprintf("  %-4s (%s)  published %.3f  live %.3f\n", std$rhs[i], CLAIM[[std$rhs[i]]],
                    PUB_LOAD[[CLAIM[[std$rhs[i]]]]], std$est.std[i]))
    cat("  (paper's loadings come from the full 7-factor model; they span only 0.894-0.917,\n",
        "   so Route B does not separate the five items -- Route A is the decisive check.)\n", sep = "")
} else cat("  lavaan not installed -- Route B skipped (Route A is decisive on its own)\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
