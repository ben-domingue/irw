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
                     custom_derived = "", custom_source = "",
                     contributor = DICT_AUTO_CONTRIBUTOR, reshare = "Public") {
    c(table, tolower(table), description, "", "", doi, "", custom_source,
      reshare, derived, custom_derived, "", contributor, "9/6/2026")
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

##------------------------------------------------------------------ result ---
cat("\n")
if (failures > 0L) { cat(failures, "FAILURE(S)\n"); quit(status = 1L) }
cat("all tests passed\n")
