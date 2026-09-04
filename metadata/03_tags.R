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

##The exact layout stage_tag_row.py writes. Unlike the Sheet, these files are
##ours, so we can demand the header match exactly rather than merely counting
##columns -- that is what makes applying KEEP_COLS to them safe.
##
##`Status` and `Reason` were appended for #1704, and APPENDED is the whole
##design: KEEP_COLS selects by position from the first 13 columns, so anything
##past them cannot reach the published table however it is filled in. They
##record whether the tagger reached a usable source and, when it did not, why.
##Never insert a new column in the middle of this vector -- that silently
##republishes different columns, Context Text among them.
AUTO_COLS <- c(
    "table", "Rater", "Construct Name", "Context Text", "Item text available?",
    "Age Range", "Child Age (for child-focused studies)", "Sample",
    "Construct type", "Measurement tool", "Item format", "Primary Language(s)",
    "Notes", "Status", "Reason"
)

##Every row in an auto file must be machine-written. A human row here would be
##silently outranked by the Sheet, so refuse it rather than lose it.
AUTO_RATER <- "claude-auto"

##Tables contributed by an auto file this run, collected for the provenance
##sidecar written after the union.
auto_tables <- character()

##Tables the derived age file supplied values for, so the sidecar does not
##credit those columns to the tagger.
derived_tables <- character()

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
        stop(label, ": ", path, " header does not match the expected ",
             length(AUTO_COLS), "-column layout. KEEP_COLS selects by position, ",
             "so a changed header here would publish the wrong columns -- ",
             "including Context Text. Found: ",
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

##Columns of the derived age file, and the only basis value it may carry.
DERIVED_COLS  <- c("table", "age range", "child age (for child-focused studies)",
                   "basis", "min_age", "max_age", "n_age", "share_under_18",
                   "generated")
DERIVED_BASIS <- "derived_cov_age"
AGE_RANGE_VOCAB <- c("Child (<18y)", "Adult (18+)", "Mixed",
                     "Elderly (minimum age >50)", "Non-human")

##Derived age tags outrank the Sheet -- for two columns only (#1760, decision 7,
##2026-09-01).
##
##This is a deliberate hole in the human-wins precedence set in #1723, and it is
##scoped as narrowly as the decision allows: `age range` and `child age` on
##tables whose own `cov_age` supports a derivation. The argument is that such a
##value is not an opinion competing with a rater's -- it is a measurement of the
##shipped table, which is what #1760 decided the column describes. Every other
##column, and every table without usable ages, keeps human precedence untouched.
##
##Why it has to exist at all: 03_tags.R drops an auto row for any table a human
##has tagged, and the Sheet is not writable from code (#1708 / 6.1). Without
##this, Rule A would tag the ~1,120 untagged tables and change none of the ~472
##`Mixed` rows that prompted the issue.
##
##The Sheet is never modified. The human value stays where it was typed, and
##reverting this is deleting the file.derived entry and re-running.
apply_derived_tags <- function(tag, path, label) {
    if (is.null(path)) return(tag)
    if (!file.exists(path)) {
        print(paste0(label, ": no derived age file at ", path,
                     " -- sheet and auto rows only"))
        return(tag)
    }
    der <- readr::read_csv(path,
                           col_types = readr::cols(.default = readr::col_character()),
                           progress = FALSE)
    if (!nrow(der)) return(tag)

    if (!identical(names(der), DERIVED_COLS)) {
        stop(label, ": ", path, " header does not match the expected layout. ",
             "Expected: ", paste(DERIVED_COLS, collapse = ", "),
             ". Found: ", paste(names(der), collapse = ", "))
    }
    basis <- trimws(as.character(der[["basis"]]))
    bad <- is.na(basis) | basis != DERIVED_BASIS
    if (any(bad)) {
        stop(label, ": ", path, " has ", sum(bad), " row(s) whose basis is not '",
             DERIVED_BASIS, "' (row ", paste(which(bad), collapse = ", "),
             "). Only a value computed from the table's own cov_age may outrank ",
             "the Sheet; anything else belongs in the Sheet or the auto file.")
    }
    ar <- trimws(as.character(der[["age range"]]))
    off <- !is.na(ar) & nzchar(ar) & !(ar %in% AGE_RANGE_VOCAB)
    if (any(off)) {
        stop(label, ": ", path, " has ", sum(off), " row(s) with an `age range` ",
             "outside the controlled vocabulary: ",
             paste0('"', unique(ar[off]), '"', collapse = ", "))
    }
    if (anyDuplicated(tolower(der$table))) {
        dup <- unique(tolower(der$table)[duplicated(tolower(der$table))])
        stop(label, ": ", path, " names ", length(dup),
             " table(s) more than once: ", paste(dup, collapse = ", "))
    }

    cols <- c("age range", "child age (for child-focused studies)")
    stopifnot(all(cols %in% names(tag)))

    key <- tolower(tag$table)
    idx <- match(tolower(der$table), key)
    hit <- !is.na(idx)

    changed <- 0L; confirmed <- 0L; preserved <- 0L
    for (i in which(hit)) {
        row <- idx[i]
        was <- tag[[cols[1]]][row]
        now <- der[[cols[1]]][i]

        ##`Non-human` is not a claim about ages, so ages cannot contradict it.
        ##The derivation has no way to know a table's respondents are not people
        ##-- that comes from the source -- and left unguarded it retagged four
        ##`Non-human` tables from their respondents' "ages" (caught in the
        ##2026-09-01 dry run). vocab.md says Non-human short-circuits; this is
        ##that sentence in code.
        if (identical(as.character(was), "Non-human")) {
            preserved <- preserved + 1L
            next
        }

        if (identical(as.character(was), as.character(now))) confirmed <- confirmed + 1L
        else changed <- changed + 1L
        for (cl in cols) tag[[cl]][row] <- der[[cl]][i]
    }

    ##Tables with no row anywhere yet: the derivation is the whole tag row.
    add <- der[!hit, , drop = FALSE]
    if (nrow(add)) {
        blank <- tag[0, , drop = FALSE]
        blank[seq_len(nrow(add)), ] <- NA_character_
        blank$table <- tolower(add$table)
        for (cl in cols) blank[[cl]] <- add[[cl]]
        tag <- rbind(tag, blank)
    }

    print(paste0(label, ": derived age tags from ", path, " -- ", changed,
                 " overridden, ", confirmed, " confirmed, ", preserved,
                 " Non-human preserved, ", nrow(add), " new row(s)"))
    tag
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
        ##Drop sentinel rows: the tagger stages `table`/`Rater`/`Notes` only,
        ##with every tag field blank, when a source is paywalled or has no
        ##working link (SKILL.md Steps 2/5). That row is a local marker meaning
        ##"attempted, unavailable" -- but neither Rater nor Notes survives
        ##KEEP_COLS, so publishing one yields a row that is nothing but a table
        ##name. It asserts the table is tagged without saying anything about it,
        ##and it makes the table read as covered in audit_tables.R's tags_csv
        ##column, so it will never resurface as needing tags. The `nom` branch
        ##below already refuses its staging file for exactly this reason
        ##("would publish 14 tag-less rows"); this is that guard in code rather
        ##than prose. First live union (2026-08-31, #1723) published 5 of them.
        ##They stay in tags_auto.csv -- that file plus the Sheet is what stops
        ##the tagger retrying a paywalled source, so nothing is re-attempted.
        empty <- apply(auto[, -1, drop = FALSE], 1,
                       function(x) all(is.na(x) | trimws(as.character(x)) == ""))
        if (any(empty)) {
            print(paste0(db$name, ": dropped ", sum(empty),
                         " tag-less auto row(s) (sentinels, not tags): ",
                         paste(auto$table[empty], collapse = ", ")))
            auto <- auto[!empty, , drop = FALSE]
        }
        stopifnot(identical(names(auto), names(tag)))
        ##Which tables the auto file contributed, so the published tags stay
        ##sweepable. KEEP_COLS drops the `Rater` column on the way in, so once a
        ##tagger value lands in tags.csv it is indistinguishable from a human's
        ##-- and a wrong one can then never be found again. A derived column does
        ##not have that problem (age_range_audit.csv records a verdict and reason
        ##per table, which is how #1760 could recompute 1,794 of them); a hand
        ##tag does, and an auto tag inherits it.
        ##
        ##Ben's ruling, 2026-09-02 (#1837): misplaced tags are not a deal-breaker
        ##and are reversible -- but reversible means recorded well enough to
        ##reverse. This is that record.
        auto_tables <<- c(auto_tables, as.character(auto$table))
        tag <- rbind(tag, auto)
        print(paste0(db$name, ": +", nrow(auto), " auto rows from ", db$file.auto,
                     " (", sum(superseded), " superseded by the sheet)"))
    }

    ##Derived age tags win over both the Sheet and the auto file, for their two
    ##columns only. After the union so it can override either source; before the
    ##liveness check so a derived row for a retired table is dropped like any
    ##other.
    tag <- apply_derived_tags(tag, db$file.derived, db$name)

    ##Whatever the derived file supplied is a measurement of the table, not a
    ##tagger assertion, and must not be credited to the tagger in the sidecar.
    ##Without this the trail claimed the tagger wrote `age range` on 389 tables
    ##whose value came from cov_age -- over-inclusive, and an audit trail that
    ##names the wrong source is worse than none.
    derived_tables <<- if (!is.null(db$file.derived) && file.exists(db$file.derived))
        tolower(trimws(readr::read_csv(db$file.derived, show_col_types = FALSE)$table)) else character()

    ##Drop tags for tables the IRW no longer publishes. 194 of the 2,480 rows
    ##in tags.csv name a table that is not live on Redivis -- retired or
    ##renamed -- and none of them is merely awaiting a metadata row (#1765).
    ##They are published anyway, so the table overstates coverage, and
    ##Rpkg's .irw_filter_rows_to_live_tables() then removes them again on read.
    ##That filter is correct but silent, so the published CSV and irw_tags()
    ##disagree by ~8% for reasons no user can see. Dropping here makes the
    ##published table mean what it says and leaves the R-package filter with
    ##nothing to do.
    ##
    ##metadata.csv is the liveness oracle rather than a Redivis call: 01
    ##runs before 03, and it is currently row-for-row identical to the live
    ##catalog (4,134 = 4,134, zero drift either way, #1765). Matching is
    ##case-insensitive -- 308 tag rows differ from their metadata row only by
    ##case, and a case-sensitive join would silently discard every one.
    tag <- drop_retired_tables(tag, db)

    ##Normalise the multi-select columns before writing. Fails loudly on any
    ##atom outside the controlled vocabulary rather than publishing it -- the
    ##union happens above precisely so auto rows face the same check.
    tag <- normalize_tag_columns(tag)

    readr::write_csv(tag, db$file.out)

    ##Sidecar rather than a new column in tags.csv: the published schema is read
    ##by Rpkg, Python-pkg and the site, and none of them should have to change to
    ##gain an audit trail. One row per table the tagger wrote, listing which of
    ##its columns still hold the auto value after the sheet and the derived file
    ##have had their say.
    write_tag_provenance(tag, db)
    invisible(tag)
}

