# Usage: Rscript item_stats.R <table> [<table> ...]
#
# Prints per-item descriptive statistics from the LIVE response data, in the
# form papers publish them, so an item-to-text mapping can be VERIFIED against
# the data instead of assumed.
#
# Why this exists: validate_items.R and audit_batch.R both only check that the
# *set* of item codes and resp values matches. Neither can tell a verified
# mapping from a guessed one -- if item_text for items 3 and 5 were swapped,
# every existing check still passes. But most papers publish a per-item table
# (M, SD, floor/ceiling %, item-total correlation, factor loadings). Matching
# that table against these numbers pins the mapping item-by-item.
#
# Read the output next to the paper's per-item table:
#   - `mean`/`sd` usually identify each item outright.
#   - When two items have near-identical means (a real occurrence), `floor_pct`
#     and `ceiling_pct` break the tie -- do not declare a match on means alone
#     if any two items are within ~0.02 of each other. The script flags those.
#   - Expect small residuals if the paper analyzed an imputed file while the
#     IRW script dropped imputed cells (or vice versa). Order and relative
#     spacing are what matter, not the third decimal.
#
# A source with no per-item statistics has no numeric verification route; record
# that honestly rather than treating "couldn't check" as "checked".

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Usage: Rscript item_stats.R <table> [<table> ...]")

stats_block <- function(df, label) {
    df$resp <- suppressWarnings(as.numeric(df$resp))
    lo <- min(df$resp, na.rm = TRUE)
    hi <- max(df$resp, na.rm = TRUE)
    items <- sort(unique(df$item))
    out <- do.call(rbind, lapply(items, function(it) {
        v <- df$resp[df$item == it]
        v <- v[!is.na(v)]
        # floor/ceiling are computed against each item's OWN observed range as
        # well as the scale-wide range; papers differ on which they report.
        data.frame(
            item        = it,
            n           = length(v),
            mean        = sprintf("%.2f", mean(v)),
            sd          = sprintf("%.2f", stats::sd(v)),
            min         = min(v),
            max         = max(v),
            floor_pct   = sprintf("%.1f", 100 * mean(v == min(v))),
            ceiling_pct = sprintf("%.1f", 100 * mean(v == max(v))),
            floor_scale = sprintf("%.1f", 100 * mean(v == lo)),
            ceil_scale  = sprintf("%.1f", 100 * mean(v == hi)),
            stringsAsFactors = FALSE
        )
    }))
    cat("--- ", label, " (", length(items), " items) ---\n", sep = "")
    print(out, row.names = FALSE)

    # Warn where means alone cannot distinguish two items.
    m <- sort(as.numeric(out$mean))
    ties <- which(diff(m) <= 0.02)
    if (length(ties) > 0) {
        tied_vals <- unique(m[sort(c(ties, ties + 1))])
        tied_items <- out$item[as.numeric(out$mean) %in% tied_vals]
        cat("\n  NOTE: means within 0.02 of each other -- means alone cannot",
            "tell these apart;\n  use floor/ceiling % to separate them:",
            paste(tied_items, collapse = ", "), "\n")
    }
    cat("\n")
}

for (table in args) {
    cat("=== ", table, " ===\n", sep = "")
    df <- tryCatch(irw::irw_fetch(table), error = function(e) NULL)
    if (is.null(df)) {
        cat("  could not fetch\n\n")
        next
    }

    # A paper's per-item table almost always describes ONE wave (usually
    # baseline), while the IRW table may pool several. Comparing pooled stats
    # against a single-wave table produces spurious mismatches, so split.
    if ("wave" %in% names(df) && length(unique(df$wave)) > 1) {
        cat("  table has ", length(unique(df$wave)), " waves -- a paper's",
            " per-item table usually reports ONE of them (typically the",
            " earliest).\n  Compare against the matching wave, not the",
            " pooled block.\n\n", sep = "")
        stats_block(df, "ALL WAVES POOLED")
        for (w in sort(unique(df$wave))) {
            stats_block(df[df$wave == w, ], paste0("wave = ", w))
        }
    } else {
        stats_block(df, "all rows")
    }
}
