## verify_coach_common.R  --  batch_016, issue #1831
##
## Shared body for the five COACH_Chen_2022 verify scripts. All five are keyed
## to one source (the deposit's codebook.xlsx), so the re-derivation and the
## checks are identical and only the table name differs.
##
## Checks, in order:
##   1. item_text re-derived from codebook.xlsx, per item
##   2. option_text per resp level, against that item's own value labels
##   3. every live level either carries the codebook's label or is a documented
##      out-of-range level with no row at all -- nothing is silently relabelled
##   4. the translated_substitute fallback is recorded as the schema requires:
##      language names the administered language, _translated columns empty
##   5. the evidence for that fallback, re-counted: no CJK item text in the
##      deposit's own files
##   6. item and resp sets against live response data
suppressMessages({library(jsonlite)})

verify_coach <- function(TBL, resp_csv = NA_character_) {
    DIR <- "itemtables/batch_016"
    CSV <- file.path(DIR, paste0(TBL, "__items.csv"))
    JSN <- file.path(DIR, "rederived_coach.json")
    fail <- character(0)

    if (!file.exists(JSN))
        system2("python3", file.path(DIR, "rederive_coach.py"))
    red <- fromJSON(JSN, simplifyVector = FALSE)
    src <- red$entries
    lower <- setNames(names(src), tolower(names(src)))
    it <- read.csv(CSV, stringsAsFactors = FALSE)
    it$item <- as.character(it$item)
    codes <- unique(it$item)

    cat("=== 1. item_text re-derived from codebook.xlsx ===\n")
    bad <- 0
    for (code in codes) {
        key  <- lower[[tolower(code)]]
        want <- if (is.null(key)) NULL else trimws(src[[key]]$text)
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

    cat("\n=== 2. option_text per resp level ===\n")
    obad <- 0; cells <- 0
    for (code in codes) {
        key <- lower[[tolower(code)]]
        o   <- src[[key]]$opts
        rows <- it[it$item == code, ]
        for (k in seq_len(nrow(rows))) {
            cells <- cells + 1
            want <- o[[as.character(rows$resp[k])]]
            if (is.null(want) || !identical(rows$option_text[k], want)) {
                obad <- obad + 1
                if (obad <= 3) cat(sprintf("  MISMATCH %s resp=%s\n    source : %s\n    shipped: %s\n",
                    code, rows$resp[k], paste(want, collapse = "|"), rows$option_text[k]))
            }
        }
    }
    cat(sprintf("  option cells checked: %d | mismatches: %d\n", cells, obad))
    if (obad) fail <- c(fail, "option_text mismatch")

    cat("\n=== 4. translated_substitute fallback recorded correctly ===\n")
    tcols <- c("item_text_translated", "option_text_translated",
               "instructions_translated", "section_prompt_translated")
    langs <- unique(it$language)
    tfull <- vapply(tcols, function(c) sum(!is.na(it[[c]]) & nzchar(it[[c]])), 1L)
    cat("  language:", paste(langs, collapse = ","),
        "| non-empty cells in the _translated columns:", sum(tfull), "\n")
    if (!identical(langs, "Chinese")) fail <- c(fail, "language is not Chinese")
    if (sum(tfull))                   fail <- c(fail, "_translated columns are not empty")

    cat("\n=== 5. evidence for the fallback: CJK in the deposit's own files ===\n")
    cj <- red$cjk_evidence
    cat(sprintf("  codebook.xlsx CJK chars: %s | raw.xlsx: %s\n",
        cj[["codebook.xlsx"]], cj[["raw.xlsx"]]))
    cat("  (a small count is font names such as SimSun, not item text)\n")
    if (is.numeric(cj[["codebook.xlsx"]]) && cj[["codebook.xlsx"]] > 20)
        fail <- c(fail, "deposit may carry CJK item text after all -- recheck the fallback")

    cat("\n=== 6. item and resp sets vs live response data ===\n")
    live <- if (!is.na(resp_csv) && nzchar(resp_csv)) {
        cat("  (using local response CSV:", resp_csv, ")\n")
        read.csv(resp_csv, stringsAsFactors = FALSE)
    } else tryCatch(irw::irw_fetch(TBL), error = function(e) NULL)

    if (is.null(live) || !nrow(live)) {
        cat("  live data unavailable -- sets NOT checked\n")
        fail <- c(fail, "live data unavailable")
    } else {
        live$item <- as.character(live$item)
        si <- identical(sort(unique(it$item)), sort(unique(live$item)))
        sr <- identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp))))
        cat("  item set identical:", si, "| resp set identical:", sr,
            "| live rows:", nrow(live), "\n")
        if (!si || !sr) fail <- c(fail, "live set mismatch")

        cat("\n=== 3. live levels with no codebook label (expected to carry no row) ===\n")
        tot <- 0
        for (code in codes) {
            key <- lower[[tolower(code)]]
            lab <- as.integer(names(src[[key]]$opts))
            lv  <- sort(unique(as.numeric(live$resp[live$item == code])))
            off <- setdiff(lv, lab)
            if (length(off)) {
                n <- sum(live$item == code & live$resp %in% off)
                tot <- tot + n
                cat(sprintf("  %-42s levels %s -> %d live rows, no row shipped\n",
                            code, paste(off, collapse = ","), n))
                if (any(it$resp[it$item == code] %in% off))
                    fail <- c(fail, paste("unlabelled level shipped for", code))
            }
        }
        cat(sprintf("  live rows on an unlabelled level: %d of %d (%.3f%%)\n",
                    tot, nrow(live), 100 * tot / nrow(live)))
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