##Which columns of a published row came from the tagger rather than a human.
##A table the tagger wrote but the sheet later superseded contributes nothing:
##by then the value is the human's.
write_tag_provenance <- function(tag, db) {
    ##Derive the name from the output file rather than hardcoding it: `core` and
    ##`nom` both write into the same directory, and a fixed name meant the second
    ##source silently overwrote the first's sidecar with an empty file.
    out <- sub("\\.csv$", "_provenance.csv", db$file.out)
    cols <- setdiff(names(tag), "table")
    keep <- tolower(trimws(as.character(tag$table))) %in%
            tolower(trimws(unique(auto_tables)))
    rows <- tag[keep, , drop = FALSE]
    if (!nrow(rows)) {
        readr::write_csv(data.frame(table = character(), columns = character(),
                                    rater = character(), generated = character()),
                         out)
        return(invisible(NULL))
    }
    filled <- function(x) !is.na(x) & trimws(as.character(x)) != ""
    DERIVED_OWNED <- c("age range", "child age (for child-focused studies)")
    per <- vapply(seq_len(nrow(rows)), function(i) {
        set <- cols[vapply(cols, function(cl) filled(rows[[cl]][i]), logical(1))]
        if (tolower(trimws(rows$table[i])) %in% derived_tables)
            set <- setdiff(set, DERIVED_OWNED)
        paste(set, collapse = "; ")
    }, character(1))
    readr::write_csv(
        data.frame(table = rows$table, columns = per, rater = AUTO_RATER,
                   generated = format(Sys.time(), "%Y-%m-%d"),
                   stringsAsFactors = FALSE)[per != "", , drop = FALSE],
        out)
    print(paste0(db$name, ": wrote ", sum(per != ""),
                 " provenance row(s) to ", out))
    invisible(NULL)
}

