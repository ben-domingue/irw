##One-time backfill for #2301: refetch the 58 biblio.csv citations that name a
##different, real, unrelated paper than the row's own DOI.
##
##02_biblio.R now does this on every run (refetch_stale_bibtex(), called last in
##getrows()), so this script exists only to land the correction without waiting
##for the weekly run -- and, unlike the pipeline, it needs no Redivis
##credentials and no dictionary read. Same code, same DOIs, same precedence:
##fetch_bibtex_from_doi() consults bibtex_overrides.csv first.
##
##Run from metadata/:  Rscript hotfixes/fix-2301-bibtex-doi.R
##Network to doi.org, ~1 request per repaired row. Rerunning is a no-op.

library(httr)
library(glue)
source("bibtex_overrides.R")
source("bibtex_doi_check.R")
bibtex_overrides <- read_bibtex_overrides("bibtex_overrides.csv")

##The fetch from 02_biblio.R, reproduced rather than sourced: that file opens
##four Google Sheets and a Redivis dataset the moment it is loaded.
fetch_bibtex_from_doi <- function(filename, doi) {
    if (is.na(doi) || doi == "") return(NA_character_)
    curated <- bibtex_override_for_doi(doi, bibtex_overrides)
    if (!is.na(curated)) return(curated)
    response <- tryCatch(GET(paste0("https://doi.org/", doi),
                             add_headers(Accept = "application/x-bibtex")),
                         error = function(e) NULL)
    if (!is.null(response) && status_code(response) == 200) {
        return(content(response, as = "text", encoding = "UTF-8"))
    }
    warning(glue("Failed to fetch BibTeX for dataset: {filename}"))
    NA_character_
}

for (f in c("biblio.csv", "comps_biblio.csv", "nominal_biblio.csv", "simsyn_biblio.csv")) {
    if (!file.exists(f)) next
    message("== ", f)
    ##trim_ws=FALSE for the same reason seed_from_local() uses it: doi.org
    ##returns BibTeX with a leading space, and trimming it would rewrite rows
    ##this fix has no business touching.
    biblio <- readr::read_csv(f, show_col_types = FALSE, trim_ws = FALSE)
    ##The four exports are CRLF-delimited (embedded newlines inside a BibTeX
    ##field stay LF). Writing with readr's default eol would rewrite all 4,367
    ##lines and bury 58 real changes in a whole-file diff, so take the eol from
    ##the file being repaired.
    eol <- if (grepl("\r\n", readChar(f, 4000L, useBytes = TRUE), fixed = TRUE)) "\r\n" else "\n"
    res <- refetch_stale_bibtex(biblio, fetch_bibtex_from_doi, f)
    if (nrow(res$log)) {
        print(res$log[, c("table", "claimed", "cited_was", "cited_now")])
        readr::write_csv(res$biblio, f, eol = eol)
    }
    assert_bibtex_doi_consistent(res$biblio, f)
}
