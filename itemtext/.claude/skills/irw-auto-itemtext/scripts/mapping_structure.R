# Usage: Rscript mapping_structure.R <table> [<group1_items> <group2_items> ...]
#   e.g. Rscript mapping_structure.R alsuhibani_2022_gcbs \
#          GCBS_01,GCBS_06,GCBS_11 GCBS_02,GCBS_07,GCBS_12
#
# Third verification route for an item-to-text mapping (see SKILL.md Step 5b),
# for the common case where the source publishes NO per-item statistics and the
# items all share one response scale -- so neither per-item means nor the
# response-range fingerprint can help.
#
# The idea: most multi-subscale instruments have a documented, fixed assignment
# of item NUMBER to subscale (GCBS items 1,6,11 = government malfeasance;
# UWES-9 items 1,2,5 = vigor; WHOQOL-BREF items 20,21,22 = social; ...). That
# assignment is a strong structural prediction about the DATA: items in the same
# subscale should correlate more with each other than with items outside it. If
# our item_text says GCBS_01 is a government-malfeasance item, the data should
# agree. A permuted mapping breaks the block structure.
#
# Same logic covers reverse-keyed items: an item whose text is negatively worded
# should correlate NEGATIVELY with the rest if the data are raw, or positively if
# the processing script already reverse-scored it. Either is informative; a
# negatively-worded item that behaves like every other item when the rest are raw
# is a red flag.
#
# With no groups given, prints the full correlation matrix and item-total
# correlations so the block structure can be read off directly.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Usage: Rscript mapping_structure.R <table> [group1 group2 ...]")
table <- args[1]
groups <- if (length(args) > 1) strsplit(args[-1], ",") else list()

df <- irw::irw_fetch(table)
df$resp <- suppressWarnings(as.numeric(df$resp))
df$id <- as.character(df$id)
df$item <- as.character(df$item)
if ("wave" %in% names(df) && length(unique(df$wave)) > 1) {
    w <- sort(unique(df$wave))[1]
    cat("NOTE: table has waves", paste(sort(unique(df$wave)), collapse = ", "),
        "-- using the earliest (wave =", w, ") so the structure is not blurred",
        "by repeated measurement.\n\n")
    df <- df[df$wave == w, ]
}

ids <- sort(unique(df$id))
items <- sort(unique(df$item))
mat <- matrix(NA_real_, nrow = length(ids), ncol = length(items),
              dimnames = list(ids, items))
mat[cbind(match(df$id, ids), match(df$item, items))] <- df$resp

cm <- stats::cor(mat, use = "pairwise.complete.obs")
tot <- rowSums(mat, na.rm = TRUE)
itc <- sapply(items, function(it) stats::cor(mat[, it], tot - ifelse(is.na(mat[, it]), 0, mat[, it]),
                                            use = "pairwise.complete.obs"))

cat("=== ", table, " (", length(items), " items, n = ", length(ids), ") ===\n\n", sep = "")
cat("--- corrected item-total correlations ---\n")
print(round(sort(itc), 2))
neg <- names(itc)[itc < 0]
if (length(neg) > 0) {
    cat("\n  NEGATIVE item-total: ", paste(neg, collapse = ", "),
        "\n  -> these behave as reverse-keyed *in the raw data*. Cross-check against",
        "\n     which items your item_text says are negatively worded.\n")
} else {
    cat("\n  No negative item-total correlations -- consistent with a scale that is",
        "\n  either all same-keyed or already reverse-scored by the processing script.\n")
}

cat("\n--- inter-item correlation matrix ---\n")
print(round(cm, 2))

if (length(groups) > 0) {
    cat("\n--- hypothesised subscale check ---\n")
    cat("For each item: mean correlation with its OWN group vs the best rival group.\n")
    cat("A correct mapping puts `own` highest for (nearly) every item.\n\n")
    assign <- rep(NA_integer_, length(items)); names(assign) <- items
    for (g in seq_along(groups)) assign[groups[[g]]] <- g
    ok <- 0; tested <- 0
    for (it in items) {
        if (is.na(assign[it])) next
        tested <- tested + 1
        ms <- sapply(seq_along(groups), function(g) {
            peers <- setdiff(groups[[g]], it)
            mean(cm[it, peers], na.rm = TRUE)
        })
        own <- assign[it]
        best <- which.max(ms)
        if (best == own) ok <- ok + 1
        cat(sprintf("  %-14s own(g%d)=%5.2f   best=g%d(%5.2f)   %s\n",
                    it, own, ms[own], best, ms[best],
                    ifelse(best == own, "ok", "<-- MISMATCH")))
    }
    cat(sprintf("\n  %d/%d items load strongest on their hypothesised subscale.\n", ok, tested))
}
