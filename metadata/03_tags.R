##Tags: one hand-annotated Google Sheet per source, unioned with one git-tracked
##CSV of automated tags per source.
##
##Mirrors the per-source `dbs` structure 02_biblio.R already uses. `core` is the
##long-standing "IRW Tags" sheet; `nom` was added for issue #1689, which found
##the non-core branches had nowhere to record tags. `comp` and `sim` are
##deliberately absent -- see Rpkg/inst/developer/tags.md for why.
##
##The automated half (issue #1723, design in #1708) exists because there is no
##Sheets service account and there is not going to be one. The Sheet stays
##read-only from code and authoritative for anything a human touched; the
##tagger's output lands in ../tags/*_auto.csv and is unioned here, human rows
##winning on conflict. "Where do I change this tag?" therefore has two answers,
##and the auto file's `Rater` column is what tells them apart.

library(gsheet)

##Multi-select normalisation for `sample` and `construct type`, applied after
##the sheet export and before write_csv. See tag_normalize.R and issue #1720.
##The Google Sheet itself is deliberately not modified.
source("tag_normalize.R")

##Columns kept, by POSITION, from the 13-column sheet:
##  1 table, 6:12 Age Range .. Primary Language(s), 3 Construct Name
##
##DO NOT "tidy" this into a by-name selection without reading the note below.
##Column 4 ("Context Text") is omitted on purpose: it holds verbatim excerpts
##from source papers, and this positional selection is the only thing keeping
##that raw text out of the public CSVs. Reordering the sheet silently changes
##what gets published. See .claude/skills/irw-site-update/SKILL.md.
##
##The auto files carry the same 13 columns and the same Context Text hazard, so
##they go through the SAME selection. Never rbind an auto file into an
##already-selected frame; tests/test_tags_union.R asserts that it never happens.
KEEP_COLS <- c(1, 6:12, 3)

##Row 1 of every tags sheet is a template/instruction row, not data, and is
##dropped. Verify rather than assume: a sheet missing this row would otherwise
##lose its first real table without any error.
INSTRUCTION_SENTINEL <- "should match what is on redivis"

##The exact 13-column layout stage_tag_row.py writes. Unlike the Sheet, these
##files are ours, so we can demand the header match exactly rather than merely
##counting columns -- that is what makes applying KEEP_COLS to them safe.
AUTO_COLS <- c(
    "table", "Rater", "Construct Name", "Context Text", "Item text available?",
    "Age Range", "Child Age (for child-focused studies)", "Sample",
    "Construct type", "Measurement tool", "Item format", "Primary Language(s)",
    "Notes"
)

##Every row in an auto file must be machine-written. A human row here would be
##silently outranked by the Sheet, so refuse it rather than lose it.
AUTO_RATER <- "claude-auto"

##Shared column selection and key normalisation, applied identically to sheet
##rows and auto rows. Everything downstream assumes it has run.
select_tag_cols <- function(tag, label) {
    if (ncol(tag) < max(KEEP_COLS)) {
        stop(label, ": expected at least ", max(KEEP_COLS),
             " columns, found ", ncol(tag),
             ". Layout changed -- re-check KEEP_COLS before proceeding.")
    }
    tag <- tag[, KEEP_COLS]
    names(tag) <- tolower(names(tag))
    tag$table <- tolower(tag$table)
    tag[!is.na(tag$table), ]
}

