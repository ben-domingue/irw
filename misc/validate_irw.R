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
##   source("https://raw.githubusercontent.com/ben-domingue/irw/main/src/misc/validate_irw.R")
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
        for (col in required) {
            if (all(is.na(df[[col]])))
                issues <- c(issues, paste(col, "is entirely NA"))
            else if (any(is.na(df[[col]])))
                notes <- c(notes, paste(col, "has", sum(is.na(df[[col]])), "NAs"))
        }

        # @check resp_numeric
        ## Storage type, deliberately: a resp column stored as character
        ## uploads to Redivis as a string and every model downstream breaks.
        ## The Python side splits this into resp_numeric (do the values parse)
        ## and resp_dtype (is the column stored as a number).
        if (!is.numeric(df$resp))
            issues <- c(issues, paste("resp is not numeric (class:", class(df$resp), ")"))

        # @check dup_id_item
        known_longitudinal <- c("wave", "timepoint", "date")
        has_longitudinal   <- any(known_longitudinal %in% names(df))
        dups <- sum(duplicated(df[, c("id", "item")]))
        if (dups > 0 && !has_longitudinal)
            issues <- c(issues, paste(dups, "duplicate id+item rows with no wave/timepoint/date column"))
        else if (dups > 0)
            notes <- c(notes, paste(dups, "duplicate id+item rows (longitudinal column present — likely ok)"))
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
