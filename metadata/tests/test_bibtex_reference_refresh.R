## Run from metadata/: Rscript tests/test_bibtex_reference_refresh.R
## Base R only, fixtures, no credentials or network (#2580).
source("dict_union.R")
source("bibtex_doi_check.R")

biblio <- data.frame(
    table       = c("a_nodoi_fixed", "b_nodoi_same", "c_doi_changed", "d_ws_only", "e_not_in_dict"),
    Reference_x = c("CIS, Indice de Confianza, Estudio 3565", "INEGI ENSU 2024",
                    "Old paper", "CIS, Estudio 3508\n", "Something"),
    BibTex      = c("@dataset{x, title={Indice}}", "@misc{y}", "@article{z, DOI={10.1/a}}",
                    "@dataset{w}", "@misc{v}"),
    stringsAsFactors = FALSE)
dict <- data.frame(
    table             = c("A_NODOI_FIXED", "b_nodoi_same", "c_doi_changed", "d_ws_only"),
    Reference         = c("CIS, Desinformacion y humor, Estudio 3563", "INEGI ENSU 2024",
                          "New paper", "CIS,  Estudio 3508"),
    `DOI (for paper)` = c(NA, "", "10.1/a", "NA"),
    check.names = FALSE, stringsAsFactors = FALSE)

r <- drop_stale_reference_bibtex(biblio, dict, "test")
## only the no-DOI row whose Reference really changed is dropped (case-insensitive join)
stopifnot(identical(r$log$table, "a_nodoi_fixed"),
          identical(sort(r$biblio$table),
                    sort(c("b_nodoi_same", "c_doi_changed", "d_ws_only", "e_not_in_dict"))))
## a DOI row is left to the #2301 check; whitespace-only differences do not count
stopifnot("c_doi_changed" %in% r$biblio$table, "d_ws_only" %in% r$biblio$table)
## a blank dictionary Reference never drops a row
dict2 <- dict; dict2$Reference[1] <- ""
stopifnot(nrow(drop_stale_reference_bibtex(biblio, dict2)$log) == 0)
## DOI (for data) also marks a row as DOI-backed
dict3 <- dict; dict3[["DOI (for data)"]] <- c("10.5/x", NA, NA, NA)
stopifnot(nrow(drop_stale_reference_bibtex(biblio, dict3)$log) == 0)
## missing columns: no-op
stopifnot(identical(drop_stale_reference_bibtex(biblio[, c("table", "BibTex")], dict)$biblio,
                    biblio[, c("table", "BibTex")]))
cat("test_bibtex_reference_refresh: OK\n")
