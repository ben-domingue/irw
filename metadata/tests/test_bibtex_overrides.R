## Run from metadata/: Rscript tests/test_bibtex_overrides.R
## Base R only; fixtures and mocked HTTP, no credentials or network.
source("bibtex_overrides.R")

overrides <- read_bibtex_overrides("bibtex_overrides.csv")
doi <- "10.7910/DVN/X2C2PL"
expected <- bibtex_override_for_doi(doi, overrides)
stopifnot(length(expected) == 1L, !is.na(expected),
          grepl("author = {{Van Bich Nguyen}}", expected, fixed = TRUE),
          grepl("version = {1}", expected, fixed = TRUE),
          grepl("doi = {10.7910/DVN/X2C2PL}", expected, fixed = TRUE),
          !grepl("ich Nguyen, Bich", expected, fixed = TRUE))

## DOI normalization must route the same deposit to the same correction.
stopifnot(identical(expected, bibtex_override_for_doi(
    " https://doi.org/10.7910/dvn/x2c2pl ", overrides)),
    identical(expected, bibtex_override_for_doi("doi: 10.7910/DVN/X2C2PL", overrides)),
    is.na(bibtex_override_for_doi("10.1000/unrelated", overrides)),
    is.na(bibtex_override_for_doi(NA_character_, overrides)))

## Fix already-cached malformed citations without touching any other row/field.
biblio <- data.frame(
    table = c("nguyen_2026_barthel", "unrelated", "nguyen_2026_isi"),
    DOI__for_paper_ = c(doi, "10.1000/unrelated", doi),
    BibTex = c("author = {ich Nguyen, Bich}", " preserve exactly \n", NA),
    Reference_x = c("dataset citation", "another citation", "dataset citation"),
    stringsAsFactors = FALSE)
fixed <- apply_bibtex_overrides(biblio, overrides)
stopifnot(identical(fixed$BibTex[c(1L, 3L)], rep(expected, 2)),
          identical(fixed[2L, ], biblio[2L, ]),
          identical(fixed[setdiff(names(fixed), "BibTex")],
                    biblio[setdiff(names(biblio), "BibTex")]),
          identical(apply_bibtex_overrides(fixed, overrides), fixed))
## An override is not a substitute dictionary entry: no new rows can appear.
empty <- biblio[FALSE, ]
stopifnot(identical(apply_bibtex_overrides(empty, overrides), empty),
          identical(apply_bibtex_overrides(biblio[2L, ], overrides), biblio[2L, ]))

## Exercise the actual production fetch function without sourcing its pipeline.
## An overridden DOI must bypass HTTP; another DOI must retain normal retrieval.
expressions <- parse("02_biblio.R")
fetch_definition <- Filter(function(x) is.call(x) &&
    identical(x[[1L]], as.name("<-")) &&
    identical(x[[2L]], as.name("fetch_bibtex_from_doi")), expressions)
stopifnot(length(fetch_definition) == 1L)
env <- new.env(parent = globalenv())
env$bibtex_overrides <- overrides
env$calls <- 0L
env$GET <- function(...) { env$calls <- env$calls + 1L; "response" }
env$add_headers <- function(...) NULL
env$status_code <- function(...) 200L
env$content <- function(...) " resolver value unchanged \n"
eval(fetch_definition[[1L]], envir = env)
stopifnot(identical(env$fetch_bibtex_from_doi("nguyen_2026_pic", doi), expected),
          env$calls == 0L,
          identical(env$fetch_bibtex_from_doi("other", "10.1000/unrelated"),
                    " resolver value unchanged \n"), env$calls == 1L)

## Invalid curated inputs must fail loudly rather than silently choose a row.
expect_invalid <- function(rows) {
    path <- tempfile(fileext = ".csv")
    on.exit(unlink(path))
    write.csv(rows, path, row.names = FALSE, na = "")
    stopifnot(inherits(try(read_bibtex_overrides(path), silent = TRUE), "try-error"))
}
duplicate <- rbind(overrides, overrides)
duplicate$doi[2L] <- "https://doi.org/10.7910/DVN/X2C2PL"
expect_invalid(duplicate)
for (field in names(overrides)) {
    invalid <- overrides
    invalid[[field]][1L] <- "  "
    expect_invalid(invalid)
}
cat("All BibTeX override checks passed.\n")
