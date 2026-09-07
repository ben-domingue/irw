##Tests for the dictionary/automated union in dict_union.R (issue #1732).
##
##Runs offline: dict_union.R touches no network, so nothing here reaches the
##Google Sheets or the published CSVs. Run it from the metadata directory:
##
##    Rscript tests/test_dict_union.R
##
##THE TEST THAT MATTERS is human_cell_always_wins(). The whole reason this file
##exists rather than a copy of 03_tags.R's union is that tags supersedes at ROW
##level and strands 19-76 tables per column (#1863). If a human's non-empty cell
##is ever overwritten, or a human's blank cell can never be filled, this merge
##has become the thing it was written to avoid.

source("dict_union.R")

failures <- 0L
ok    <- function(what) cat("  ok   -", what, "\n")
check <- function(cond, what) {
    if (isTRUE(cond)) ok(what)
    else { cat("  FAIL -", what, "\n"); failures <<- failures + 1L }
}
expect_error <- function(expr, pattern, what) {
    e <- tryCatch({ force(expr); NULL }, error = function(e) conditionMessage(e))
    if (is.null(e)) { cat("  FAIL -", what, "(no error raised)\n"); failures <<- failures + 1L }
    else check(grepl(pattern, e, fixed = TRUE), what)
}

##---------------------------------------------------------------- fixtures ---
##The sheet as gsheet2tbl returns it TODAY: `Custom License` twice, already
##disambiguated by make.unique. A fixture using the post-rename names would test
##a layout that does not exist yet.
SHEET_NAMES <- c("table", "table.lower", "Description", "URL (for data)",
                 "Reference", "DOI (for paper)", "Original License",
                 "Custom License...8", "Public Reshare?", "Derived License",
                 "Custom License...11", "Notes", "Contributor", "Date")

fake_sheet <- function(...) {
    rows <- list(...)
    d <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE)
    names(d) <- SHEET_NAMES
    d
}
sheet_row <- function(table, description = "", derived = "", doi = "",
                      custom_derived = "", contributor = "BD") {
    c(table, tolower(table), description, "", "", doi, "", "",
      "Public", derived, custom_derived, "", contributor, "1/1/2026")
}

fake_auto <- function(...) {
    rows <- list(...)
    d <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE)
    names(d) <- DICT_AUTO_COLS
    d
}
auto_row <- function(table, description = "", derived = "", doi = "",
                     doi_data = "", custom_derived = "", custom_source = "",
                     contributor = DICT_AUTO_CONTRIBUTOR, reshare = "Public") {
    c(table, tolower(table), description, "", "", doi, doi_data, "",
      custom_source, reshare, derived, custom_derived, "", contributor,
      "9/6/2026")
}

##------------------------------------------------------------------- tests ---
cat("resolve_dict_cols\n")

local({
    d <- fake_sheet(sheet_row("a_2020"))
    map <- resolve_dict_cols(d)
    check(map[["Custom License (source)"]]  == "Custom License...8",
          "source terms resolve to the column after `Original License`")
    check(map[["Custom License (derived)"]] == "Custom License...11",
          "derived terms resolve to the column fix-licenses.R used to read")
})

local({
    d <- fake_sheet(sheet_row("a_2020"))
    names(d)[c(8, 11)] <- c("Custom License (source)", "Custom License (derived)")
    map <- resolve_dict_cols(d)
    check(map[["Custom License (derived)"]] == "Custom License (derived)",
          "after the #1732 rename, both resolve by name")
})

local({
    d <- fake_sheet(sheet_row("a_2020"))
    d[["Custom License...8"]] <- NULL
    expect_error(resolve_dict_cols(d, "core"),
                 "expected two `Custom License` columns",
                 "one Custom License column is refused, not guessed at")
})

cat("union_dict -- precedence\n")

