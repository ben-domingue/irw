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


##--------------------------------------------- retired tables (#1765, 2.5a) ---
##drop_retired_tables() removes tags for tables the IRW no longer publishes.
##The failure modes matter more than the happy path: a missing or truncated
##metadata.csv must never be able to delete the tag corpus, and the match must
##be case-insensitive because 308 tag rows differ from their metadata row only
##by case.

with_oracle <- function(tables, f) {
    d <- tempfile(); dir.create(d)
    live <- file.path(d, "metadata.csv")
    readr::write_csv(data.frame(table = tables), live)
    on.exit(unlink(d, recursive = TRUE), add = TRUE)
    f(live)
}

tag3 <- data.frame(table = c("alive_one", "RETIRED_one", "alive_two"),
                   `age range` = c("Adult (18+)", "Mixed", "Mixed"),
                   check.names = FALSE)

##Happy path: the retired row goes, the live ones stay.
with_oracle(c(paste0("filler", 1:1200), "alive_one", "alive_two"), function(live) {
    db <- list(name = "t", file.live = live, file.out = file.path(tempdir(), "tags.csv"))
    out <- drop_retired_tables(tag3, db)
    check(nrow(out) == 2 && !("RETIRED_one" %in% out$table),
          "drop_retired_tables removes a tag row whose table is not live")
    side <- file.path(tempdir(), "retired_tags.csv")
    check(file.exists(side) && nrow(readr::read_csv(side, show_col_types = FALSE)) == 1,
          "dropped rows are written to retired_tags.csv, not discarded")
})

##Case-insensitivity: 308 real rows depend on this.
with_oracle(c(paste0("filler", 1:1200), "ALIVE_ONE", "alive_two"), function(live) {
    db <- list(name = "t", file.live = live, file.out = file.path(tempdir(), "tags2.csv"))
    out <- drop_retired_tables(tag3, db)
    check("alive_one" %in% out$table,
          "a tag row matching its metadata row only by case is kept, not dropped")
})

##A truncated oracle must not be able to wipe the corpus.
with_oracle(c("alive_one"), function(live) {
    db <- list(name = "t", file.live = live, file.out = file.path(tempdir(), "tags3.csv"))
    out <- suppressWarnings(drop_retired_tables(tag3, db))
    check(nrow(out) == nrow(tag3),
          "an implausibly small metadata.csv is refused as an oracle, nothing dropped")
})

##A missing oracle is a warning, not a silent purge and not a hard stop.
local({
    db <- list(name = "t", file.live = file.path(tempdir(), "does_not_exist.csv"),
               file.out = file.path(tempdir(), "tags4.csv"))
    out <- suppressWarnings(drop_retired_tables(tag3, db))
    check(nrow(out) == nrow(tag3),
          "a missing metadata.csv publishes everything rather than dropping it")
})

##nom has no file.live and must be left entirely alone.
local({
    out <- drop_retired_tables(tag3, list(name = "nom", file.out = "nominal_tags.csv"))
    check(identical(out, tag3), "a db with no file.live is untouched (nom)")
})

##--------------------------------------- derived age tags (#1760, decision 7) ---
cat("\nderived age tags\n")

write_derived <- function(rows, cols = DERIVED_COLS) {
    d <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE)
    names(d) <- cols
    f <- tempfile(fileext = ".csv")
    readr::write_csv(d, f)
    f
}

##A tag frame in the shape get_tags() has at the point apply_derived_tags runs.
tag_frame <- function() {
    data.frame(
        table = c("has_ages", "no_ages", "confirmed_one"),
        `age range` = c("Mixed", "Mixed", "Adult (18+)"),
        `child age (for child-focused studies)` = c("Adolescent (12-18y)", NA, NA),
        sample = c("Educational", "Clinical", "Representative"),
        `construct name` = c("A", "B", "C"),
        check.names = FALSE, stringsAsFactors = FALSE)
}

drow <- function(tb, ar, ca = NA, basis = DERIVED_BASIS)
    c(tb, ar, ca, basis, "18", "94", "2562", "0", "2026-09-01")

