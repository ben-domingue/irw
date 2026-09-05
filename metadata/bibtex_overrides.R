## Curated corrections for DOI resolvers that return demonstrably wrong BibTeX.
## Each entry must carry its authoritative source and the reason for overriding.
## These functions only replace citations; they never create bibliography rows.

normalize_bibtex_doi <- function(doi) {
    doi <- tolower(trimws(as.character(doi)))
    doi <- sub("^https?://(dx\\.)?doi\\.org/", "", doi)
    doi <- sub("^doi:[[:space:]]*", "", doi)
    doi[is.na(doi)] <- ""
    doi
}

read_bibtex_overrides <- function(path) {
    overrides <- read.csv(path, colClasses = "character", check.names = FALSE,
                          na.strings = "", stringsAsFactors = FALSE)
    required <- c("doi", "BibTex", "source_url", "reason")
    if (!identical(names(overrides), required)) {
        stop("BibTeX overrides must have columns: ", paste(required, collapse = ", "))
    }
    for (field in required) {
        if (any(is.na(overrides[[field]]) | trimws(overrides[[field]]) == "")) {
            stop("Blank ", field, " in BibTeX overrides")
        }
    }
    overrides$doi <- normalize_bibtex_doi(overrides$doi)
    if (any(overrides$doi == "") || anyDuplicated(overrides$doi)) {
        stop("Blank or duplicate DOI in BibTeX overrides")
    }
    overrides
}

bibtex_override_for_doi <- function(doi, overrides) {
    hit <- match(normalize_bibtex_doi(doi), overrides$doi)
    overrides$BibTex[hit]
}

apply_bibtex_overrides <- function(biblio, overrides) {
    if (!nrow(biblio)) return(biblio)
    hit <- match(normalize_bibtex_doi(biblio$DOI__for_paper_), overrides$doi)
    keep <- !is.na(hit)
    biblio$BibTex[keep] <- overrides$BibTex[hit[keep]]
    biblio
}