human_cell_always_wins <- function() {
    d <- fake_sheet(sheet_row("a_2020", description = "HUMAN WROTE THIS",
                              derived = "CC BY 4.0"))
    a <- fake_auto(auto_row("a_2020", description = "machine guess",
                            derived = "CC0 1.0", doi = "10.1/x"))
    res <- union_dict(d, a)
    check(res$dict$Description[1] == "HUMAN WROTE THIS",
          "a non-empty human cell is never overwritten")
    check(res$dict$`Derived License`[1] == "CC BY 4.0",
          "a non-empty human licence is never overwritten")
    check(res$dict$`DOI (for paper)`[1] == "10.1/x",
          "a blank human cell IS filled (the #1863 defect, not repeated)")
    check(nrow(res$dict) == 1L, "topping up a row does not duplicate it")
}
human_cell_always_wins()

local({
    ##The sheet stores three things that all mean blank.
    for (empty in list(NA_character_, "", "NA")) {
        d <- fake_sheet(sheet_row("a_2020"))
        d$Description[1] <- empty
        a <- fake_auto(auto_row("a_2020", description = "filled"))
        res <- union_dict(d, a)
        check(res$dict$Description[1] == "filled",
              paste0("a cell holding ", if (is.na(empty)) "NA" else paste0("'", empty, "'"),
                     " counts as blank and is filled"))
    }
})

local({
    d <- fake_sheet(sheet_row("a_2020", contributor = "Samuel Enrique"))
    a <- fake_auto(auto_row("a_2020", doi = "10.1/x"))
    res <- union_dict(d, a)
    check(res$dict$Contributor[1] == "Samuel Enrique",
          "topping up a human row does not steal its Contributor")
    check(res$dict$Date[1] == "1/1/2026",
          "topping up a human row does not restamp its Date")
})

local({
    d <- fake_sheet(sheet_row("A_2020"))          ##sheet keeps original case
    a <- fake_auto(auto_row("a_2020", doi = "10.1/x"))
    res <- union_dict(d, a)
    check(nrow(res$dict) == 1L && res$dict$`DOI (for paper)`[1] == "10.1/x",
          "the key match is case-insensitive (307 tables depend on this)")
})

cat("union_dict -- new rows and licence terms\n")

local({
    d <- fake_sheet(sheet_row("a_2020"))
    a <- fake_auto(auto_row("b_2026", description = "new table",
                            derived = "CC BY 4.0"))
    res <- union_dict(d, a)
    check(nrow(res$dict) == 2L, "a table absent from the sheet is appended")
    check(res$dict$table[2] == "b_2026", "the appended row keeps its name")
    check(res$dict$Description[2] == "new table", "the appended row keeps its cells")
})

local({
    ##The two Custom License columns must not cross-contaminate: source terms
    ##belong at position 8, derived terms at 11 -- the one fix-licenses.R read.
    d <- fake_sheet(sheet_row("a_2020"))
    a <- fake_auto(auto_row("a_2020", custom_source = "SOURCE TERMS",
                            custom_derived = "DERIVED TERMS"))
    res <- union_dict(d, a)
    check(res$dict$`Custom License...8`[1]  == "SOURCE TERMS",
          "source licence terms land in the column after `Original License`")
    check(res$dict$`Custom License...11`[1] == "DERIVED TERMS",
          "derived licence terms land in the column after `Derived License`")
})

cat("union_dict -- provenance\n")

local({
    d <- fake_sheet(sheet_row("a_2020", description = "HUMAN"))
    a <- fake_auto(auto_row("a_2020", description = "ignored", doi = "10.1/x"))
    res <- union_dict(d, a)
    check(nrow(res$provenance) == 1L, "a topped-up table gets a provenance row")
    check(res$provenance$columns[1] == "DOI (for paper)",
          "provenance names only the cells the machine actually filled")
    check(!grepl("Description", res$provenance$columns[1]),
          "provenance does not claim a cell the human owns")
})