##The core case: a derived value beats the Sheet, on its own column only.
local({
    f <- write_derived(list(drow("has_ages", "Adult (18+)")))
    out <- apply_derived_tags(tag_frame(), f, "t")
    r <- out[out$table == "has_ages", ]
    check(r[["age range"]] == "Adult (18+)",
          "a derived age range overrides the sheet value")
    check(is.na(r[["child age (for child-focused studies)"]]),
          "child age is overridden too, including to blank")
    check(r[["sample"]] == "Educational" && r[["construct name"]] == "A",
          "no other column is touched by the override")
    check(nrow(out) == 3, "a matching derived row does not add a row")
})

##A table nobody has tagged gets a row created from the derivation alone.
local({
    f <- write_derived(list(drow("brand_new", "Child (<18y)", "Early (<6y)")))
    out <- apply_derived_tags(tag_frame(), f, "t")
    r <- out[out$table == "brand_new", ]
    check(nrow(out) == 4 && nrow(r) == 1,
          "a derived row for an untagged table is added")
    check(r[["age range"]] == "Child (<18y)" && is.na(r[["sample"]]),
          "an added row carries only the two derived columns")
})

##Ages cannot contradict `Non-human`; the derivation has no way to know.
local({
    tf <- tag_frame()
    tf[["age range"]][tf$table == "no_ages"] <- "Non-human"
    f <- write_derived(list(drow("no_ages", "Adult (18+)")))
    out <- apply_derived_tags(tf, f, "t")
    check(out[out$table == "no_ages", ][["age range"]] == "Non-human",
          "a Non-human tag is never overridden by a derived age")
})

##Case-insensitive matching, the trap that cost 308 rows elsewhere.
local({
    f <- write_derived(list(drow("HAS_AGES", "Adult (18+)")))
    out <- apply_derived_tags(tag_frame(), f, "t")
    check(nrow(out) == 3 && out[out$table == "has_ages", ][["age range"]] == "Adult (18+)",
          "matching is case-insensitive, so no duplicate row is created")
})

##Guards.
local({
    f <- write_derived(list(drow("has_ages", "Adult (18+)", basis = "vibes")))
    expect_error(apply_derived_tags(tag_frame(), f, "t"), "whose basis is not",
                 "a row whose basis is not derived_cov_age is refused")

    f2 <- write_derived(list(drow("has_ages", "Grown-ups")))
    expect_error(apply_derived_tags(tag_frame(), f2, "t"), "outside the controlled vocabulary",
                 "an age range outside the vocabulary is refused")

    f3 <- write_derived(list(drow("has_ages", "Mixed"), drow("HAS_AGES", "Adult (18+)")))
    expect_error(apply_derived_tags(tag_frame(), f3, "t"), "more than once",
                 "the same table twice in the derived file is refused")

    f4 <- write_derived(list(drow("has_ages", "Adult (18+)")[1:8]),
                        cols = DERIVED_COLS[1:8])
    expect_error(apply_derived_tags(tag_frame(), f4, "t"), "header does not match",
                 "a derived file with the wrong header is refused")
})

##Absent file and unwired source both degrade to sheet-plus-auto behaviour.
local({
    t0 <- tag_frame()
    check(identical(apply_derived_tags(t0, NULL, "nom"), t0),
          "a db with no file.derived is untouched (nom)")
    check(identical(apply_derived_tags(t0, file.path(tempdir(), "nope.csv"), "t"), t0),
          "a missing derived file leaves the tags unchanged")
})

##The published `sample` rule from #1760: General is the residual.
cat("\nsample frame residual (#1760, decision 3)\n")
local({
    x <- c("General/non-specific, Representative",
           "General/non-specific, Targeted/specific",
           "Educational, General/non-specific",
           "Representative, Targeted/specific",
           "General/non-specific")
    out <- normalize_multiselect(x, "sample")
    check(out[1] == "Representative" && out[2] == "Targeted/specific",
          "General/non-specific is dropped beside a specific frame value")
    check(out[3] == "Educational, General/non-specific",
          "a setting atom does not displace General/non-specific")
    check(out[4] == "Representative, Targeted/specific",
          "Representative and Targeted/specific are never collapsed")
    check(out[5] == "General/non-specific",
          "General/non-specific alone is left alone")
    check(identical(normalize_multiselect(out, "sample"), out),
          "the rule is idempotent")
})

cat("\n")
if (failures > 0L) { cat(failures, "FAILURE(S)\n"); quit(status = 1L) }
cat("all tests passed\n")
