# Step 5b for the seven earja_2026_* tables (Zenodo 10.5281/zenodo.23763732).
#
# THE CLAIM. Each item's text is tied to its code by the deposit's own labels,
# twice over: the questionnaire PDF's "Code" column reads AT1..AT5, AN1..AN5,
# ... and the response CSV's column headers are the same strings. The
# processing script lowercases them and changes nothing else. So no step in the
# chain is positional, and the swap this check exists to catch -- item_text for
# items 3 and 5 exchanged -- would require the SOURCE to be internally wrong.
#
# WHAT THIS SCRIPT CAN AND CANNOT ADD. There is no published per-item statistic
# to predict against: the deposit is standalone, with no article DOI and no
# related identifier, so the template's preferred route (published means vs
# observed means) does not exist here. The available route is internal: each
# item should correlate more with its own block's score than with any other
# block's. That pins BLOCK MEMBERSHIP -- it would catch an item text taken from
# the wrong construct -- and it cannot separate two items inside one block from
# each other. Recorded as PARTIAL for that reason.
#
# Reads the staged CSVs by default so it is runnable before upload; point it at
# a directory of the published tables to re-run later.
#
#   Rscript verify_earja_2026_ai_streamer.R [resp_dir]

args <- commandArgs(trailingOnly = TRUE)
RESP_DIR <- if (length(args)) args[1] else "../irw_output"

BLOCKS <- list(
    earja_2026_algorithmic_transparency = "at",
    earja_2026_anthropomorphism         = "an",
    earja_2026_perceived_risk           = "pr",
    earja_2026_trust                    = "tr",
    earja_2026_fomo                     = "fo",
    earja_2026_purchase_intention       = "pi",
    earja_2026_ai_literacy              = "al")

wide <- list()
for (tbl in names(BLOCKS)) {
    d <- read.csv(file.path(RESP_DIR, paste0(tbl, ".csv")),
                  stringsAsFactors = FALSE)
    w <- reshape(d[, c("id", "item", "resp")], idvar = "id",
                 timevar = "item", direction = "wide")
    colnames(w) <- sub("^resp\\.", "", colnames(w))
    rownames(w) <- w$id
    wide[[tbl]] <- w[order(w$id), setdiff(colnames(w), "id"), drop = FALSE]
}

ids <- rownames(wide[[1]])
stopifnot(all(vapply(wide, function(w) identical(rownames(w), ids), logical(1))))
cat(sprintf("%d respondents, %d blocks, %d items total\n\n", length(ids),
            length(wide), sum(vapply(wide, ncol, integer(1)))))

# Per-item descriptives -- print the numbers, so the reader can judge.
cat(sprintf("%-6s %-34s %6s %6s %5s %5s\n",
            "item", "block", "mean", "sd", "min", "max"))
for (tbl in names(wide))
    for (it in colnames(wide[[tbl]])) {
        v <- wide[[tbl]][[it]]
        cat(sprintf("%-6s %-34s %6.2f %6.2f %5d %5d\n",
                    it, tbl, mean(v), sd(v), min(v), max(v)))
    }

# Block scores, then each item against every block (its own block's score has
# the item itself removed, or the comparison is rigged in its favour).
scores <- lapply(wide, function(w) rowSums(w))
cat("\nitem-to-block correlations (own block corrected for the item itself)\n")
cat(sprintf("%-6s %-20s %7s | %-20s %7s %s\n",
            "item", "own block", "r_own", "best other block", "r_other", "ok"))

worst_margin <- Inf
n_items <- 0
for (tbl in names(wide)) {
    w <- wide[[tbl]]
    for (it in colnames(w)) {
        own <- scores[[tbl]] - w[[it]]
        r_own <- cor(w[[it]], own)
        others <- setdiff(names(wide), tbl)
        r_oth <- vapply(others, function(o) cor(w[[it]], scores[[o]]),
                        numeric(1))
        best <- others[which.max(r_oth)]
        margin <- r_own - max(r_oth)
        worst_margin <- min(worst_margin, margin)
        n_items <- n_items + 1
        cat(sprintf("%-6s %-20s %7.3f | %-20s %7.3f %s\n",
                    it, BLOCKS[[tbl]], r_own, BLOCKS[[best]], max(r_oth),
                    if (margin > 0) "yes" else "NO"))
    }
}

cat(sprintf("\n%d items checked; smallest own-minus-other margin %.3f\n",
            n_items, worst_margin))
cat("What this establishes: every item sits with the block its text says it",
    "belongs to.\n", sep = " ")
cat("What it does NOT establish: the order of items WITHIN a block. That rests",
    "on the\nliteral code match between the questionnaire PDF's Code column and",
    "the response\nfile's headers, which is the source's own labelling and not",
    "a positional guess.\n", sep = " ")

cat(if (worst_margin > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