##Rows whose table is absent from the live catalog. Returns `tag` unchanged,
##loudly, if the oracle is missing or implausibly small -- a truncated
##metadata.csv must never be able to delete the tag corpus.
drop_retired_tables <- function(tag, db, min_oracle_rows = 1000) {
    if (is.null(db$file.live)) return(tag)          ##nom has its own catalog
    if (!file.exists(db$file.live)) {
        warning(db$name, ": ", db$file.live, " not found; publishing ",
                nrow(tag), " tag rows without a liveness check. Run ",
                "01_metadata.R first.", call. = FALSE)
        return(tag)
    }
    live <- readr::read_csv(db$file.live, show_col_types = FALSE)
    if (!"table" %in% names(live) || nrow(live) < min_oracle_rows) {
        warning(db$name, ": ", db$file.live, " has ", nrow(live),
                " row(s); too few to trust as a liveness oracle (expected at ",
                "least ", min_oracle_rows, "). Skipping the retired-table ",
                "check rather than risk dropping live tags.", call. = FALSE)
        return(tag)
    }
    retired <- !(tolower(tag$table) %in% tolower(live$table))
    if (any(retired)) {
        ##Keep them on disk. These rows are real human annotation work, and a
        ##retired table can come back under the same name.
        out <- file.path(dirname(db$file.out),
                         paste0("retired_", basename(db$file.out)))
        readr::write_csv(tag[retired, , drop = FALSE], out)
        print(paste0(db$name, ": dropped ", sum(retired),
                     " tag row(s) for tables no longer live -> ", out))
        tag <- tag[!retired, , drop = FALSE]
    }
    tag
}

dbs <- list(
    core = list(name = "core",
                url = 'https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123',
                file.auto = "../tags/tags_auto.csv",
                file.derived = "../tags/age_range_derived.csv",
                file.live = "metadata.csv",
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