local({
    d <- fake_sheet(sheet_row("a_2020", description = "HUMAN", doi = "10.1/x"))
    a <- fake_auto(auto_row("a_2020", description = "ignored"))
    res <- union_dict(d, a)
    check(nrow(res$provenance) == 0L,
          "a row the machine could not add anything to gets no provenance row")
})

cat("read_dict_auto -- refusals\n")

tmp <- tempfile(fileext = ".csv")
on.exit(unlink(tmp), add = TRUE)

local({
    readr::write_csv(fake_auto(auto_row("a_2020", contributor = "BD")), tmp)
    expect_error(read_dict_auto(tmp, "core"), "whose Contributor is not 'automated'",
                 "a human-authored row in the automated file is refused")
})

local({
    readr::write_csv(fake_auto(auto_row("a_2020", reshare = "")), tmp)
    expect_error(read_dict_auto(tmp, "core"), "blank `Public Reshare?`",
                 "a blank Public Reshare? is refused (it would vanish silently)")
})

local({
    readr::write_csv(fake_auto(auto_row("a_2020"), auto_row("A_2020")), tmp)
    expect_error(read_dict_auto(tmp, "core"), "more than once",
                 "the same table staged twice is refused, case-insensitively")
})

local({
    bad <- fake_auto(auto_row("a_2020"))
    names(bad)[3] <- "Descriptions"
    readr::write_csv(bad, tmp)
    expect_error(read_dict_auto(tmp, "core"), "header does not match",
                 "a changed header is refused rather than merged by position")
})

local({
    check(is.null(read_dict_auto(NULL, "comps")),
          "a source with no automated file configured is a no-op")
    check(is.null(read_dict_auto(file.path(tempdir(), "nope.csv"), "core")),
          "a missing automated file degrades to sheet-only")
})

cat("drop_dead_dict_rows\n")

local({
    live <- tempfile(fileext = ".csv")
    on.exit(unlink(live), add = TRUE)
    readr::write_csv(data.frame(table = c(sprintf("t%04d", 1:1500), "a_2020")), live)
    a <- fake_auto(auto_row("a_2020"), auto_row("retired_2019"))
    kept <- drop_dead_dict_rows(a, live, "core")
    check(nrow(kept) == 1L && kept$table[1] == "a_2020",
          "a row naming a table absent from metadata.csv is dropped")
})

local({
    live <- tempfile(fileext = ".csv")
    on.exit(unlink(live), add = TRUE)
    readr::write_csv(data.frame(table = "a_2020"), live)      ##implausibly small
    a <- fake_auto(auto_row("a_2020"), auto_row("b_2026"))
    kept <- suppressWarnings(drop_dead_dict_rows(a, live, "core"))
    check(nrow(kept) == 2L,
          "a truncated oracle warns and drops nothing (cannot empty a batch)")
})

cat("pending rows (held, not discarded)\n")

local({
    live <- tempfile(fileext = ".csv"); pend <- tempfile(fileext = ".csv")
    on.exit(unlink(c(live, pend)), add = TRUE)
    readr::write_csv(data.frame(table = c(sprintf("t%04d", 1:1500), "a_2020")), live)
    a <- fake_auto(auto_row("a_2020"), auto_row("draft_2026"))
    kept <- drop_dead_dict_rows(a, live, "core", pending.file = pend)
    held <- readr::read_csv(pend, col_types = readr::cols(.default = readr::col_character()))
    check(nrow(kept) == 1L, "a row for an unpublished table is held back")
    check(nrow(held) == 1L && held$table[1] == "draft_2026",
          "the held row is written to the pending file, not discarded")
    check(identical(names(held), DICT_AUTO_COLS),
          "the pending file keeps the full layout, so it can be re-read")
})

