# verify_zeng_2026_gai_self_efficacy.R -- Step 5b mapping check (batch_249)
# (adapted from references/verify_template.R)
#
# Claim: IRW item SE<k> is S1 File column Q<14+k>, which the paper's Table 2 prints as
# "SE<k>(Q<14+k>)" beside its item wording (Self Efficacy block, Q15-Q19).
# The processing script (data/zeng_2026_gai_learning.py) renames Q15..Q19 -> SE1..SE5
# BY NAME (dict(zip(q_cols, item_names))), not by spreadsheet position. S1's physical
# column order is permuted in the TTF (Q5,Q6,Q9,Q7,Q8) and RA (Q10,Q11,Q14,Q12,Q13)
# blocks; the SE block sits in order (Q15..Q19), and the check below is by NAME and
# id-level agreement, so it does not depend on position either way.
#
# Route A (decisive for code -> S1 column): for every live SE item, count id-level exact
#   agreement with EVERY Q5..Q39 column of S1. The mapping holds iff each item agrees
#   207/207 with its claimed column and with no other column.
# Route B (corroboration only): one-factor CFA on the live items vs the paper's Table 3
#   standardized loadings for Q15..Q19 (0.919/0.865/0.899/0.903/0.906) -- too tightly
#   bunched to separate items on its own (only Q16 stands apart).
# What neither route establishes: that Table 2's printed wording is what sits beside each
#   Q code -- that tie is the paper's own explicit "SEk(Qn)" label (paper_explicit) --
#   nor that the authors' English matches the administered Chinese.
#
# Note: this fetches the live table (1,035 rows) with irw_fetch -- a deliberate, tiny export,
# because an id-level comparison cannot be done from server-side set aggregates.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "zeng_2026_gai_self_efficacy"
CLAIM <- setNames(paste0("Q", 15:19), paste0("SE", 1:5))
PUB_LOAD <- c(Q15 = 0.919, Q16 = 0.865, Q17 = 0.899, Q18 = 0.903, Q19 = 0.906)  # Table 3, Std.

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]

tf <- tempfile(fileext = ".xlsx")
download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346696.s001",
              tf, mode = "wb", quiet = TRUE)
s1 <- as.data.frame(read_excel(tf))
qcols <- paste0("Q", 5:39)
cat(sprintf("S1: %d rows; live: %d ids, %d rows\n", nrow(s1), length(unique(d$id)), nrow(d)))
cat("S1 physical order of the SE block:", paste(names(s1)[names(s1) %in% CLAIM], collapse = ","), "\n")

ok <- TRUE
cat("\nRoute A: id-level exact agreement of each live item with every S1 Q column\n")
for (it in names(CLAIM)) {
    x <- d[d$item == it, ]
    if (any(is.na(match(x$id, s1$Code)))) ok <- FALSE
    src <- s1[match(x$id, s1$Code), qcols]
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
    fit <- lavaan::cfa("F =~ SE1 + SE2 + SE3 + SE4 + SE5", data = w)
    std <- lavaan::standardizedSolution(fit)
    std <- std[std$op == "=~", ]
    for (i in seq_len(nrow(std)))
        cat(sprintf("  %-4s (%s)  published %.3f  live %.3f\n", std$rhs[i], CLAIM[[std$rhs[i]]],
                    PUB_LOAD[[CLAIM[[std$rhs[i]]]]], std$est.std[i]))
    cat("  (paper's loadings come from the full 7-factor model, so small residuals are expected;\n",
        "   Route B corroborates only -- the loadings are too close to separate items.)\n", sep = "")
} else cat("  lavaan not installed -- Route B skipped (Route A is decisive on its own)\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
