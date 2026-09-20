##Cached BibTeX must cite the DOI the row claims (issue #2301).
##
##THE DEFECT. 58 biblio rows carried a BibTeX entry for a different, real,
##unrelated paper. The signature is the one #1764 found in the dictionary: a
##spreadsheet drag-fill enumerated `DOI (for paper)` per table -- base DOI, base
##+1, base +2 -- and because APA/Wiley/SAGE number articles sequentially, every
##incremented value resolved to a genuine article in the same journal.
##
###1764 corrected the sheet. It could not correct biblio, because of the
##interaction of two rules that are each right on their own:
##
##  1. BibTeX is fetched once and cached forever. seed_from_local() reuses any
##     non-blank cached value and new_data_rows selects only rows biblio lacks
##     or whose BibTex is NA, so a populated BibTex is never refetched.
##  2. DOI__for_paper_ is refreshed on EVERY row on EVERY run
##     (BIBLIO_REFRESH_COLS, #2001).
##
##So the DOI column healed and the BibTeX beside it did not. bibtex_overrides.csv
##is the same class worked around one deposit at a time.
##
##THE FIX. Compare the DOI *inside* the cached BibTeX against the DOI columns
##beside it, refetch the ones that disagree, and refuse to write a biblio whose
##BibTeX still cites a DOI the row does not claim. This closes the class rather
##than the 58: any future correction to a DOI cell now invalidates the citation
##cached against the old value, whatever moved it.
##
##WHERE IT RUNS. At the end of getrows(), after refresh_biblio_from_dict() and
##apply_data_doi(). Both can move a DOI cell *after* the fetch stage has already
##run, so a check placed before them would pass on a row this one repairs, and
##the repair would wait for the following week's run.
##
##Base R only, and the fetch is injected, so tests need neither network nor
##credentials.

##The DOI a BibTeX entry cites. doi.org returns `DOI={10.…}` inline; other
##resolvers emit `doi = {10.…}` on its own line, and some quote instead of
##brace. NA when the entry carries no DOI field at all -- true of every
##Claude-generated citation for a row with no DOI, which is not a defect.
bibtex_cited_doi <- function(bib) {
    if (length(bib) != 1L) return(vapply(bib, bibtex_cited_doi, character(1),
                                         USE.NAMES = FALSE))
    if (is.na(bib)) return(NA_character_)
    m <- regmatches(bib, regexpr("(?i)(^|[,{[:space:]])doi[[:space:]]*=[[:space:]]*[{\"][^}\",]+[}\"]",
                                 bib, perl = TRUE))
    if (!length(m)) return(NA_character_)
    val <- sub("(?i)^.*?doi[[:space:]]*=[[:space:]]*[{\"]", "", m, perl = TRUE)
    val <- sub("[}\"].*$", "", val)
    bibtex_norm_doi(val)
}

##The repo's DOI normalisation, kept base-R here so this file can be sourced
##alone. Mirrors dict_norm_doi() in dict_union.R plus the lowercasing
##normalize_bibtex_doi() does: a resolver prefix or a change of case is not a
##different DOI.
bibtex_norm_doi <- function(x) {
    x <- tolower(trimws(ifelse(is.na(x), "", as.character(x))))
    x <- trimws(sub("^(data[[:space:]]+doi|doi)[[:space:]]*:[[:space:]]*", "", x))
    x <- trimws(sub("^https?://(dx\\.)?doi\\.org/", "", x))
    x <- trimws(sub("\\.s[0-9]{3}$", "", x))
    trimws(sub("\\.$", "", x))
}

##A DOI cell is not always one DOI. `condon_2024_sapa_personality` lists seven
##Dataverse deposits separated by "; ", `imps2025_hf` two DOIs on separate
##lines, and `bakumenko_2023_adyghe_values` a DOI followed by prose. Citing any
##one of them is citing the row's source, so split and keep the DOI-shaped
##tokens. A cell with none -- "not yet published", an OSF URL, a blank -- yields
##nothing to check against, which is "unknown", not "wrong".
bibtex_doi_tokens <- function(cell) {
    if (is.na(cell)) return(character(0))
    parts <- unlist(strsplit(as.character(cell), "[;,[:space:]]+"))
    parts <- bibtex_norm_doi(parts)
    parts[grepl("^10\\.[0-9]{4,9}/", parts)]
}