local({
    ##An empty pending file is a statement -- "nothing is waiting on a publish"
    ##-- and a missing one is not. The batch window depends on telling them apart.
    live <- tempfile(fileext = ".csv"); pend <- tempfile(fileext = ".csv")
    on.exit(unlink(c(live, pend)), add = TRUE)
    readr::write_csv(data.frame(table = c(sprintf("t%04d", 1:1500), "a_2020")), live)
    drop_dead_dict_rows(fake_auto(auto_row("a_2020")), live, "core", pending.file = pend)
    check(file.exists(pend) &&
          nrow(readr::read_csv(pend, show_col_types = FALSE)) == 0L,
          "with nothing held, the pending file is written empty rather than left stale")
})

cat("DOI (for data) -- the #1690 split\n")

local({
    d <- fake_sheet(sheet_row("a_2020"))
    a <- fake_auto(auto_row("a_2020", doi_data = "10.7910/DVN/ZDNSFJ"))
    res <- union_dict(d, a)
    check("DOI (for data)" %in% names(res$dict),
          "the sheet does not carry the column and the union creates it")
    check(res$dict[["DOI (for data)"]][1] == "10.7910/DVN/ZDNSFJ",
          "the automated deposit DOI lands in it")
})

local({
    ##The whole point: the sheet cites a Dataverse deposit as the paper.
    d <- fake_sheet(sheet_row("a_2020"))
    d[["DOI (for paper)"]][1] <- "https://doi.org/10.7910/DVN/ZDNSFJ"
    a <- fake_auto(auto_row("a_2020", doi_data = "10.7910/DVN/ZDNSFJ"))
    res <- union_dict(d, a)
    check(dict_blank(res$dict[["DOI (for paper)"]][1]),
          "a paper DOI that is the SAME deposit DOI is cleared in the export")
    check(res$dict[["DOI (for data)"]][1] == "10.7910/DVN/ZDNSFJ",
          "the value is preserved in the data column, not lost")
    check(grepl("-DOI (for paper)", res$provenance$columns[1], fixed = TRUE),
          "the cleared cell is named in the provenance")
})

local({
    ##The guard. A genuine article DOI must survive even when the row also has
    ##a deposit DOI -- which is the correct end state for a row with both.
    d <- fake_sheet(sheet_row("a_2020"))
    d[["DOI (for paper)"]][1] <- "10.1371/journal.pone.0146050"
    a <- fake_auto(auto_row("a_2020", doi_data = "10.7910/DVN/ZDNSFJ"))
    res <- union_dict(d, a)
    check(res$dict[["DOI (for paper)"]][1] == "10.1371/journal.pone.0146050",
          "a paper DOI that is NOT the deposit DOI is left alone")
    check(res$dict[["DOI (for data)"]][1] == "10.7910/DVN/ZDNSFJ",
          "and the deposit DOI still lands beside it")
})

local({
    ##Blank `DOI (for data)` must never be read as "clear the paper DOI".
    d <- fake_sheet(sheet_row("a_2020"))
    d[["DOI (for paper)"]][1] <- "10.7910/DVN/ZDNSFJ"
    a <- fake_auto(auto_row("a_2020", description = "x"))
    res <- union_dict(d, a)
    check(res$dict[["DOI (for paper)"]][1] == "10.7910/DVN/ZDNSFJ",
          "an automated row with no data DOI clears nothing")
})

local({
    ##dict_norm_doi is a COMPARISON helper, so the wrapped and bare forms of one
    ##DOI must collapse together or the override silently never fires.
    check(dict_norm_doi("https://doi.org/10.7910/DVN/ZDNSFJ") == "10.7910/DVN/ZDNSFJ",
          "dict_norm_doi unwraps a resolver URL")
    check(dict_norm_doi("data doi: 10.6084/m9.figshare.1.v2") == "10.6084/m9.figshare.1.v2",
          "dict_norm_doi drops a `data doi: ` prefix")
    check(dict_norm_doi("10.3389/fpsyg.2022.1014794.s001") == "10.3389/fpsyg.2022.1014794",
          "dict_norm_doi drops a supplement suffix")
    check(dict_norm_doi(NA) == "", "dict_norm_doi maps NA to blank, not \"NA\"")
})