##Reads one auto-tag file. Returns NULL when the source has none configured, or
##the file is missing or empty, so an absent auto file degrades to the previous
##sheet-only behaviour instead of failing the pipeline.
read_auto_tags <- function(path, label) {
    if (is.null(path)) return(NULL)
    if (!file.exists(path)) {
        print(paste0(label, ": no auto-tag file at ", path, " -- sheet only"))
        return(NULL)
    }

    ##Read every column as character: these are free-text tags, and type
    ##guessing would turn a numeric-looking language code into a double.
    auto <- readr::read_csv(
        path,
        col_types = readr::cols(.default = readr::col_character()),
        progress = FALSE
    )
    if (!nrow(auto)) return(NULL)

    if (!identical(names(auto), AUTO_COLS)) {
        stop(label, ": ", path, " header does not match the expected 13-column ",
             "layout. KEEP_COLS selects by position, so a changed header here ",
             "would publish the wrong columns -- including Context Text. Found: ",
             paste(names(auto), collapse = ", "))
    }

    rater <- trimws(as.character(auto[["Rater"]]))
    bad <- is.na(rater) | rater != AUTO_RATER
    if (any(bad)) {
        stop(label, ": ", path, " has ", sum(bad), " row(s) whose Rater is not '",
             AUTO_RATER, "' (row ", paste(which(bad), collapse = ", "),
             "). Human-entered tags belong in the Google Sheet, which wins on ",
             "conflict -- a human row placed here would be silently discarded.")
    }

    select_tag_cols(auto, label)
}

get_tags <- function(db) {
    tag <- gsheet2tbl(db$url)

    first <- trimws(as.character(tag[[1]][1]))
    if (is.na(first) || !identical(tolower(first), INSTRUCTION_SENTINEL)) {
        stop(db$name, ": expected the instruction row ('", INSTRUCTION_SENTINEL,
             "') directly under the header, found '", first,
             "'. Refusing to drop row 1 -- it looks like real data.")
    }
    tag <- tag[-1, ]

    ##Everything through the print below reproduces the original core-only
    ##script's behaviour exactly; do not "fix" it here without regenerating and
    ##reviewing tags.csv, which feeds the public Redivis table.
    tag <- select_tag_cols(tag, db$name)

    ##Rows naming a table but carrying no tags are counted, not dropped --
    ##long-standing behaviour, and the count is the useful signal here.
    n <- apply(tag[, -1], 1, function(x) sum(!is.na(x)))
    print(paste0(db$name, ": ", nrow(tag), " rows -> ", db$file.out,
                 " (", sum(n == 0), " named but untagged)"))

    ##Union the automated tags. Human rows win on conflict, keyed on `table`.
    ##Dropping superseded auto rows here is also the retirement path: once a
    ##human tags a table, its auto row stops being published whether or not
    ##anyone remembers to delete it from the file.
    auto <- read_auto_tags(db$file.auto, db$name)
    if (!is.null(auto)) {
        superseded <- auto$table %in% tag$table
        auto <- auto[!superseded, ]
        stopifnot(identical(names(auto), names(tag)))
        tag <- rbind(tag, auto)
        print(paste0(db$name, ": +", nrow(auto), " auto rows from ", db$file.auto,
                     " (", sum(superseded), " superseded by the sheet)"))
    }

    ##Normalise the multi-select columns before writing. Fails loudly on any
    ##atom outside the controlled vocabulary rather than publishing it -- the
    ##union happens above precisely so auto rows face the same check.
    tag <- normalize_tag_columns(tag)

    readr::write_csv(tag, db$file.out)
    invisible(tag)
}

dbs <- list(
    core = list(name = "core",
                url = 'https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123',
                file.auto = "../tags/tags_auto.csv",
                file.out = "tags.csv"),
    ##`nom` has no file.auto on purpose. tags/nominal_tags_staging.csv looks like
    ##an auto file -- same 13 columns -- but it is an empty scaffold: every Rater
    ##and every Construct Name is blank, and it still carries the sheet's
    ##instruction row. It is a paste queue for a human, not tagger output. Wiring
    ##it here would publish 14 tag-less rows and a table named "should match what
    ##is on redivis". Give it a file.auto only once something writes real tags to
    ##it with Rater = claude-auto.
    nom  = list(name = "nom",
                url = 'https://docs.google.com/spreadsheets/d/1v3toO6OPts_HIjcjHTOb9_v2Ne2oXZSTkGTeO6fUyrg/edit?gid=126134123#gid=126134123',
                file.out = "nominal_tags.csv")
)

##tests/test_tags_union.R sources this file for the functions above; it must not
##reach the network or overwrite the published CSVs while doing so.
if (!identical(getOption("irw.tags.run"), FALSE)) {
    for (i in seq_along(dbs)) {
        get_tags(dbs[[i]])
    }
}