##Same article, different landing page. SciELO issues a `.en` DOI for the
##English version of a Portuguese article (`amorim_2025_climej_*`) and some
##repositories a `.v<n>` per deposit version. Deliberately narrow: `-018` vs
##`-020` is not a variant of anything, which is the whole point.
bibtex_doi_base <- function(x) sub("\\.(en|pt|es|fr|de|v[0-9]+)$", "", x)

##Data-repository registrants, copied verbatim from DATA_PREFIXES in
##check_dictionary_dois.R (#1764) and pinned to it by a parity assertion in
##tests/test_bibtex_doi_check.R. The two files answer different questions about
##the same distinction, and neither is a library the other can source: that
##script fetches the sheet the moment it is loaded.
BIBTEX_DATA_DOI_PREFIXES <- c("10.7910/", "10.17605/", "10.31234/", "10.31219/", "10.5281/",
                   "10.5061/", "10.6084/", "10.5255/", "10.3886/", "10.17632/",
                   "10.34894/", "10.5683/", "10.48668/", "10.33009/", "10.32614/",
                   "10.18712/", "10.4232/", "10.17026/", "10.57760/", "10.57903/",
                   "10.17608/", "10.23668/", "10.7802/", "10.21979/", "10.60507/",
                   "10.25349/", "10.24433/")

bibtex_is_data_doi <- function(x) {
    if (!length(x)) return(logical(0))
    Reduce(`|`, lapply(BIBTEX_DATA_DOI_PREFIXES, function(p) startsWith(x, p)))
}

##"ok" / "deposit" / "mismatch" / "unknown", one per row. unknown means the comparison
##cannot be made -- no BibTeX, no DOI in it, or no DOI in either column -- and
##is never an error.
bibtex_doi_status <- function(bib, paper, data) {
    n <- length(bib)
    paper <- rep(paper, length.out = n)
    data  <- rep(data,  length.out = n)
    out <- character(n)
    for (i in seq_len(n)) {
        cited <- bibtex_cited_doi(bib[i])
        claimed <- unique(c(bibtex_doi_tokens(paper[i]), bibtex_doi_tokens(data[i])))
        if (is.na(cited) || cited == "" || !length(claimed)) {
            out[i] <- "unknown"
        } else if (cited %in% claimed ||
                   bibtex_doi_base(cited) %in% bibtex_doi_base(claimed)) {
            out[i] <- "ok"
        } else if (bibtex_is_data_doi(cited)) {
            ##The citation names the deposit the data came from while the row
            ##now names the paper: 15 rows, all of them cached before #1690 put
            ##the deposit DOI in a column of its own. That is a stale citation,
            ##not a false one -- it points at this dataset -- so it is reported
            ##and left alone. Refetching it would rewrite 15 correct-enough
            ##citations for cosmetics, and would fight any row whose deposit DOI
            ##reaches DOI__for_data_ on a later run.
            out[i] <- "deposit"
        } else {
            out[i] <- "mismatch"
        }
    }
    out
}

##Which DOI a row should be cited by: the paper where there is one, the deposit
##otherwise. The same precedence 02_biblio.R uses for a fresh row, so a refetch
##cannot disagree with what a first fetch would have produced.
bibtex_preferred_doi <- function(paper, data) {
    p <- bibtex_doi_tokens(paper)
    if (length(p)) return(p[1])
    d <- bibtex_doi_tokens(data)
    if (length(d)) return(d[1])
    NA_character_
}

