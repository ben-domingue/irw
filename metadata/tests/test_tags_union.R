##Tests for the sheet/auto-tag union in 03_tags.R (issue #1723).
##
##Runs offline: gsheet2tbl is stubbed, so nothing here touches the network, the
##Google Sheets, or the published CSVs. Run it from this directory:
##
##    Rscript tests/test_tags_union.R
##
##THE TEST THAT MATTERS is context_text_never_published(). 03_tags.R keeps
##"Context Text" -- verbatim excerpts from source papers -- out of the public
##CSVs by selecting columns positionally (KEEP_COLS). The auto-tag files carry
##that same column, populated. A naive rbind of an auto file into the published
##frame would publish paper text. #1708 asked for a test asserting it cannot;
##this is that test.

options(irw.tags.run = FALSE)   ##source the functions, do not run the pipeline
source("03_tags.R")

failures <- 0L
ok <- function(what) cat("  ok   -", what, "\n")
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
PAPER_TEXT <- "VERBATIM EXCERPT FROM A COPYRIGHTED PAPER - MUST NOT BE PUBLISHED"

##A sheet export: same 13 columns, instruction row first, as gsheet2tbl returns.
fake_sheet <- function(tables) {
    instruction <- c("should match what is on redivis",
                     rep("template", length(AUTO_COLS) - 1))
    rows <- lapply(tables, function(tb) c(
        tb, "jdtrinh", paste0("Human construct for ", tb), PAPER_TEXT, "Yes",
        "Adult (18+y)", NA, "Educational", "Cognitive/educational",
        "Survey/questionnaire", "Likert Scale/selected response", "eng", "note"))
    m <- rbind(instruction, do.call(rbind, rows))
    d <- as.data.frame(m, stringsAsFactors = FALSE)
    names(d) <- AUTO_COLS
    tibble::as_tibble(d)
}

write_auto <- function(path, tables, rater = AUTO_RATER, cols = AUTO_COLS) {
    rows <- lapply(tables, function(tb) c(
        tb, rater, paste0("Auto construct for ", tb), PAPER_TEXT, "No",
        "Child (<18y)", "Early (<6y)", "Clinical", "Developmental",
        "Observational rating", "Free response", "spa", "auto note"))
    d <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE)
    names(d) <- cols
    readr::write_csv(d, path)
    path
}

##Runs get_tags() against stubbed inputs and returns the written CSV.
run_union <- function(sheet_tables, auto_path) {
    out <- tempfile(fileext = ".csv")
    ##Shadow the package function with a global binding. `<<-` would walk past
    ##the global env and hit gsheet's locked namespace, so assign explicitly.
    assign("gsheet2tbl", function(url) fake_sheet(sheet_tables), envir = globalenv())
    on.exit(rm("gsheet2tbl", envir = globalenv()), add = TRUE)
    get_tags(list(name = "test", url = "stub://sheet",
                  file.auto = auto_path, file.out = out))
    readr::read_csv(out, col_types = readr::cols(.default = readr::col_character()),
                    progress = FALSE)
}

##------------------------------------------------------------------- tests ---
cat("\ncontext text\n")
context_text_never_published <- function() {
    auto <- write_auto(tempfile(fileext = ".csv"), c("auto_only_tbl"))
    res  <- run_union(c("human_tbl"), auto)

    check(!"context text" %in% names(res), "no 'context text' column in the output")
    check(!any(grepl(PAPER_TEXT, as.matrix(res), fixed = TRUE)),
          "no cell anywhere contains the paper excerpt")
    check(!"rater" %in% names(res), "no 'rater' column leaks into the output")
    check(!"notes" %in% names(res), "no 'notes' column leaks into the output")
}
context_text_never_published()

cat("\nprecedence\n")
precedence <- function() {
    auto <- write_auto(tempfile(fileext = ".csv"), c("shared_tbl", "auto_only_tbl"))
    res  <- run_union(c("human_tbl", "shared_tbl"), auto)

    check(nrow(res) == 3, "3 rows: 2 human + 1 non-superseded auto")
    check(sum(res$table == "shared_tbl") == 1, "the contested table appears exactly once")
    check(res$`construct name`[res$table == "shared_tbl"] == "Human construct for shared_tbl",
          "human row wins on conflict")
    check("auto_only_tbl" %in% res$table, "auto row survives for a table the sheet lacks")
    check(res$`construct name`[res$table == "auto_only_tbl"] == "Auto construct for auto_only_tbl",
          "the surviving auto row keeps its own values")
}
precedence()

