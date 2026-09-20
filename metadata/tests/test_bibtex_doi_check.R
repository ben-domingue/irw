## Run from metadata/: Rscript tests/test_bibtex_doi_check.R
## Base R only; fixtures and an injected fetch, no credentials or network.
source("bibtex_doi_check.R")

## --- extraction -----------------------------------------------------------
## doi.org returns the field inline and brace-delimited; other resolvers put it
## on its own line, and some quote. A Claude-generated entry has no DOI at all.
inline <- " @article{Kazarovytska_2026, title={Do people want to remember?}, url={http://dx.doi.org/10.1037/pspi0000513}, DOI={10.1037/pspi0000513}, year={2026} }"
stopifnot(identical(bibtex_cited_doi(inline), "10.1037/pspi0000513"),
          identical(bibtex_cited_doi("@misc{x,\n  doi = {10.7910/DVN/X2C2PL},\n}"),
                    "10.7910/dvn/x2c2pl"),
          identical(bibtex_cited_doi("@misc{x, doi = \"10.5281/zenodo.1\" }"),
                    "10.5281/zenodo.1"),
          is.na(bibtex_cited_doi("@misc{x, title={no doi here}}")),
          is.na(bibtex_cited_doi(NA_character_)))
## A `url` field that happens to contain doi.org is not the DOI field.
stopifnot(is.na(bibtex_cited_doi("@misc{x, url={https://doi.org/10.1/a}}")))
stopifnot(identical(bibtex_cited_doi(c(inline, NA_character_)),
                    c("10.1037/pspi0000513", NA_character_)))

## --- the cell is not always one DOI ---------------------------------------
stopifnot(identical(bibtex_doi_tokens("10.7910/DVN/PNGUT5; 10.7910/DVN/7A9YMV"),
                    c("10.7910/dvn/pngut5", "10.7910/dvn/7a9ymv")),
          identical(bibtex_doi_tokens("10.7910/dvn/nirwkz; russian/adyghe language"),
                    "10.7910/dvn/nirwkz"),
          identical(bibtex_doi_tokens("not yet published"), character(0)),
          identical(bibtex_doi_tokens(NA_character_), character(0)))

## --- status ---------------------------------------------------------------
bib <- function(doi) sprintf("@article{a, DOI={%s}}", doi)
## The #2301 signature: base DOI corrected in the sheet, cached BibTeX still on
## base+n. Both resolve, both are real articles, and they are not the same paper.
stopifnot(identical(bibtex_doi_status(bib("10.1037/pspi0000518"),
                                      "10.1037/pspi0000513", NA), "mismatch"),
          identical(bibtex_doi_status(bib("10.1002/ab.22089"),
                                      "10.1002/ab.22088", NA), "mismatch"),
          identical(bibtex_doi_status(bib("10.46814/lajdv3n5-020"),
                                      "10.46814/lajdv3n5-018", NA), "mismatch"))
## A cached citation for the source deposit on a row that now names a paper is
## stale, not false: it points at this dataset. Reported, not repaired.
stopifnot(identical(bibtex_doi_status(bib("10.17605/OSF.IO/N26MB"),
                                      "10.1038/s41597-022-01383-6", NA), "deposit"),
          identical(bibtex_doi_status(bib("10.7910/DVN/RVJIMX"),
                                      "10.1007/s10648-021-09609-6", NA), "deposit"))

## The data-repository prefixes must stay identical to check_dictionary_dois.R,
## which draws the same distinction for #1764. Read them out of that file rather
## than trusting two hand-maintained copies to agree.
src <- paste(readLines("check_dictionary_dois.R"), collapse = "\n")
block <- regmatches(src, regexpr("DATA_PREFIXES <- c\\([^)]*\\)", src))
stopifnot(length(block) == 1L,
          identical(eval(parse(text = sub("^DATA_PREFIXES <- ", "", block))),
                    BIBTEX_DATA_DOI_PREFIXES))
