## verify_ecps_common.R  --  batch_016, issue #1831
##
## Shared body for the five ecps_sahm_2024 verify scripts. All five are keyed
## to one source (the COVIDiSTRESS Global Survey Round II questionnaire on OSF),
## so the re-derivation and the checks are identical and only the table differs.
##
## Checks, in order:
##   1. item_text re-derived from the questionnaire workbook, per item
##   2. section_prompt and instrument, per item
##   3. option_text is empty throughout -- the two available questionnaire
##      documents are registration-stage and their response designs do not
##      describe the administered scales (see provenance.csv), so no option
##      label is asserted
##   4. cross-document wording agreement, where a scale appears in both workbooks
##   5. the source tie: every shipped item code is a column of
##      Final_COVIDiSTRESS_Vol2_cleaned.csv
##   6. item and resp sets against live response data
suppressMessages({library(jsonlite)})

verify_ecps <- function(TBL, resp_csv = NA_character_) {
    DIR <- "itemtables/batch_016"
    CSV <- file.path(DIR, paste0(TBL, "__items.csv"))
    JSN <- file.path(DIR, "rederived_ecps.json")
    fail <- character(0)

    if (!file.exists(JSN))
        system2("python3", file.path(DIR, "rederive_ecps.py"))
    red <- fromJSON(JSN, simplifyVector = FALSE)
    src <- red$tables[[TBL]]
    if (is.null(src)) { cat("no re-derived entry for", TBL, "\n"); return("no source") }
    it <- read.csv(CSV, stringsAsFactors = FALSE)
    it$item <- as.character(it$item)
    codes <- unique(it$item)

    cat("=== 1. item_text re-derived from the questionnaire ===\n")
    bad <- 0
    for (code in codes) {
        want <- src[[code]]$text
        got  <- unique(it$item_text[it$item == code])
        if (is.null(want) || length(got) != 1 || !identical(got, want)) {
            bad <- bad + 1
            if (bad <= 3) cat(sprintf("  MISMATCH %s\n    source : %s\n    shipped: %s\n", code,
                substr(paste(want, collapse = "|"), 1, 90),
                substr(paste(got, collapse = "|"), 1, 90)))
        }
    }
    cat(sprintf("  items compared: %d | mismatches: %d\n", length(codes), bad))
    if (bad) fail <- c(fail, "item_text mismatch")

    cat("\n=== 2. section_prompt and instrument ===\n")
    sbad <- 0
    for (code in codes) {
        for (f in c("section_prompt", "instrument")) {
            want <- src[[code]][[f]]
            want <- if (is.null(want) || !nzchar(want)) NA_character_ else want
            got  <- unique(it[[f]][it$item == code])
            if (length(got) != 1 || !identical(as.character(got), as.character(want))) sbad <- sbad + 1
        }
    }
    cat(sprintf("  cells compared: %d | mismatches: %d\n", 2 * length(codes), sbad))
    if (sbad) fail <- c(fail, "section_prompt/instrument mismatch")

    cat("\n=== 3. option_text deliberately empty ===\n")
    nonempty <- sum(!is.na(it$option_text) & nzchar(it$option_text))
    cat("  non-empty option_text cells:", nonempty, "of", nrow(it), "\n")
    if (nonempty) fail <- c(fail, "option_text is populated but no option source was established")

    cat("\n=== 4. cross-document wording agreement ===\n")
    for (k in names(red$cross_document_wording))
        cat(sprintf("  %-28s %s\n", k, red$cross_document_wording[[k]]))
    if (any(grepl("^differs", unlist(red$cross_document_wording))))
        fail <- c(fail, "the two questionnaire documents disagree on wording")

    cat("\n=== 5. source tie: item codes are columns of the COVIDiSTRESS Vol 2 file ===\n")
    cc <- red$source_column_check[[TBL]]
    if (is.null(cc)) {
        cat("  source CSV not cached -- column check skipped\n")
    } else {
        cat(sprintf("  items: %s | codes that are not a column: %d\n",
                    cc$items, length(cc$not_a_column)))
        if (length(cc$not_a_column)) fail <- c(fail, "item code absent from the source data file")
    }

    cat("\n=== 6. item and resp sets vs live response data ===\n")
    live <- if (!is.na(resp_csv) && nzchar(resp_csv)) {
        cat("  (using local response CSV:", resp_csv, ")\n")
        read.csv(resp_csv, stringsAsFactors = FALSE)
    } else tryCatch(irw::irw_fetch(TBL), error = function(e) NULL)

    if (is.null(live) || !nrow(live)) {
        cat("  live data unavailable -- sets NOT checked\n")
        fail <- c(fail, "live data unavailable")
    } else {
        si <- identical(sort(codes), sort(unique(as.character(live$item))))
        sr <- identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp))))
        cat("  item set identical:", si, "| resp set identical:", sr,
            "| live rows:", nrow(live), "\n")
        if (!si || !sr) fail <- c(fail, "live set mismatch")
    }

    cat("\n", strrep("-", 60), "\n", sep = "")
    if (length(fail)) {
        cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
    } else cat("VERDICT: PASS\n")
    invisible(fail)
}

verify_args <- function() {
    a <- commandArgs(trailingOnly = TRUE)
    i <- match("--resp-csv", a)
    if (!is.na(i)) {
        if (length(a) < i + 1) stop("--resp-csv needs a path")
        return(a[i + 1])
    }
    NA_character_
}