cat("\nschema\n")
schema <- function() {
    auto      <- write_auto(tempfile(fileext = ".csv"), c("auto_only_tbl"))
    with_auto <- run_union(c("human_tbl"), auto)
    no_auto   <- run_union(c("human_tbl"), NULL)

    check(identical(names(with_auto), names(no_auto)),
          "union output has the same columns as sheet-only output")
    check(identical(names(no_auto), tolower(AUTO_COLS[KEEP_COLS])),
          "columns are exactly KEEP_COLS, lowercased")
    check(nrow(run_union(c("human_tbl"), tempfile(fileext = ".csv"))) == 1,
          "a missing auto file degrades to sheet-only rather than failing")
}
schema()

cat("\nguards\n")
guards <- function() {
    human_row <- write_auto(tempfile(fileext = ".csv"), c("x_tbl"), rater = "jdtrinh")
    expect_error(run_union(c("human_tbl"), human_row),
                 "Rater is not 'claude-auto'",
                 "a human-rated row in an auto file is refused, not silently dropped")

    shuffled <- AUTO_COLS
    shuffled[3:4] <- shuffled[4:3]   ##swap Construct Name and Context Text
    reordered <- write_auto(tempfile(fileext = ".csv"), c("x_tbl"), cols = shuffled)
    expect_error(run_union(c("human_tbl"), reordered),
                 "header does not match the expected 13-column layout",
                 "a reordered auto header is refused before KEEP_COLS can misfire")

    ##Sentinel rows: SKILL.md Steps 2/5 tell the tagger to stage table + Rater +
    ##Notes only, every tag field blank, when a source is paywalled or has no
    ##working link. Neither Rater nor Notes survives KEEP_COLS, so publishing one
    ##yields a bare table name that reads as "tagged" everywhere downstream.
    ###1723's first live union (2026-08-31) shipped 5 of these.
    write_row <- function(path, values) {
        d <- as.data.frame(matrix("", nrow = 1, ncol = length(AUTO_COLS)),
                           stringsAsFactors = FALSE)
        names(d) <- AUTO_COLS
        for (nm in names(values)) d[1, nm] <- values[[nm]]
        readr::write_csv(d, path)
        path
    }

    sentinel <- write_row(tempfile(fileext = ".csv"), list(
        table = "paywalled_tbl", Rater = AUTO_RATER,
        Notes = "cannot fully access due to paywall"))
    out <- run_union(c("human_tbl"), sentinel)
    check(!("paywalled_tbl" %in% out$table),
          "a tag-less sentinel auto row is not published")
    check(nrow(out) == 1,
          "dropping a sentinel leaves the sheet rows untouched")

    ##The guard keys on "no tag content at all", not "some fields missing" --
    ##a partially tagged auto row must still publish.
    partial <- write_row(tempfile(fileext = ".csv"), list(
        table = "partial_tbl", Rater = AUTO_RATER, `Age Range` = "Adult (18+)"))
    out2 <- run_union(c("human_tbl"), partial)
    check("partial_tbl" %in% out2$table,
          "an auto row with any real tag content is still published")
}
guards()

cat("\nrepo files\n")
repo_files <- function() {
    wired <- Filter(function(db) !is.null(db$file.auto), dbs)
    check(length(wired) > 0, "at least one source is wired to an auto file")
    for (db in wired) {
        p <- db$file.auto
        if (!file.exists(p)) { check(FALSE, paste(p, "exists")); next }
        got <- names(readr::read_csv(p, n_max = 0, show_col_types = FALSE))
        check(identical(got, AUTO_COLS), paste0(basename(p), " has the expected header"))
        raters <- unique(trimws(readr::read_csv(p, col_types = readr::cols(.default = readr::col_character()),
                                                progress = FALSE)$Rater))
        check(identical(raters, AUTO_RATER), paste0(basename(p), " is entirely ", AUTO_RATER))
    }
}
repo_files()

cat("\n")
if (failures > 0L) { cat(failures, "FAILURE(S)\n"); quit(status = 1L) }
cat("all tests passed\n")
