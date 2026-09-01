##Dictionary DOI consistency check (issue #1764).
##
##ONE INVARIANT: rows of the Data Dictionary that share an identical `Reference`
##must carry an identical `DOI (for paper)`. Citing one paper while pointing at
##two different DOIs is a contradiction on the face of the row -- no network, no
##credentials, no judgement call required.
##
##Why this check and not a smarter one. `irw-auto-tag` resolves a table's source
##by DOI and reads that paper. A wrong DOI does not fail loudly: the fetch
##succeeds, the content verifies as a genuine article, and the table is tagged
##from an unrelated paper. #1764 found 36 such tables, 34 of them from a
##spreadsheet drag-fill that incremented the DOI by one per row -- and because
##APA/Wiley journals number articles sequentially, every incremented value landed
##on a real, different article in the same journal. Nothing downstream noticed.
##
##Run it:
##
##    Rscript check_dictionary_dois.R              ##live sheet
##    Rscript check_dictionary_dois.R dict.csv     ##a local snapshot
##
##Exits 1 if any violation is found, so it can gate a pipeline run.

suppressPackageStartupMessages({
    library(gsheet)
})

DICT_URL <- paste0("https://docs.google.com/spreadsheets/d/",
                   "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s",
                   "/edit?gid=0#gid=0")

##Data-repository prefixes. A Reference group whose DOIs are ALL data DOIs is the
##legitimate one-deposit-per-scale pattern (the 60-table goldberg_2018_* group is
##exactly this: one ESCS citation, 19 Dataverse DOIs). Not a contradiction.
DATA_PREFIXES <- c("10.7910/", "10.17605/", "10.31234/", "10.31219/", "10.5281/",
                   "10.5061/", "10.6084/", "10.5255/", "10.3886/", "10.17632/",
                   "10.34894/", "10.5683/", "10.48668/", "10.33009/", "10.32614/",
                   "10.18712/", "10.4232/", "10.17026/", "10.57760/", "10.57903/",
                   "10.17608/", "10.23668/", "10.7802/", "10.21979/", "10.60507/",
                   "10.25349/", "10.24433/")

##Known-benign mixed groups: one row carries the article DOI, its siblings the
##data DOI. Both are correct (see #1764's follow-up comment); they are listed
##here so a real regression is not lost in noise. Keyed on the DOI set, so a
##group only stays exempt while its membership is unchanged.
ALLOWED_MIXED <- list(
    c("10.1186/s40359-024-00851-2", "10.34894/fddftj"),          ##IJLS_Eersel_2024_*
    c("10.1371/journal.pone.0276189", "10.3886/e175721v1")       ##alcoholhealthwarninglabel_*
)

norm_doi <- function(x) {
    x <- tolower(trimws(ifelse(is.na(x), "", as.character(x))))
    x <- sub("^https?://(dx\\.)?doi\\.org/", "", x)
    x <- sub("^doi:\\s*", "", x)
    sub("\\.$", "", trimws(x))
}

norm_ref <- function(x) {
    x <- tolower(ifelse(is.na(x), "", as.character(x)))
    trimws(gsub("\\s+", " ", x))
}

is_data_doi <- function(d) any(startsWith(d, DATA_PREFIXES))

##The drag-fill signature: DOIs identical but for a trailing integer that runs
##consecutively. Reported separately because it names the cause, and because it
##tells the curator the fix (collapse to the lowest, which is the batch head).
dragfill_run <- function(dois) {
    stem <- sub("[0-9]+$", "", dois)
    tail <- suppressWarnings(as.integer(sub("^.*?([0-9]+)$", "\\1", dois)))
    if (length(unique(stem)) != 1L || anyNA(tail) || length(tail) < 3L) return(FALSE)
    tail <- sort(unique(tail))
    length(tail) >= 3L && all(diff(tail) == 1L)
}

check_dictionary <- function(d) {
    stopifnot(all(c("table", "Reference", "DOI (for paper)") %in% names(d)))
    ref <- norm_ref(d[["Reference"]])
    doi <- norm_doi(d[["DOI (for paper)"]])
    tab <- as.character(d[["table"]])

    ##A Reference too short to be a citation cannot anchor the invariant.
    keep <- nzchar(doi) & nchar(ref) > 40L
    ref <- ref[keep]; doi <- doi[keep]; tab <- tab[keep]

    out <- list()
    for (r in unique(ref)) {
        i <- which(ref == r)
        dset <- sort(unique(doi[i]))
        if (length(dset) < 2L) next
        if (all(vapply(dset, is_data_doi, logical(1)))) next
        if (any(vapply(ALLOWED_MIXED, function(a) setequal(dset, a), logical(1)))) next
        out[[length(out) + 1L]] <- list(
            reference = r, dois = dset, tables = sort(tab[i]),
            n_tables = length(i), dragfill = dragfill_run(dset)
        )
    }
    out[order(-vapply(out, function(x) x$n_tables, integer(1)))]
}

report <- function(v) {
    if (length(v) == 0L) {
        cat("OK - every Reference group carries a single DOI.\n"); return(0L)
    }
    n <- sum(vapply(v, function(x) x$n_tables, integer(1)))
    cat(sprintf("FAIL - %d Reference group(s) carry more than one DOI, %d tables.\n\n",
                length(v), n))
    for (x in v) {
        cat(sprintf("  %d tables, %d DOIs%s\n", x$n_tables, length(x$dois),
                    if (x$dragfill) "  [DRAG-FILL: consecutive run; collapse to the lowest]" else ""))
        cat(sprintf("    ref : %s...\n", substr(x$reference, 1, 90)))
        cat(sprintf("    dois: %s\n", paste(x$dois, collapse = ", ")))
        cat(sprintf("    e.g.: %s\n\n", paste(utils::head(x$tables, 4), collapse = ", ")))
    }
    cat("The dictionary is read-only from code (#1708): fix in the sheet.\n")
    1L
}

if (!isFALSE(getOption("irw.dictcheck.run", TRUE))) {
    a <- commandArgs(trailingOnly = TRUE)
    d <- if (length(a) && nzchar(a[1])) {
        read.csv(a[1], check.names = FALSE, colClasses = "character")
    } else {
        as.data.frame(gsheet2tbl(DICT_URL))
    }
    quit(status = report(check_dictionary(d)))
}