local({
    ##PARITY. dict_norm_doi mirrors normalize() in doi_hygiene.py, which is the
    ##definition. Two implementations drift; this is what notices.
    hygiene <- "../automated_finding/doi_hygiene.py"
    if (!file.exists(hygiene)) {
        cat("  skip - doi_hygiene.py not found\n")
    } else {
        probes <- c("https://doi.org/10.7910/DVN/ZDNSFJ",
                    "http://dx.doi.org/10.1136/bmjgh-2019-001724",
                    "data doi: 10.6084/m9.figshare.26820745.v4",
                    "DOI:10.1371/journal.pone.0146050",
                    "10.3389/fpsyg.2022.1014794.s001",
                    "10.17632/826gmw6ypw.1",
                    "10.1787/9789264281820-en",
                    "10.1037/a0022874.",
                    "  10.5281/zenodo.123  ",
                    "")
        py <- suppressWarnings(system2("python3", c(hygiene, "--filter"),
                                       input = probes, stdout = TRUE, stderr = FALSE))
        if (!is.null(attr(py, "status")) || length(py) != length(probes)) {
            cat("  skip - could not run doi_hygiene.py --filter\n")
        } else {
            check(identical(unname(dict_norm_doi(probes)), py),
                  "dict_norm_doi agrees with doi_hygiene.py on every probe")
        }
    }
})

cat("apply_data_doi -- the carry-through to biblio.csv\n")

local({
    ##biblio.csv is built incrementally: a long-published row never passes
    ##through new_data_rows, so without this join none of the 979 rows changes.
    dict <- fake_sheet(sheet_row("a_2020"), sheet_row("b_2021"), sheet_row("c_2022"))
    dict[["DOI (for data)"]] <- c("10.7910/DVN/ZDNSFJ", "10.6084/m9.figshare.1.v2", NA)
    dict[["DOI (for paper)"]] <- c(NA, NA, "10.1371/journal.pone.0146050")
    biblio <- data.frame(
        table = c("a_2020", "b_2021", "c_2022"),
        DOI__for_paper_ = c("https://doi.org/10.7910/DVN/ZDNSFJ",
                            "10.1136/bmjgh-2019-001724",
                            "10.1371/journal.pone.0146050"),
        stringsAsFactors = FALSE)
    out <- apply_data_doi(biblio, dict)

    check(is.na(out$DOI__for_paper_[1]),
          "a published row citing the deposit as the paper is cleared")
    check(out$DOI__for_data_[1] == "10.7910/DVN/ZDNSFJ",
          "and gains the deposit DOI in its own column")
    check(out$DOI__for_paper_[2] == "10.1136/bmjgh-2019-001724",
          "a row whose paper DOI is a REAL paper keeps it, data DOI or not")
    check(out$DOI__for_data_[2] == "10.6084/m9.figshare.1.v2",
          "and still gains its deposit DOI")
    check(out$DOI__for_paper_[3] == "10.1371/journal.pone.0146050" &&
          is.na(out$DOI__for_data_[3]),
          "a row with no deposit DOI is untouched")
})

local({
    ##A source with no automated file never gains the column. It must still
    ##produce the biblio schema rather than failing.
    dict <- fake_sheet(sheet_row("a_2020"))
    biblio <- data.frame(table = "a_2020", DOI__for_paper_ = "10.1/x",
                         stringsAsFactors = FALSE)
    out <- apply_data_doi(biblio, dict)
    check("DOI__for_data_" %in% names(out) && is.na(out$DOI__for_data_[1]),
          "a sheet with no `DOI (for data)` yields the column, all blank")
    check(out$DOI__for_paper_[1] == "10.1/x",
          "and clears nothing")
})

cat("apply_custom_license_terms\n")

