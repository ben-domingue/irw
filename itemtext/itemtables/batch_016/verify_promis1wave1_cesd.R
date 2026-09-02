## verify_promis1wave1_cesd.R  --  batch_016, issue #1831
##
## Re-derives the shipped text from the cached study codebook via
## rederive_cesd.py and diffs it, so this checks the mapping rather than the
## plumbing: an evidence string cannot be re-run, a rebuild can.
##
## CES-D sits in the codebook's legacy-items tables rather than the PROMIS bank
## sections, so it has its own re-derivation (see rederive_cesd.py for the two
## layout traps) and its own verify script.
##
## Run from itemtext/:
##   Rscript itemtables/batch_016/verify_promis1wave1_cesd.R
##   Rscript itemtables/batch_016/verify_promis1wave1_cesd.R --resp-csv <path>
suppressMessages({library(jsonlite)})

TBL <- "promis1wave1_cesd"
DIR <- "itemtables/batch_016"
CSV <- file.path(DIR, paste0(TBL, "__items.csv"))
JSN <- file.path(DIR, "rederived_cesd.json")
fail <- character(0)

a <- commandArgs(trailingOnly = TRUE)
i <- match("--resp-csv", a)
resp_csv <- if (!is.na(i)) a[i + 1] else NA_character_

if (!file.exists(JSN)) system2("python3", file.path(DIR, "rederive_cesd.py"))
red <- fromJSON(JSN, simplifyVector = FALSE)
src <- red$items
it  <- read.csv(CSV, stringsAsFactors = FALSE)
it$item <- as.character(it$item)
codes <- unique(it$item)

cat("=== 1. item_text and instructions re-derived from the codebook ===\n")
bad <- 0
for (code in codes) {
    for (f in c("item_text", "instructions")) {
        want <- if (f == "item_text") src[[code]]$stem else src[[code]]$instructions
        got  <- unique(it[[f]][it$item == code])
        if (is.null(want) || length(got) != 1 || !identical(got, want)) {
            bad <- bad + 1
            if (bad <= 3) cat(sprintf("  MISMATCH %s %s\n    source : %s\n    shipped: %s\n",
                code, f, substr(paste(want, collapse = "|"), 1, 80),
                substr(paste(got, collapse = "|"), 1, 80)))
        }
    }
}
cat(sprintf("  cells compared: %d | mismatches: %d\n", 2 * length(codes), bad))
if (bad) fail <- c(fail, "item_text/instructions mismatch")

cat("\n=== 2. option_text per resp level ===\n")
obad <- 0; cells <- 0
for (code in codes) {
    rows <- it[it$item == code, ]
    rows <- rows[order(rows$resp), ]
    want <- unname(unlist(src[[code]]$opts[as.character(rows$resp)]))
    cells <- cells + nrow(rows)
    if (length(want) != nrow(rows) || !identical(unname(rows$option_text), want)) obad <- obad + 1
}
cat(sprintf("  option cells checked: %d | items with a mismatch: %d\n", cells, obad))
if (obad) fail <- c(fail, "option_text mismatch")

cat("\n=== 3. one shared response set across the scale ===\n")
cat("  items sharing it:", red$items_sharing_it, "of", length(src),
    "| deviating:", if (length(red$items_not_sharing_it)) paste(unlist(red$items_not_sharing_it),
    collapse = ",") else "none", "\n")
if (length(red$items_not_sharing_it)) fail <- c(fail, "an item's option set differs from the scale's")

cat("\n=== 4. item and resp sets vs live, and the reverse-item fingerprint ===\n")
live <- if (!is.na(resp_csv) && nzchar(resp_csv)) {
    cat("  (using local response CSV:", resp_csv, ")\n")
    read.csv(resp_csv, stringsAsFactors = FALSE)
} else tryCatch(irw::irw_fetch(TBL), error = function(e) NULL)

if (is.null(live) || !nrow(live)) {
    cat("  live data unavailable -- sets and fingerprint NOT checked\n")
    fail <- c(fail, "live data unavailable")
} else {
    live$item <- as.character(live$item)
    si <- identical(sort(codes), sort(unique(live$item)))
    sr <- identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp))))
    cat("  item set identical:", si, "| resp set identical:", sr, "| live rows:", nrow(live), "\n")
    if (!si || !sr) fail <- c(fail, "live set mismatch")

    # The canonical CES-D words items 4, 8, 12 and 16 positively and the other
    # 16 negatively. The shipped stems put the positive wording at exactly those
    # four numbers, so the data should show them as the only reverse-scoring
    # items -- a check on the code-to-text tie that does not use the codebook.
    w <- reshape(live[, c("id", "item", "resp")], idvar = "id", timevar = "item",
                 direction = "wide")
    m <- as.matrix(w[, -1]); colnames(m) <- sub("resp.CESD", "", colnames(m))
    m <- m[, order(as.integer(colnames(m)))]
    cm  <- cor(m, use = "pairwise.complete.obs")
    avg <- (rowSums(cm, na.rm = TRUE) - 1) / (ncol(cm) - 1)
    POS <- c("4", "8", "12", "16")
    pos <- avg[names(avg) %in% POS]; neg <- avg[!names(avg) %in% POS]
    cat(sprintf("  mean r with the other 19: items 4/8/12/16 = [%+.3f, %+.3f]; other 16 = [%+.3f, %+.3f]\n",
                min(pos), max(pos), min(neg), max(neg)))
    stems <- vapply(POS, function(k) src[[paste0("CESD", k)]]$stem, "")
    cat("  shipped stems at those four numbers:", paste(sQuote(stems), collapse = ", "), "\n")
    if (!(max(pos) < 0 && min(neg) > 0)) {
        cat("  the four do NOT separate cleanly from the rest\n")
        fail <- c(fail, "reverse-item fingerprint does not match the canonical CES-D positions")
    } else {
        cat("  clean separation: those four are the only negatively correlating items\n")
    }
}

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
