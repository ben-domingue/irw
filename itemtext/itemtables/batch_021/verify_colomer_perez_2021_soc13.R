# verify_colomer_perez_2021_soc13.R
#
# CLAIM UNDER TEST: the numeric suffix in each IRW item code (INVSOC1..SOC13)
# is the canonical SOC-13 item number, so item_text for item n is SOC-13 item n.
#
# FALSIFIABLE PREDICTION: the SOC-13 is scored by reversing exactly items
# 1, 2, 3, 7 and 10 (the negatively worded set; stated as such in Rodriguez-Prat
# et al., Health Qual Life Outcomes 2022;20:2, CC BY: "the negatively worded
# items (Items 1, 2, 3, 7, and 10)"). The study's own deposited file carries the
# authors' SOCTOTAL. If the code numbers are the instrument's numbers and the
# item values are stored raw, then reversing exactly those five columns and no
# others must reproduce SOCTOTAL for every respondent -- and no other subset of
# the 8192 possible ones should do so.
#
# This does NOT establish the order of items WITHIN either polarity class:
# nothing here distinguishes SOC5 from SOC6, or INVSOC2 from INVSOC3.

suppressMessages(library(irw))

TABLE <- "colomer_perez_2021_soc13"
COLS  <- c("INVSOC1","INVSOC2","INVSOC3","SOC4","SOC5","SOC6","INVSOC7",
           "SOC8","SOC9","SOC10","SOC11","SOC12","SOC13")
EXPECTED_REVERSED <- c("INVSOC1","INVSOC2","INVSOC3","INVSOC7","SOC10")  # items 1,2,3,7,10

# 1. The live item codes are the source file's column names (data/colomer_perez_2021_self_care.py
#    melts them unchanged). Confirm server-side, without exporting the table.
sets <- irw::irw_table_sets(TABLE, source = "core")
live <- sort(as.character(sets$items))
cat("live item codes  :", paste(live, collapse = ", "), "\n")
cat("source .sav cols :", paste(sort(COLS), collapse = ", "), "\n")
codes_ok <- identical(live, sort(COLS))
cat("codes identical to source columns:", codes_ok, "\n\n")

# 2. Fetch the study's own S1 Dataset (PLOS ONE 10.1371/journal.pone.0260827, CC BY).
f <- file.path(tempdir(), "colomer_s001.sav")
if (!file.exists(f))
    utils::download.file(paste0("https://journals.plos.org/plosone/article/file",
                                "?type=supplementary&id=10.1371/journal.pone.0260827.s001"),
                         f, quiet = TRUE, mode = "wb")
d <- as.data.frame(haven::read_sav(f))
d <- d[stats::complete.cases(d[, c(COLS, "SOCTOTAL")]), ]
cat("respondents in source file:", nrow(d), "\n\n")

# 3. Brute force every one of the 2^13 reversal subsets against the authors' SOCTOTAL.
X <- as.matrix(d[, COLS]); tot <- d$SOCTOTAL
exact <- integer(0); labs <- character(0)
for (m in 0:(2^13 - 1)) {
    sel <- as.logical(bitwAnd(m, 2^(0:12)))
    Y <- X; if (any(sel)) Y[, sel] <- 8 - Y[, sel]
    exact <- c(exact, sum(rowSums(Y) == tot))
    labs  <- c(labs, paste(COLS[sel], collapse = "+"))
}
o <- order(-exact)[1:4]
cat("best reversal subsets, by exact SOCTOTAL matches out of", nrow(d), ":\n")
for (i in o) cat(sprintf("  %5d/%d  {%s}\n", exact[i], nrow(d),
                         if (nchar(labs[i])) labs[i] else "(none)"))
winner <- sort(strsplit(labs[o[1]], "+", fixed = TRUE)[[1]])
n_perfect <- sum(exact == nrow(d))
cat("\nsubsets reproducing SOCTOTAL for EVERY respondent:", n_perfect, "\n")
cat("winning subset:", paste(winner, collapse = ", "), "\n")
cat("expected      :", paste(sort(EXPECTED_REVERSED), collapse = ", "), "\n\n")

# 4. Corroborating sign pattern: item-rest correlations against the 8 positive items.
pos <- setdiff(COLS, EXPECTED_REVERSED)
cat("item-rest correlations against the sum of the 8 positively worded items:\n")
for (cn in COLS) {
    rest <- rowSums(d[, setdiff(pos, cn), drop = FALSE])
    cat(sprintf("  %-9s %+0.3f  %s\n", cn, stats::cor(d[[cn]], rest),
                if (cn %in% EXPECTED_REVERSED) "(predicted negative)" else "(predicted positive)"))
}

signs_ok <- all(vapply(COLS, function(cn) {
    rest <- rowSums(d[, setdiff(pos, cn), drop = FALSE])
    r <- stats::cor(d[[cn]], rest)
    if (cn %in% EXPECTED_REVERSED) r < 0 else r > 0
}, logical(1)))
cat("\nall 13 signs as predicted:", signs_ok, "\n")

cat("\nNote: this pins the POLARITY CLASS of every item (5 reverse-worded vs 8\n",
    "positively worded, 1 of 1287 possible 5-subsets) and shows the values are\n",
    "stored raw rather than pre-reversed. It does NOT distinguish items within a\n",
    "class -- SOC5 vs SOC6, or INVSOC2 vs INVSOC3, are not separated by anything\n",
    "here. Status is therefore PARTIAL, not VERIFIED.\n", sep = "")

pass <- codes_ok && n_perfect == 1 &&
        identical(winner, sort(EXPECTED_REVERSED)) && signs_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