local({
    d <- fake_sheet(sheet_row("a_2020", custom_derived = "TERMS HERE"),
                    sheet_row("b_2020"))
    b <- data.frame(table = c("A_2020", "b_2020", "c_2020"),
                    stringsAsFactors = FALSE)
    out <- suppressMessages(apply_custom_license_terms(b, d))
    check(out$Custom_License_Terms[1] == "TERMS HERE",
          "terms attach case-insensitively to a long-published row")
    check(is.na(out$Custom_License_Terms[2]),
          "a row with no terms gets NA, not an empty string")
    check(is.na(out$Custom_License_Terms[3]),
          "a biblio row absent from the dictionary is left alone")
    check(nrow(out) == 3L, "the join adds no rows and drops none")
})

cat("refresh_biblio_from_dict -- #2001\n")

##A biblio frame in the shape getrows() has by the time the refresh runs: the
##Redivis column names, .csv already stripped from `table`.
fake_biblio <- function(...) {
    rows <- list(...)
    d <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE)
    names(d) <- c("table", "DOI__for_paper_", "Reference_x", "URL__for_data_",
                  "Derived_License", "Description", "BibTex")
    d
}
biblio_row <- function(table, doi = "", reference = "", url = "", derived = "",
                       description = "", bibtex = "@misc{x}") {
    c(table, doi, reference, url, derived, description, bibtex)
}
refresh <- function(b, d) suppressMessages(refresh_biblio_from_dict(b, d))

THE_TEST_THAT_MATTERS <- function() {
    ##An empty dictionary cell must never blank a published biblio value. This
    ##is `cdm_timss03` today -- biblio holds a paper DOI the dictionary lacks --
    ##and it is the orphan-deletion pattern that removed provenance for four
    ##live su_2024_* tables.
    b <- fake_biblio(biblio_row("a_2020", doi = "10.1007/s10763-018-9916-9",
                                description = "published text"))
    for (empty in list(NA_character_, "", "NA")) {
        d <- fake_sheet(sheet_row("a_2020"))
        d$`DOI (for paper)`[1] <- empty
        d$Description[1]       <- empty
        out <- refresh(b, d)$biblio
        check(out$DOI__for_paper_[1] == "10.1007/s10763-018-9916-9" &&
              out$Description[1] == "published text",
              paste0("a dictionary cell holding ",
                     if (is.na(empty)) "NA" else paste0("'", empty, "'"),
                     " never blanks a published value"))
    }
}
THE_TEST_THAT_MATTERS()

local({
    ##The 163 conflicts: the dictionary is the corrected side.
    b <- fake_biblio(biblio_row("rmet_higgins_2022_tas",
                                description = "the paper's title, in the wrong field"))
    d <- fake_sheet(sheet_row("rmet_higgins_2022_tas",
                              description = "Toronto Alexithymia Scale"))
    res <- refresh(b, d)
    check(res$biblio$Description[1] == "Toronto Alexithymia Scale",
          "the dictionary wins a conflict on an already-published row")
    check(nrow(res$log) == 1L && res$log$kind[1] == "conflict",
          "the change is logged as a conflict")
    check(res$log$was[1] == "the paper's title, in the wrong field" &&
          res$log$now[1] == "Toronto Alexithymia Scale",
          "the log carries both sides, so the first run is reviewable as a list")
})

local({
    ##The 62 fills.
    b <- fake_biblio(biblio_row("a_2020"))
    d <- fake_sheet(sheet_row("a_2020", description = "Big Five Inventory"))
    res <- refresh(b, d)
    check(res$biblio$Description[1] == "Big Five Inventory",
          "a blank biblio cell is filled from the dictionary")
    check(res$log$kind[1] == "fill", "the change is logged as a fill")
})

local({
    ##Churn control. A run that rewrote every row for a resolver prefix or a
    ##case difference would bury the 226 real changes in a 4,261-row diff.
    b <- fake_biblio(biblio_row("a_2020", doi = "https://doi.org/10.1/x",
                                derived = "CC BY 4.0",
                                description = "Spatial  reasoning "))
    d <- fake_sheet(sheet_row("a_2020", doi = "doi: 10.1/x", derived = "cc by 4.0",
                              description = "Spatial reasoning"))
    res <- refresh(b, d)
    check(nrow(res$log) == 0L,
          "a DOI resolver prefix, a licence spelling and whitespace are not changes")
    check(res$biblio$DOI__for_paper_[1] == "https://doi.org/10.1/x",
          "an unchanged cell keeps the published bytes")
})

