# verify_anh_2026_ai_adoption.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: the item_text shipped for AI1..AI8 is the wording printed
# against those same codes in PLOS ONE 10.1371/journal.pone.0340002 Table 3
# ("Measurement model assessment"), and those codes address the same eight
# columns that produced the live IRW table.
#
# The mapping is a two-link chain and each link is checked separately:
#
#   link A  live item code  <->  S1 File column name
#           Route 9 (response-frequency matching). The processing script
#           data/anh_2026_finwellbeing.py melts S1 columns AI1..AI8 by NAME,
#           but only the counts show what actually produced the live rows.
#           40 item x resp cells must match exactly. Each item's 5-tuple of
#           counts is unique across the eight items, so this separates EVERY
#           item from every other -- a swap of any two would break it.
#
#   link B  S1 column name  <->  Table 3 row label
#           A literal code-label identity (Table 3's first column is
#           "Variable code" and prints AI1..AI8), not an order inference.
#           Corroborated numerically by reproducing Table 3's eight published
#           outer loadings from S1. See the caveat printed at the end.
#
# NOT verified here: that the English shipped is what respondents read. The
# study was administered in Vietnamese (translation/back-translation, sec 3.3)
# and no Vietnamese wording exists in the deposit -- text_source is
# translated_substitute and that is a provenance fact, not a testable one.
#
# Uses server-side aggregates only; it never exports the IRW table.

suppressMessages(library(irw))

TABLE <- "anh_2026_ai_adoption"
ITEMS <- paste0("AI", 1:8)

# Published outer loadings, PLOS ONE 10.1371/journal.pone.0340002 Table 3.
PUBLISHED_LOADING <- c(AI1 = 0.703, AI2 = 0.710, AI3 = 0.738, AI4 = 0.747,
                       AI5 = 0.776, AI6 = 0.787, AI7 = 0.742, AI8 = 0.841)

S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0340002.s001")

## ---- live side: one GROUP BY, no export ---------------------------------
tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                   "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS INT64) AS resp,",
                   "COUNT(*) AS n FROM `%s`",
                   "WHERE resp IS NOT NULL GROUP BY item, resp"),
             tbl$qualified_reference)
live <- as.data.frame(irw:::.irw_query_tibble(q))
live_tab <- matrix(0L, nrow = 8, ncol = 5, dimnames = list(ITEMS, 1:5))
for (i in seq_len(nrow(live)))
    live_tab[live$item[i], as.character(live$resp[i])] <- as.integer(live$n[i])

## ---- source side: S1 File ------------------------------------------------
s1 <- read.csv(S1, stringsAsFactors = FALSE)
stopifnot(all(ITEMS %in% names(s1)))
src_tab <- t(sapply(ITEMS, function(k) table(factor(s1[[k]], levels = 1:5))))
dimnames(src_tab) <- list(ITEMS, 1:5)

## ---- link A --------------------------------------------------------------
cat("== link A: live item code <-> S1 column, response-frequency match ==\n")
cat(sprintf("%-5s %-22s %-22s %s\n", "item", "S1 counts (1..5)", "live counts (1..5)", "ok"))
okA <- TRUE
for (k in ITEMS) {
    same <- identical(as.integer(src_tab[k, ]), as.integer(live_tab[k, ]))
    okA <- okA && same
    cat(sprintf("%-5s %-22s %-22s %s\n", k,
                paste(src_tab[k, ], collapse = "/"),
                paste(live_tab[k, ], collapse = "/"),
                if (same) "yes" else "NO"))
}
# the counts must also be a DISTINGUISHING signature, not just equal
uniq <- nrow(unique(src_tab)) == 8L
cat(sprintf("all 40 cells match: %s | the 8 count-signatures are distinct: %s\n\n",
            okA, uniq))

## ---- link B --------------------------------------------------------------
cat("== link B: S1 column <-> Table 3 row, published outer loadings ==\n")
Z <- scale(as.matrix(s1[, ITEMS]))
comp <- rowSums(Z)
obs <- sapply(ITEMS, function(k) cor(s1[[k]], comp))
cat(sprintf("%-5s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (k in ITEMS)
    cat(sprintf("%-5s %10.3f %10.3f %8.3f\n", k,
                PUBLISHED_LOADING[[k]], obs[[k]], obs[[k]] - PUBLISHED_LOADING[[k]]))
worst <- max(abs(obs - PUBLISHED_LOADING))
rho <- cor(rank(obs), rank(PUBLISHED_LOADING))
cat(sprintf("largest deviation: %.3f | Spearman rho: %.3f\n\n", worst, rho))

cat("What link B does NOT establish: the composite used here is a unit-weight sum,\n",
    "not the PLS mode-A construct score of the paper's full structural model, so\n",
    "the three near-tied loadings AI1/AI2/AI3 (0.703/0.710/0.738) do not order\n",
    "reliably. Link B is corroboration; what actually ties S1 columns to Table 3\n",
    "rows is that Table 3's own 'Variable code' column prints AI1..AI8 verbatim.\n\n", sep = "")

pass <- okA && uniq && worst <= 0.05
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
