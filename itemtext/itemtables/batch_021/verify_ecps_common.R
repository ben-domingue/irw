## verify_ecps_common.R  --  batch_021, issue #1831
##
## Shared body for the eight ecps_sahm_2024 verify scripts. All eight are keyed
## to one source -- the administered COVIDiSTRESS Round II Qualtrics form, plus
## the two registration workbooks for the parts its print view does not render
## -- so the re-derivation and the checks are identical and only the table
## differs.
##
## Checks, in order:
##   1. item_text re-derived from the instrument, per item
##   2. section_prompt and instrument, per item
##   3. option_text per resp level, against that item's own response ladder,
##      including the positions the form left without a verbal label
##   4. where every string was verified: the administered form, or the workbooks
##   5. the _0neutral decode, re-run from the cleaned data file
##   6. the source tie: every item code is a column of that file
##   7. item and resp sets against live response data
suppressMessages({library(jsonlite)})

verify_ecps <- function(TBL, resp_csv = NA_character_) {
    DIR <- "itemtables/batch_021"
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

    cat("=== 1. item_text re-derived from the administered instrument ===\n")
    bad <- 0
    for (code in codes) {
        want <- src[[code]]$text
        got  <- unique(it$item_text[it$item == code])
        if (is.null(want) || length(got) != 1 || !identical(got, want)) {
            bad <- bad + 1
            if (bad <= 3) cat(sprintf("  MISMATCH %s\n    source : %s\n    shipped: %s\n", code,
                substr(paste(want, collapse = "|"), 1, 88),
                substr(paste(got, collapse = "|"), 1, 88)))
        }
    }
    cat(sprintf("  items compared: %d | mismatches: %d\n", length(codes), bad))
    if (bad) fail <- c(fail, "item_text mismatch")

    cat("\n=== 2. section_prompt and instrument ===\n")
    sbad <- 0
    for (code in codes) {
        for (f in c("section_prompt", "instrument")) {
            want <- src[[code]][[if (f == "instrument") "instrument" else "section_prompt"]]
            want <- if (is.null(want) || !nzchar(want)) NA_character_ else want
            got  <- unique(it[[f]][it$item == code])
            if (length(got) != 1 || !identical(as.character(got), as.character(want)))
                sbad <- sbad + 1
        }
    }
    cat(sprintf("  cells compared: %d | mismatches: %d\n", 2 * length(codes), sbad))
    if (sbad) fail <- c(fail, "section_prompt/instrument mismatch")

    cat("\n=== 3. option_text against each item's response ladder ===\n")
    obad <- 0; labelled <- 0; blank <- 0
    for (code in codes) {
        lad  <- src[[code]]$ladder
        rows <- it[it$item == code, ]
        for (k in seq_len(nrow(rows))) {
            key <- format(rows$resp[k], trim = TRUE)
            if (!key %in% names(lad)) {
                obad <- obad + 1
                if (obad <= 3) cat(sprintf("  %s resp=%s has no position in the ladder\n",
                                           code, key))
                next
            }
            want <- lad[[key]]
            got  <- rows$option_text[k]
            # a NULL ladder entry is a position the form left unlabelled, which
            # must ship empty rather than invented
            ok <- if (is.null(want)) is.na(got) else identical(got, want)
            if (is.null(want)) blank <- blank + 1 else labelled <- labelled + 1
            if (!ok) {
                obad <- obad + 1
                if (obad <= 3) cat(sprintf("  MISMATCH %s resp=%s\n    ladder : %s\n    shipped: %s\n",
                    code, key, if (is.null(want)) "(unlabelled position)" else want,
                    if (is.na(got)) "(empty)" else got))
            }
        }
    }
    cat(sprintf("  option cells checked: %d | labelled: %d | unlabelled by the form: %d | mismatches: %d\n",
                labelled + blank, labelled, blank, obad))
    if (obad) fail <- c(fail, "option_text does not match the response ladder")

    cat("\n=== 4. where the strings were verified ===\n")
    sv <- red$string_verification
    cat(sprintf("  administered form: %s | registration workbooks: %s | neither: %s\n",
                sv$in_survey_pdf, sv$in_workbooks, sv$unverified))
    if (!identical(as.numeric(sv$unverified), 0)) fail <- c(fail, "unverified source strings")

    cat("\n=== 5. the _0neutral decode, re-run from the cleaned data file ===\n")
    nd <- red$neutral_decode
    if (is.null(nd$distinct_mappings)) {
        cat("  ", nd$note, "\n", sep = "")
    } else {
        cat(sprintf("  items carrying both codings: %s | distinct mappings: %d\n",
                    nd$items_with_both_codings, length(nd$distinct_mappings)))
        for (sig in names(nd$distinct_mappings))
            cat(sprintf("     n=%-3d %s\n", length(nd$distinct_mappings[[sig]]), sig))
        if (length(nd$distinct_mappings) > 2)
            fail <- c(fail, "the _0neutral decode is no longer consistent")
    }

    cat("\n=== 6. source tie: item codes are columns of the cleaned data file ===\n")
    cc <- red$source_column_check[[TBL]]
    if (is.null(cc)) {
        cat("  cleaned data file not cached -- column check skipped\n")
    } else {
        cat(sprintf("  items: %s | codes that are not a column: %d\n",
                    cc$items, length(cc$not_a_column)))
        if (length(cc$not_a_column)) fail <- c(fail, "item code absent from the source file")
    }

    cat("\n=== 7. item and resp sets vs live response data ===\n")
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