local({
    ##Case IS significant in a description: an instrument name that changed case
    ##changed. (DOIs and licences are the two exceptions above.)
    b <- fake_biblio(biblio_row("a_2020", description = "dreem"))
    d <- fake_sheet(sheet_row("a_2020", description = "DREEM"))
    check(nrow(refresh(b, d)$log) == 1L, "a case change in a Description is a change")
})

local({
    b <- fake_biblio(biblio_row("A_2020", description = "old"))
    d <- fake_sheet(sheet_row("a_2020", description = "new"))
    check(refresh(b, d)$biblio$Description[1] == "new",
          "the key match is case-insensitive (307 tables depend on this)")
})

local({
    ##getrows() strips .csv from biblio before writing; some dictionary rows
    ##still carry it.
    b <- fake_biblio(biblio_row("a_2020", description = "old"))
    d <- fake_sheet(sheet_row("a_2020"))
    d$table[1] <- "a_2020.csv"; d$table.lower[1] <- "a_2020.csv"
    d$Description[1] <- "new"
    check(refresh(b, d)$biblio$Description[1] == "new",
          "a dictionary row still carrying .csv matches the stripped biblio row")
})

local({
    ##A truncated sheet must be able to say "no change", never "wrong change".
    b <- fake_biblio(biblio_row("a_2020", description = "published"),
                     biblio_row("b_2020", description = "published"))
    d <- fake_sheet(sheet_row("b_2020", description = "published"))
    res <- refresh(b, d)
    check(res$biblio$Description[1] == "published" && nrow(res$log) == 0L,
          "a biblio row the dictionary does not mention is left alone")
    check(nrow(res$biblio) == 2L, "the refresh adds no rows and drops none")
})

local({
    ##BibTeX is cached on purpose -- regenerating costs a DOI fetch plus a
    ##Claude call, and the model does not return byte-identical BibTeX twice.
    b <- fake_biblio(biblio_row("a_2020", bibtex = "@misc{cached}"))
    d <- fake_sheet(sheet_row("a_2020", description = "x"))
    check(refresh(b, d)$biblio$BibTex[1] == "@misc{cached}",
          "the refresh never touches BibTex")
})

local({
    ##comps/nom/sim spell the licence column with an underscore.
    b <- fake_biblio(biblio_row("a_2020", derived = "CC0 1.0"))
    d <- fake_sheet(sheet_row("a_2020"))
    names(d)[names(d) == "Derived License"] <- "Derived_License"
    d$Derived_License[1] <- "CC BY 4.0"
    check(refresh(b, d)$biblio$Derived_License[1] == "CC BY 4.0",
          "both dictionary spellings of the licence column are read")
})

local({
    ##A sheet with no such column at all is a sheet, not an error.
    b <- fake_biblio(biblio_row("a_2020", url = "http://example.org"))
    d <- fake_sheet(sheet_row("a_2020"))
    d[["URL (for data)"]] <- NULL
    check(refresh(b, d)$biblio$URL__for_data_[1] == "http://example.org",
          "a dictionary with no URL column leaves the biblio URL alone")
})

local({
    ##The dictionary has known duplicate rows (dictionary_duplicates_2026-08-24).
    b <- fake_biblio(biblio_row("a_2020", description = "old"))
    d <- fake_sheet(sheet_row("a_2020", description = "first"),
                    sheet_row("a_2020", description = "second"))
    res <- refresh(b, d)
    check(res$biblio$Description[1] == "first" && nrow(res$biblio) == 1L,
          "a duplicated dictionary row does not duplicate or double-write biblio")
})

