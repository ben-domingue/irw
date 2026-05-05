## validate_irw.R — IRW format checker
##
## Source this file, then call validate_irw(df, label) on each dataset before saving.
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

    ## required columns
    required <- c("id", "item", "resp")
    missing  <- setdiff(required, names(df))
    if (length(missing) > 0)
        issues <- c(issues, paste("missing required columns:", paste(missing, collapse=", ")))

    if (length(missing) == 0) {
        ## NAs in required columns
        for (col in required) {
            if (all(is.na(df[[col]])))
                issues <- c(issues, paste(col, "is entirely NA"))
            else if (any(is.na(df[[col]])))
                notes <- c(notes, paste(col, "has", sum(is.na(df[[col]])), "NAs"))
        }

        ## resp must be numeric
        if (!is.numeric(df$resp))
            issues <- c(issues, paste("resp is not numeric (class:", class(df$resp), ")"))

        ## duplicate id+item
        known_longitudinal <- c("wave", "timepoint", "date")
        has_longitudinal   <- any(known_longitudinal %in% names(df))
        dups <- sum(duplicated(df[, c("id", "item")]))
        if (dups > 0 && !has_longitudinal)
            issues <- c(issues, paste(dups, "duplicate id+item rows with no wave/timepoint/date column"))
        else if (dups > 0)
            notes <- c(notes, paste(dups, "duplicate id+item rows (longitudinal column present — likely ok)"))
    }

    ## covariate naming
    known_cols  <- c("id", "item", "resp", "rt", "date", "wave", "timepoint")
    other_cols  <- setdiff(names(df), known_cols)
    unprefixed  <- other_cols[!grepl("^cov_", other_cols)]
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