##Refetch the citations that cite the wrong paper, and report what moved.
##
##A failed fetch blanks the row rather than keeping the cached value: a missing
##citation is a gap the next run fills, a citation for someone else's paper is a
##false statement about the data. `fetch` takes (table, doi) and returns BibTeX
##or NA -- fetch_bibtex_from_doi() in 02_biblio.R, which consults
##bibtex_overrides.csv first, so a curated correction survives this.
refetch_stale_bibtex <- function(biblio, fetch, label = "core") {
    if (!nrow(biblio) || !all(c("BibTex", "DOI__for_paper_") %in% names(biblio))) {
        return(list(biblio = biblio, log = stale_bibtex_log()))
    }
    data_col <- if ("DOI__for_data_" %in% names(biblio)) {
        as.character(biblio$DOI__for_data_)
    } else rep(NA_character_, nrow(biblio))
    status <- bibtex_doi_status(as.character(biblio$BibTex),
                               as.character(biblio$DOI__for_paper_), data_col)
    if (any(status == "deposit")) {
        message(label, ": ", sum(status == "deposit"), " row(s) cite their source ",
                "deposit rather than the paper the row names; left as they are")
    }
    idx <- which(status == "mismatch")
    if (!length(idx)) {
        message(label, ": every cached BibTeX cites a DOI its row claims")
        return(list(biblio = biblio, log = stale_bibtex_log()))
    }
    message(label, ": ", length(idx), " cached BibTeX entr(ies) cite a DOI the row ",
            "does not claim; refetching")
    rows <- vector("list", length(idx))
    for (j in seq_along(idx)) {
        i <- idx[j]
        was <- bibtex_cited_doi(biblio$BibTex[i])
        want <- bibtex_preferred_doi(biblio$DOI__for_paper_[i], data_col[i])
        new <- tryCatch(fetch(biblio$table[i], want), error = function(e) NA_character_)
        if (length(new) != 1L) new <- NA_character_
        biblio$BibTex[i] <- new
        got <- bibtex_cited_doi(new)
        if (is.na(new)) {
            warning(sprintf("%s: could not refetch BibTeX for %s (%s); left blank",
                            label, biblio$table[i], want))
        }
        rows[[j]] <- data.frame(table = biblio$table[i], claimed = want,
                                cited_was = was, cited_now = got,
                                outcome = if (is.na(new)) "blanked" else "refetched",
                                stringsAsFactors = FALSE)
    }
    log <- do.call(rbind, rows)
    log <- log[order(log$table), , drop = FALSE]
    message("  refetched ", sum(log$outcome == "refetched"), ", blanked ",
            sum(log$outcome == "blanked"))
    list(biblio = biblio, log = log)
}

stale_bibtex_log <- function() {
    data.frame(table = character(0), claimed = character(0), cited_was = character(0),
               cited_now = character(0), outcome = character(0),
               stringsAsFactors = FALSE)
}

##The gate. Three lines of comparison is all it would have taken to catch this
##at the run that introduced it, so it runs on every row of every write, not
##only the ones this script touched.
assert_bibtex_doi_consistent <- function(biblio, label = "core") {
    if (!nrow(biblio) || !all(c("BibTex", "DOI__for_paper_") %in% names(biblio))) return(invisible(TRUE))
    data_col <- if ("DOI__for_data_" %in% names(biblio)) {
        as.character(biblio$DOI__for_data_)
    } else rep(NA_character_, nrow(biblio))
    status <- bibtex_doi_status(as.character(biblio$BibTex),
                               as.character(biblio$DOI__for_paper_), data_col)
    bad <- which(status == "mismatch")
    if (length(bad)) {
        detail <- paste(sprintf("  %s: row claims %s, BibTeX cites %s",
                                biblio$table[bad],
                                vapply(bad, function(i) bibtex_preferred_doi(
                                    biblio$DOI__for_paper_[i], data_col[i]), character(1)),
                                bibtex_cited_doi(as.character(biblio$BibTex[bad]))),
                        collapse = "\n")
        stop(label, ": ", length(bad), " BibTeX entr(ies) cite a DOI the row does ",
             "not claim (#2301). Not written.\n", detail, call. = FALSE)
    }
    message(label, ": BibTeX/DOI agreement verified on ", nrow(biblio), " row(s)")
    invisible(TRUE)
}
