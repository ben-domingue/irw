## validate_irw.R — IRW format checker
##
## Source this file, then call validate_irw(df, label) on each dataset before saving.
##
## This implements the `core` profile: the five checks below, and no more. The
## full check set — response-scale homogeneity, composite items, rt/date units,
## covariate ranges, table naming — lives in the `irw_validate` Python package
## and runs as `irw-validate <file.csv>`. This file is deliberately NOT a
## wrapper around it: its whole value is that it works for someone with an R
## session and a URL, and nothing else installed.
##
## The `# @check` markers below name each check. `irw_validate/tests/` parses
## them and asserts they match `irw_validate.model.CORE_CHECKS` exactly, so the
## two implementations cannot drift apart again (irw#1703, sub-item 1.3).
##
## Output:
##   OK    — dataset passes all checks
##   NOTE  — soft warning (e.g. NAs in resp, columns missing cov_ prefix); worth reviewing
##   ERROR — hard violation of IRW format (e.g. missing id/item/resp, non-numeric resp,
##            duplicate id+item rows with no longitudinal column); must be fixed before upload
##
## Example:
##
##   source("https://raw.githubusercontent.com/ben-domingue/irw/main/misc/validate_irw.R")
##   ## or, if working locally:
##   ## source("/path/to/irw/src/misc/validate_irw.R")
##
##   df <- read.csv("mydata.csv")
##   validate_irw(df, "mydata.csv")
##
##   ## to check all CSVs in the current directory:
##   fns <- list.files(pattern="*.csv")
##   for (fn in fns) {
##       df <- read.csv(fn)
##       validate_irw(df, fn)
##   }

validate_irw <- function(df, label="") {
    issues <- character(0)
    notes  <- character(0)

    # @check required_columns
    required <- c("id", "item", "resp")
    missing  <- setdiff(required, names(df))
    if (length(missing) > 0)
        issues <- c(issues, paste("missing required columns:", paste(missing, collapse=", ")))

    if (length(missing) == 0) {
        # @check id_na
        # @check item_na
        # @check resp_na
        ## A bare "N NAs" conflates a typed null with an "NA"-style token that
        ## read.csv parsed as missing, and the two mean different things at
        ## upload (#2029, #2314). This side cannot tell them apart -- say so
        ## rather than implying a count of empty cells.
        na_note <- paste("These may be empty cells or literal 'NA'-style text",
                         "that the reader parsed as missing; the two are not",
                         "distinguished here.")
        for (col in required) {
            if (all(is.na(df[[col]])))
                issues <- c(issues, paste0(col, " has no usable values: all ",
                                           nrow(df), " row(s) are missing. ",
                                           na_note))
            else if (any(is.na(df[[col]])))
                notes <- c(notes, paste0(col, " has ", sum(is.na(df[[col]])),
                                         " missing value(s). ", na_note))
        }

        # @check resp_numeric
        ## Storage type, deliberately: a resp column stored as character
        ## uploads to Redivis as a string and every model downstream breaks.
        ## The Python side splits this into resp_numeric (do the values parse)
        ## and resp_dtype (is the column stored as a number).
        if (!is.numeric(df$resp))
            issues <- c(issues, paste("resp is not numeric (class:", class(df$resp), ")"))

        # @check dup_id_item
        ## The reassurance used to fire on the mere PRESENCE of a wave /
        ## timepoint / date column, without testing whether it explained
        ## anything. 14 of 15 sampled reassurances were wrong -- the repeats
        ## survived every accepted occasion key and their full combination
        ## (#1728, #2314). Test the keys and report what is left.
        ##
        ## `rt` is deliberately absent: it is a measurement, and letting it key
        ## a row would silently merge rows that differ only by rounding.
        known_longitudinal <- c("wave", "timepoint", "date")
        has_longitudinal   <- any(known_longitudinal %in% names(df))
        occasion <- c("rater", "wave", "timepoint", "date", "trialnum", "trial",
                      "order", "session", "occasion", "period", "block",
                      "subtest")
        occ <- c(intersect(occasion, names(df)),
                 grep("^trial_", names(df), value = TRUE))
        occ <- unique(occ)
        dups <- sum(duplicated(df[, c("id", "item")]))
        if (dups > 0 && !has_longitudinal) {
            issues <- c(issues, paste(dups, "duplicate id+item rows with no wave/timepoint/date column"))
        } else if (dups > 0) {
            resolved <- NULL
            for (col in occ)
                if (!any(duplicated(df[, c("id", "item", col)]))) {
                    resolved <- col
                    break
                }
            if (is.null(resolved) && length(occ) > 1 &&
                !any(duplicated(df[, c("id", "item", occ)])))
                resolved <- paste(occ, collapse = "+")
            if (!is.null(resolved)) {
                notes <- c(notes, paste0(dups, " duplicate id+item rows, made ",
                                         "unique by ", resolved,
                                         " (occasion columns tested: ",
                                         paste(occ, collapse = ", "), ")"))
            } else {
                residual <- sum(duplicated(df[, c("id", "item", occ)]))
                notes <- c(notes, paste0(dups, " duplicate id+item rows; ",
                                         residual, " excess row(s) remain after ",
                                         "keying on every occasion column ",
                                         "present, individually and combined ",
                                         "(tested: ",
                                         paste(occ, collapse = ", "), ")"))
            }
        }
    }

    # @check cov_prefix
    ## Broadened 2026-09-02 to the full documented standard: treat, rater and
    ## item_family are legitimate columns, and this list predated them, so it
    ## emitted a NOTE on every correctly-formatted table that used one.
    known_cols  <- c("id", "item", "resp", "rt", "date", "wave", "timepoint",
                     "treat", "rater", "item_family")
    other_cols  <- setdiff(names(df), known_cols)
    known_prefix <- "^(cov_|itemcov_|qmatrix|trial_)"
    unprefixed  <- other_cols[!grepl(known_prefix, other_cols)]
    if (length(unprefixed) > 0)
        notes <- c(notes, paste("columns without cov_ prefix:", paste(unprefixed, collapse=", ")))

    ## report
    header <- if (nchar(label) > 0) paste0("[", label, "]") else "[dataset]"
    if (length(issues) == 0 && length(notes) == 0) {
        message(header, " OK")
    } else {
        if (length(issues) > 0)
            message(header, " ERROR: ", paste(issues, collapse="; "))
        if (length(notes) > 0)
            message(header, " NOTE: ", paste(notes, collapse="; "))
    }

    invisible(list(issues=issues, notes=notes))
}


## Exit status, so this can gate a script rather than only inform one:
##
##   res <- validate_irw(df, "mydata.csv")
##   quit(status = validate_irw_status(res))
##
## Matches irw-validate's contract: 0 clean, 1 something blocks.
validate_irw_status <- function(res) {
    if (length(res$issues) > 0) 1L else 0L
}