local({
    ##The log is written even when nothing drifted: "nothing changed" is a
    ##different and more useful statement than a missing file.
    tmplog <- tempfile(fileext = ".csv")
    on.exit(unlink(tmplog), add = TRUE)
    b <- fake_biblio(biblio_row("a_2020", description = "same"))
    d <- fake_sheet(sheet_row("a_2020", description = "same"))
    suppressMessages(refresh_biblio_from_dict(b, d, "core", log.file = tmplog))
    check(file.exists(tmplog), "an empty refresh still writes its log")
    check(identical(names(readr::read_csv(tmplog, show_col_types = FALSE)),
                    c("table", "column", "kind", "was", "now")),
          "the empty log keeps the full header")
})


##------------------------------------------------- description overrides ---
##DESCRIPTION_OVERRIDES is the one place a WRONG human cell can be corrected,
##so the load-bearing property is the guard, not the replacement: it must fire
##only on an exact match with the superseded text, and it must disarm itself
##the moment a human fixes the sheet.
local({
    ov <- list(list(table = "a_2020", issue = "#1",
                    superseded = "the wrong instrument",
                    corrected  = "the right instrument", why = "test"))
    ap <- function(b) suppressMessages(suppressWarnings(
        apply_description_overrides(b, "core", ov)))

    b <- ap(fake_biblio(biblio_row("a_2020", description = "the wrong instrument")))
    check(identical(b$Description[1], "the right instrument"),
          "an exact match on the superseded text is corrected")

    ##The guard. Anything other than the recorded text is left alone -- this is
    ##what keeps the override from being "the Description looks wrong to me".
    b <- ap(fake_biblio(biblio_row("a_2020", description = "something else entirely")))
    check(identical(b$Description[1], "something else entirely"),
          "a Description that is not the recorded text is never touched")

    ##Self-disarming: once the sheet says the corrected text, the entry is spent
    ##and the human's cell wins again with no code change.
    b <- ap(fake_biblio(biblio_row("a_2020", description = "the right instrument")))
    check(identical(b$Description[1], "the right instrument"),
          "an already-corrected sheet cell is left as the human wrote it")

    ##Whitespace in the sheet carries no meaning and must not defeat a match.
    b <- ap(fake_biblio(biblio_row("a_2020", description = "  the wrong   instrument ")))
    check(identical(b$Description[1], "the right instrument"),
          "the match is whitespace-normalised")

    ##A stale entry must be audible. Silence would let a correction that no
    ##longer applies sit in the file forever.
    w <- tryCatch({
        apply_description_overrides(
            fake_biblio(biblio_row("a_2020", description = "moved on")), "core", ov)
        NULL
    }, warning = function(w) conditionMessage(w))
    check(!is.null(w) && grepl("did not match", w, fixed = TRUE),
          "a non-matching override warns rather than failing silently")

    ##A table absent from this source's biblio is not an error: the same
    ##override list is applied to core/comps/nom/sim, and only core has these.
    b <- ap(fake_biblio(biblio_row("other_2020", description = "untouched")))
    check(identical(b$Description[1], "untouched"),
          "an override for a table this source lacks is a no-op")
})

local({
    ##Every shipped entry must be well-formed, or it fails silently at export
    ##time on a table nobody is looking at.
    bad <- Filter(function(o)
        !all(nzchar(c(o$table, o$issue, o$superseded, o$corrected, o$why))) ||
        identical(desc_norm(o$superseded), desc_norm(o$corrected)),
        DESCRIPTION_OVERRIDES)
    check(length(bad) == 0L,
          "every DESCRIPTION_OVERRIDES entry is complete and actually changes the text")
    check(!anyDuplicated(vapply(DESCRIPTION_OVERRIDES, function(o) o$table, character(1))),
          "no table carries two Description overrides")
})

##------------------------------------------------------------------ result ---
cat("\n")
if (failures > 0L) { cat(failures, "FAILURE(S)\n"); quit(status = 1L) }
cat("all tests passed\n")
