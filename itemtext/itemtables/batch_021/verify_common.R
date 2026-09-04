## verify_common.R  --  batch_021, issue #1831
##
## Shared body for the seven promis1wave1 verify scripts. All seven tables are
## keyed to one source (the study's PROMIS Wave 1 codebook, Appendix A), so the
## re-derivation and the checks are identical and only the table name differs.
##
## Checks, in order:
##   1. item_text re-derived from the codebook, per item
##   2. section_prompt (the codebook's item context), per item
##   3. option_text per resp level, applying the documented 6-option/5-level rule
##   4. independent cross-check against the official PROMIS item-bank PDFs
##   5. item and resp sets against live response data
##
## Rule for the 6-wide codebook option sets (see provenance.csv note): where the
## per-item respondent count shows no deficit against sibling items, the two
## bottom categories share live level 1 and option_text joins both labels with
## ' / '; where it shows a clear deficit, the extra category is absent from the
## live data and levels 1-5 map onto keys 1-5.
suppressMessages({library(jsonlite)})

MERGE_LOW <- list(c("Had no pain", "Never"),
                  c("Not sure if I had this type of pain", "Did not have this type of pain"))

expected_labels <- function(e, used) {
    o <- e$opts
    if (length(o) == 6 && identical(as.numeric(used), as.numeric(1:5))) {
        lo <- unname(c(o[["1"]], o[["2"]]))
        if (any(vapply(MERGE_LOW, function(m) identical(lo, m), TRUE)))
            return(c(paste(o[["1"]], "/", o[["2"]]), o[["3"]], o[["4"]], o[["5"]], o[["6"]]))
    }
    unname(unlist(o[as.character(used)]))
}

norm_txt <- function(s) {
    s <- tolower(gsub("[‘’]", "'", s))
    s <- gsub("[^a-z0-9' ]+", " ", s)
    trimws(gsub("\\s+", " ", s))
}

verify_table <- function(TBL, resp_csv = NA_character_) {
    DIR <- "itemtables/batch_021"
    CSV <- file.path(DIR, paste0(TBL, "__items.csv"))
    JSN <- file.path(DIR, "rederived.json")
    fail <- character(0)

    if (!file.exists(JSN))
        system2("python3", file.path(DIR, "rederive_promis.py"))
    src <- fromJSON(JSN, simplifyVector = FALSE)
    it  <- read.csv(CSV, stringsAsFactors = FALSE)
    it$item <- as.character(it$item)
    codes <- sort(unique(it$item))

    cat("=== 1. item_text re-derived from the codebook ===\n")
    bad <- 0
    for (code in codes) {
        want <- src[[code]]$text
        got  <- unique(it$item_text[it$item == code])
        if (is.null(want) || length(got) != 1 || !identical(got, want)) {
            bad <- bad + 1
            if (bad <= 3) cat(sprintf("  MISMATCH %s\n    source : %s\n    shipped: %s\n",
                code, substr(paste(want, collapse = "|"), 1, 90),
                substr(paste(got, collapse = "|"), 1, 90)))
        }
    }
    cat(sprintf("  items compared: %d | mismatches: %d\n", length(codes), bad))
    if (bad) fail <- c(fail, "item_text mismatch")

    cat("\n=== 2. section_prompt (codebook item context) ===\n")
    sbad <- 0
    for (code in codes) {
        want <- src[[code]]$context
        want <- if (is.null(want) || !nzchar(want)) NA_character_ else want
        got  <- unique(it$section_prompt[it$item == code])
        if (length(got) != 1 || !identical(as.character(got), as.character(want))) sbad <- sbad + 1
    }
    cat(sprintf("  items compared: %d | mismatches: %d\n", length(codes), sbad))
    if (sbad) fail <- c(fail, "section_prompt mismatch")

    cat("\n=== 3. option_text per resp level ===\n")
    obad <- 0; cells <- 0
    for (code in codes) {
        rows <- it[it$item == code, ]
        rows <- rows[order(rows$resp), ]
        want <- expected_labels(src[[code]], rows$resp)
        cells <- cells + nrow(rows)
        if (length(want) != nrow(rows) || !identical(unname(rows$option_text), want)) {
            obad <- obad + 1
            if (obad <= 3) cat(sprintf("  MISMATCH %s\n    source : %s\n    shipped: %s\n",
                code, paste(want, collapse = " | "), paste(rows$option_text, collapse = " | ")))
        }
    }
    cat(sprintf("  option cells checked: %d | items with a mismatch: %d\n", cells, obad))
    if (obad) fail <- c(fail, "option_text mismatch")

    cat("\n=== 4. cross-check vs official PROMIS item-bank PDFs ===\n")
    cov <- codes[vapply(codes, function(c) !is.null(src[[c]]$official_prefix), TRUE)]
    pbad <- character(0)
    for (code in cov) {
        off <- norm_txt(src[[code]]$official_prefix)
        shp <- norm_txt(unique(it$item_text[it$item == code])[1])
        if (nchar(off) >= 12 && !startsWith(shp, off)) pbad <- c(pbad, code)
    }
    cat(sprintf("  items covered by the official extract: %d of %d | prefix disagreements: %d\n",
        length(cov), length(codes), length(pbad)))
    if (length(pbad)) {
        for (code in pbad) cat(sprintf("    %s\n      official: %s\n      shipped : %s\n",
            code, src[[code]]$official_prefix, unique(it$item_text[it$item == code])[1]))
        cat("  NOTE: a disagreement here is a wording discrepancy between the study\n",
            "       codebook and the canonical instrument, recorded in provenance.csv,\n",
            "       not necessarily a defect in the shipped text.\n", sep = "")
    }

    cat("\n=== 5. item and resp sets vs live response data ===\n")
    live <- NULL
    if (!is.na(resp_csv) && nzchar(resp_csv)) {
        live <- read.csv(resp_csv, stringsAsFactors = FALSE)
        cat("  (using local response CSV:", resp_csv, ")\n")
    } else {
        live <- tryCatch(irw::irw_fetch(TBL), error = function(e) NULL)
    }
    if (is.null(live) || !nrow(live)) {
        cat("  live data unavailable -- sets NOT checked\n")
        fail <- c(fail, "live data unavailable")
    } else {
        si <- identical(sort(unique(as.character(it$item))), sort(unique(as.character(live$item))))
        sr <- identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp))))
        cat("  item set identical:", si, "| resp set identical:", sr,
            "| live rows:", nrow(live), "\n")
        if (!si || !sr) fail <- c(fail, "live set mismatch")
    }

    cat("\n", strrep("-", 60), "\n", sep = "")
    if (length(fail)) {
        cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
    } else {
        cat("VERDICT: PASS\n")
    }
    invisible(fail)
}

## Shared arg handling: optional --resp-csv <path> for the set check.
verify_args <- function() {
    a <- commandArgs(trailingOnly = TRUE)
    i <- match("--resp-csv", a)
    if (!is.na(i)) {
        if (length(a) < i + 1) stop("--resp-csv needs a path")
        return(a[i + 1])
    }
    NA_character_
}