## Not defects: resolver prefix, case, one of several listed DOIs, the deposit
## when the row carries both, a SciELO language variant, and no DOI to compare.
stopifnot(identical(bibtex_doi_status(bib("https://doi.org/10.1037/PSPI0000513"),
                                      "10.1037/pspi0000513", NA), "ok"),
          identical(bibtex_doi_status(bib("10.7910/DVN/7A9YMV"),
                                      "10.7910/DVN/PNGUT5; 10.7910/DVN/7A9YMV", NA), "ok"),
          identical(bibtex_doi_status(bib("10.7910/DVN/UOBDRV"),
                                      "10.1371/journal.pone.0297822",
                                      "10.7910/DVN/UOBDRV"), "ok"),
          identical(bibtex_doi_status(bib("10.1590/1982-7849rac2025240272.en"),
                                      "10.1590/1982-7849rac2025240272", NA), "ok"),
          identical(bibtex_doi_status(bib("10.6084/m9.figshare.28188872.v1"),
                                      "not yet published", NA), "unknown"),
          identical(bibtex_doi_status("@misc{x, title={generated}}",
                                      "10.1037/pspi0000513", NA), "unknown"),
          identical(bibtex_doi_status(NA_character_, "10.1037/pspi0000513", NA),
                    "unknown"))

## --- which DOI a refetch should use ---------------------------------------
stopifnot(identical(bibtex_preferred_doi("10.1037/pspi0000513", "10.7910/DVN/A"),
                    "10.1037/pspi0000513"),
          identical(bibtex_preferred_doi(NA, "10.7910/DVN/A"), "10.7910/dvn/a"),
          is.na(bibtex_preferred_doi("not yet published", NA)))

## --- refetch --------------------------------------------------------------
biblio <- data.frame(
    table = c("kazarovytska_2026_ingroup_event_attribution", "fine", "generated", "unreachable"),
    DOI__for_paper_ = c("10.1037/pspi0000513", "10.1037/pspi0000513", NA, "10.1002/ab.22088"),
    DOI__for_data_  = c(NA, NA, NA, NA),
    BibTex = c(bib("10.1037/pspi0000518"), bib("10.1037/pspi0000513"),
               "@misc{x, title={generated}}", bib("10.1002/ab.22097")),
    Description = c("a", "b", "c", "d"),
    stringsAsFactors = FALSE)
calls <- character(0)
fake_fetch <- function(table, doi) {
    calls <<- c(calls, doi)
    if (identical(doi, "10.1002/ab.22088")) return(NA_character_)  ## resolver down
    bib(doi)
}
res <- suppressWarnings(refetch_stale_bibtex(biblio, fake_fetch, "core"))
## Only the rows that disagree are fetched, and each against its own claim.
stopifnot(identical(calls, c("10.1037/pspi0000513", "10.1002/ab.22088")),
          identical(res$biblio$BibTex[1], bib("10.1037/pspi0000513")),
          ## an agreeing row and a DOI-less generated one are untouched
          identical(res$biblio$BibTex[2:3], biblio$BibTex[2:3]),
          ## a failed fetch blanks rather than keeping someone else's paper
          is.na(res$biblio$BibTex[4]),
          identical(res$biblio[setdiff(names(res$biblio), "BibTex")],
                    biblio[setdiff(names(biblio), "BibTex")]),
          nrow(res$log) == 2L,
          identical(sort(res$log$outcome), c("blanked", "refetched")))
## Idempotent: a second pass has nothing left to do (the blanked row is
## "unknown", not "mismatch").
again <- refetch_stale_bibtex(res$biblio, function(table, doi)
    stop("must not fetch"), "core")
stopifnot(nrow(again$log) == 0L, identical(again$biblio, res$biblio))

## --- the gate -------------------------------------------------------------
stopifnot(inherits(tryCatch(assert_bibtex_doi_consistent(biblio, "core"),
                            error = function(e) e), "error"))
assert_bibtex_doi_consistent(res$biblio, "core")
## Empty, and a frame without the columns, are both no-ops rather than failures.
assert_bibtex_doi_consistent(biblio[FALSE, ], "core")
assert_bibtex_doi_consistent(data.frame(table = "x", stringsAsFactors = FALSE), "core")

## --- the shipped file ------------------------------------------------------
## The four biblio exports in this directory must satisfy the gate the pipeline
## now applies. This is the regression test for the 58 rows of #2301.
for (f in c("biblio.csv", "comps_biblio.csv", "nominal_biblio.csv", "simsyn_biblio.csv")) {
    if (!file.exists(f)) next
    csv <- read.csv(f, colClasses = "character", check.names = FALSE, na.strings = "")
    assert_bibtex_doi_consistent(csv, f)
}

cat("test_bibtex_doi_check.R: all assertions passed\n")
