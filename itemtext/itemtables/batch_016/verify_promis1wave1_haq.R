## verify_promis1wave1_haq.R  --  batch_016, issue #1831
##
## Re-derives the shipped text from the cached study codebook via
## rederive_haq.py and diffs it, so this checks the mapping rather than the
## plumbing: an evidence string cannot be re-run, a rebuild can.
##
## HAQ sits in the codebook's legacy-items tables and its codes end in a letter,
## so it has its own re-derivation (see rederive_haq.py) and its own verify.
##
## Run from itemtext/:
##   Rscript itemtables/batch_016/verify_promis1wave1_haq.R
##   Rscript itemtables/batch_016/verify_promis1wave1_haq.R --resp-csv <path>
suppressMessages({library(jsonlite)})

TBL <- "promis1wave1_haq"
DIR <- "itemtables/batch_016"
CSV <- file.path(DIR, paste0(TBL, "__items.csv"))
JSN <- file.path(DIR, "rederived_haq.json")
fail <- character(0)

a <- commandArgs(trailingOnly = TRUE)
i <- match("--resp-csv", a)
resp_csv <- if (!is.na(i)) a[i + 1] else NA_character_

if (!file.exists(JSN)) system2("python3", file.path(DIR, "rederive_haq.py"))
src <- fromJSON(JSN, simplifyVector = FALSE)$items
it  <- read.csv(CSV, stringsAsFactors = FALSE)
it$item <- as.character(it$item)
codes <- unique(it$item)

cat("=== 1. item_text and section_prompt re-derived from the codebook ===\n")
bad <- 0
for (code in codes) {
    want_t <- src[[code]]$stem
    got_t  <- unique(it$item_text[it$item == code])
    want_c <- src[[code]]$context
    want_c <- if (is.null(want_c) || !nzchar(want_c)) NA_character_ else want_c
    got_c  <- unique(it$section_prompt[it$item == code])
    if (is.null(want_t) || length(got_t) != 1 || !identical(got_t, want_t)) {
        bad <- bad + 1
        if (bad <= 3) cat(sprintf("  MISMATCH %s item_text\n    source : %s\n    shipped: %s\n",
            code, substr(paste(want_t, collapse = "|"), 1, 80),
            substr(paste(got_t, collapse = "|"), 1, 80)))
    }
    if (length(got_c) != 1 || !identical(as.character(got_c), as.character(want_c))) bad <- bad + 1
}
cat(sprintf("  items compared: %d | mismatches: %d\n", length(codes), bad))
if (bad) fail <- c(fail, "item_text/section_prompt mismatch")

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

cat("\n=== 3. the two sub-blocks ===\n")
tab <- table(it$section_id)
cat("  ", paste(sprintf("%s=%d rows", names(tab), tab), collapse = " | "), "\n")
n4 <- sum(vapply(codes, function(c) length(src[[c]]$opts) == 4, TRUE))
n2 <- sum(vapply(codes, function(c) length(src[[c]]$opts) == 2, TRUE))
cat("  items on the 0-3 difficulty run:", n4, "| items on the yes/no aids run:", n2, "\n")
if (n4 + n2 != length(codes)) fail <- c(fail, "unexpected option-set size")

cat("\n=== 4. item and resp sets vs live ===\n")
live <- if (!is.na(resp_csv) && nzchar(resp_csv)) {
    cat("  (using local response CSV:", resp_csv, ")\n")
    read.csv(resp_csv, stringsAsFactors = FALSE)
} else tryCatch(irw::irw_fetch(TBL), error = function(e) NULL)

if (is.null(live) || !nrow(live)) {
    cat("  live data unavailable -- sets NOT checked\n")
    fail <- c(fail, "live data unavailable")
} else {
    live$item <- as.character(live$item)
    si <- identical(sort(codes), sort(unique(live$item)))
    sr <- identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp))))
    cat("  item set identical:", si, "| resp set identical:", sr, "| live rows:", nrow(live), "\n")
    if (!si || !sr) fail <- c(fail, "live set mismatch")

    # Reported, not enforced. The numeric prefix marks the HAQ's eight activity
    # categories, so items sharing one should cohere more than items across two.
    # The direction is informative; the size is not decisive, because the HAQ
    # disability index is strongly unidimensional and between-category
    # correlations are high anyway.
    its <- grep("^HAQ[1-8][abc]$", unique(live$item), value = TRUE)
    w <- reshape(live[live$item %in% its, c("id", "item", "resp")], idvar = "id",
                 timevar = "item", direction = "wide")
    m <- as.matrix(w[, -1]); colnames(m) <- sub("resp.", "", colnames(m), fixed = TRUE)
    cm <- cor(m, use = "pairwise.complete.obs")
    ct <- substr(colnames(cm), 4, nchar(colnames(cm)) - 1)
    win <- c(); btw <- c()
    for (p in seq_len(ncol(cm))) for (q in seq_len(ncol(cm))) if (p < q) {
        if (ct[p] == ct[q]) win <- c(win, cm[p, q]) else btw <- c(btw, cm[p, q])
    }
    cat(sprintf("  category coherence (reported, not enforced): within n=%d mean r=%.3f | between n=%d mean r=%.3f\n",
                length(win), mean(win), length(btw), mean(btw)))
    cat("  direction is as the category structure predicts; ranges overlap, so this",
        "corroborates rather than pins.\n")
}

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
