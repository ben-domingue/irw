##Union the automated dictionary rows into the Data Dictionary sheet export.
##Issue #1732 (roadmap item 6b) -- the dictionary half of what #1723 did for
##tags. Sourced by 02_biblio.R before getrows(); nothing here touches the
##network, so tests/test_dict_union.R can exercise it offline.
##
##The rule, and it differs from 03_tags.R on purpose:
##
##  A HUMAN CELL WINS THE CELL IT OCCUPIES. An automated cell fills a cell the
##  human left empty. The whole automated row is never dropped.
##
##03_tags.R supersedes at ROW level -- one human row discards the entire
##automated row, including columns the human left blank -- which strands 19-76
##tables per column (#1863). For tags that is a residual. For the dictionary a
##sparse-but-present row is the common case, so row-level supersede would mean
##an automated writer could only ever reach a table with no dictionary row at
##all. Ben's ruling on #1732, 2026-09-03: build this column-wise from the start.

##The layout of dictionary_auto.csv. Names are OURS, so we can demand an exact
##match rather than counting columns -- that is what makes a name-keyed merge
##safe here where 03_tags.R had to select positionally.
##
##The two `Custom License` columns are given distinct names on our side because
##the sheet has the SAME name twice (positions 8 and 11) and a name-keyed union
##is ambiguous against that. resolve_dict_cols() below maps these onto whatever
##the sheet currently calls them.
DICT_AUTO_COLS <- c(
    "table", "table.lower", "Description", "URL (for data)", "Reference",
    "DOI (for paper)", "DOI (for data)", "Original License",
    "Custom License (source)", "Public Reshare?", "Derived License",
    "Custom License (derived)", "Notes", "Contributor", "Date"
)

##Columns that exist HERE and not in the sheet.
##
##`DOI (for data)` is the #1690 schema change, and it deliberately never becomes
##a sheet column. 979 dictionary rows put a *deposit* DOI (Dataverse, Mendeley,
##figshare, Zenodo, Dryad, OSF, ICPSR) in `DOI (for paper)`, which is a different
##object from the paper: its year is a deposit year, and resolving it gets the
##depositor rather than the authors. Splitting the two needed either a sheet
##column plus a 979-cell paste, or this. Ben chose this on 2026-09-06 --
##the automated file carries the new column, `union_dict()` creates it in the
##merged frame, and nobody edits the sheet.
DICT_AUTO_ONLY_COLS <- c("DOI (for data)")

##Every row in an automated file must be machine-written, for the same reason
##03_tags.R forces Rater: a human row placed here would be outranked by the
##sheet on every cell it shares, so refuse it rather than lose it.
DICT_AUTO_CONTRIBUTOR <- "automated"

##Columns a merge must never touch. The key identifies the row; Contributor and
##Date describe who wrote the SHEET row, and letting an automated file overwrite
##them would erase the human's authorship of a row it merely topped up.
DICT_KEY_COLS <- c("table", "table.lower")
DICT_NEVER_FILL <- c(DICT_KEY_COLS, "Contributor", "Date")

##A cell is blank if it is NA, empty, or the literal string "NA" -- the sheet
##stores all three and means the same thing by each (#1863's guard, restated).
dict_blank <- function(x) {
    x <- trimws(as.character(x))
    is.na(x) | x == "" | toupper(x) == "NA"
}

##Strip R's make.unique suffix: "Custom License...11" -> "Custom License".
dict_base_names <- function(x) sub("\\.\\.\\.[0-9]+$", "", x)

##Map each DICT_AUTO_COLS name onto the column the sheet actually uses.
##
##Twelve of the fourteen match by name. The two `Custom License` columns do not,
##because the sheet names them identically and gsheet2tbl/readr disambiguate
##them to "Custom License...8" and "Custom License...11". Resolved by ORDER
##among the columns whose base name is "Custom License": first is the source's
##terms (it follows `Original License`), second is what IRW redistributes under
##(it follows `Derived License`). metadata/hotfixes/fix-licenses.R read
##the second one by its mangled name for exactly that reason, before this change
##retired it.
##
##Once the sheet is renamed to two distinct names (#1732 step 1), this resolves
##by name instead and the ORDER branch stops being reached. Do not delete either
##column: 20 rows carry source terms and 4 carry derived terms, all on Public
##tables (verified 2026-09-06).
resolve_dict_cols <- function(dict, label = "dictionary") {
    nm <- names(dict)
    out <- setNames(rep(NA_character_, length(DICT_AUTO_COLS)), DICT_AUTO_COLS)

    plain <- setdiff(DICT_AUTO_COLS, c("Custom License (source)", "Custom License (derived)"))
    for (cl in plain) {
        hit <- which(nm == cl)
        ##An auto-only column is absent from the sheet by design, so NA is the
        ##right answer rather than an error. union_dict() calls
        ##ensure_dict_auto_cols() first, so by the time IT resolves, the column
        ##is there; other callers (tests/manual_dict_test.R reads the raw sheet)
        ##get NA and must not use it.
        if (length(hit) == 0L && cl %in% DICT_AUTO_ONLY_COLS) next
        if (length(hit) != 1L) {
            stop(label, ": expected exactly one column named '", cl, "', found ",
                 length(hit), ". The dictionary layout has changed -- re-check ",
                 "DICT_AUTO_COLS before proceeding.")
        }
        out[[cl]] <- nm[hit]
    }

    ##Post-rename: distinct names, matched directly.
    src <- which(nm == "Custom License (source)")
    drv <- which(nm == "Custom License (derived)")
    if (length(src) == 1L && length(drv) == 1L) {
        out[["Custom License (source)"]]  <- nm[src]
        out[["Custom License (derived)"]] <- nm[drv]
        return(out)
    }

    ##Pre-rename: two columns sharing the base name, resolved by order.
    cust <- which(dict_base_names(nm) == "Custom License")
    if (length(cust) != 2L) {
        stop(label, ": expected two `Custom License` columns (or one each of ",
             "'Custom License (source)' and 'Custom License (derived)' after the ",
             "#1732 rename), found ", length(cust), ": ",
             paste(nm[cust], collapse = ", "), ".")
    }
    out[["Custom License (source)"]]  <- nm[cust[1]]
    out[["Custom License (derived)"]] <- nm[cust[2]]
    out
}

##The join key. Case-insensitive on purpose: 307 table names in this corpus are
##not all-lowercase, and a case-sensitive join silently drops every one of them.
dict_key <- function(x) tolower(trimws(as.character(x)))

##Read one automated dictionary file. Returns NULL when the source has none
##configured, or the file is missing or empty, so an absent file degrades to the
##previous sheet-only behaviour instead of failing the pipeline -- the same
##contract read_auto_tags() has in 03_tags.R.
read_dict_auto <- function(path, label) {
    if (is.null(path)) return(NULL)
    if (!file.exists(path)) {
        message(label, ": no automated dictionary file at ", path, " -- sheet only")
        return(NULL)
    }

    ##Every column as character: these are free-text metadata fields, and type
    ##guessing would turn a numeric-looking license year or DOI suffix into a
    ##double. trim_ws = FALSE so a value is stored as it was staged.
    auto <- readr::read_csv(path,
                            col_types = readr::cols(.default = readr::col_character()),
                            trim_ws = FALSE, progress = FALSE)
    if (!nrow(auto)) return(NULL)

    if (!identical(names(auto), DICT_AUTO_COLS)) {
        stop(label, ": ", path, " header does not match the expected ",
             length(DICT_AUTO_COLS), "-column layout. Expected: ",
             paste(DICT_AUTO_COLS, collapse = ", "), ". Found: ",
             paste(names(auto), collapse = ", "))
    }

    contrib <- trimws(as.character(auto[["Contributor"]]))
    bad <- is.na(contrib) | contrib != DICT_AUTO_CONTRIBUTOR
    if (any(bad)) {
        stop(label, ": ", path, " has ", sum(bad), " row(s) whose Contributor is ",
             "not '", DICT_AUTO_CONTRIBUTOR, "' (row ",
             paste(which(bad), collapse = ", "),
             "). Human-entered rows belong in the sheet, which wins every cell ",
             "it fills -- a human row placed here would be silently outranked.")
    }

    ##`Public Reshare?` is not decoration: 02_biblio.R drops every non-Public row
    ##before biblio is built, so a row that leaves it blank vanishes from the
    ##published table with no error and no diff. Refuse it here instead.
    reshare <- trimws(as.character(auto[["Public Reshare?"]]))
    missing <- dict_blank(reshare)
    if (any(missing)) {
        stop(label, ": ", path, " has ", sum(missing), " row(s) with a blank ",
             "`Public Reshare?` (row ", paste(which(missing), collapse = ", "),
             "). 02_biblio.R drops non-Public rows, so a blank one would ",
             "silently never reach biblio.")
    }

    key <- dict_key(auto[["table.lower"]])
    key[dict_blank(key)] <- dict_key(auto[["table"]])[dict_blank(key)]
    if (any(dict_blank(key))) {
        stop(label, ": ", path, " has ", sum(dict_blank(key)),
             " row(s) with no table name.")
    }
    if (anyDuplicated(key)) {
        dup <- unique(key[duplicated(key)])
        stop(label, ": ", path, " names ", length(dup), " table(s) more than ",
             "once: ", paste(dup, collapse = ", "))
    }
    auto
}

##Drop automated rows for tables the IRW does not publish, using metadata.csv as
##the liveness oracle the way 03_tags.R's drop_retired_tables() does. 01 runs
##before 02, so the file is current.
##
##Returns `auto` unchanged, loudly, if the oracle is missing or implausibly
##small: a truncated metadata.csv must never be able to silently empty a staged
##batch.
##`pending.file`, when given, records the rows held back. They are HELD, not
##discarded: the row stays in dictionary_auto.csv and lands on the first run
##after the table is published.
##
##That window is the normal case, not an edge case. A batch's order is: clean
##the dataset, upload the table to a Redivis DRAFT, add the dictionary row,
##publish. 01_metadata.R lists tables from the RELEASED dataset version, so
##between the upload and the publish click every one of that batch's rows names
##a table metadata.csv has never heard of. Without this file the only trace is a
##message in a long pipeline log -- which is the silent-failure shape this whole
##change exists to end.
drop_dead_dict_rows <- function(auto, live.file, label, min_oracle_rows = 1000,
                                pending.file = NULL) {
    if (is.null(auto) || is.null(live.file)) {
        write_dict_pending(NULL, pending.file)
        return(auto)
    }
    if (!file.exists(live.file)) {
        warning(label, ": ", live.file, " not found; unioning ", nrow(auto),
                " automated row(s) without a liveness check. Run 01_metadata.R ",
                "first.", call. = FALSE)
        write_dict_pending(NULL, pending.file)
        return(auto)
    }
    live <- readr::read_csv(live.file, show_col_types = FALSE, progress = FALSE)
    if (!"table" %in% names(live) || nrow(live) < min_oracle_rows) {
        warning(label, ": ", live.file, " has ", nrow(live), " row(s); too few ",
                "to trust as a liveness oracle. Unioning without the check.",
                call. = FALSE)
        write_dict_pending(NULL, pending.file)
        return(auto)
    }
    key  <- dict_key(auto[["table.lower"]])
    key[dict_blank(key)] <- dict_key(auto[["table"]])[dict_blank(key)]
    keep <- key %in% dict_key(live$table)
    if (any(!keep)) {
        message(label, ": holding ", sum(!keep), " automated row(s) naming a ",
                "table absent from ", live.file,
                " (publish the table and they land next run): ",
                paste(auto[["table"]][!keep], collapse = ", "))
    }
    write_dict_pending(auto[!keep, , drop = FALSE], pending.file)
    auto[keep, , drop = FALSE]
}

##Always written, even when empty: an empty file says "nothing is waiting",
##which is a different and more useful statement than a missing file.
write_dict_pending <- function(pending, pending.file) {
    if (is.null(pending.file)) return(invisible(NULL))
    if (is.null(pending) || !nrow(pending)) {
        pending <- as.data.frame(
            setNames(replicate(length(DICT_AUTO_COLS), character(0), simplify = FALSE),
                     DICT_AUTO_COLS),
            check.names = FALSE)
    }
    readr::write_csv(pending, pending.file)
    if (nrow(pending)) {
        message("  wrote ", nrow(pending), " pending row(s) to ", pending.file)
    }
    invisible(NULL)
}

##Add any auto-only column the sheet does not carry, as all-blank, so the merge
##and everything after it can treat the frame as having the full layout.
##Appended at the end rather than inserted: 02_biblio.R selects by name, but the
##two `Custom License` columns are resolved by ORDER, and inserting a column
##between them would silently swap source terms for derived ones.
ensure_dict_auto_cols <- function(dict) {
    for (cl in DICT_AUTO_ONLY_COLS) {
        if (!cl %in% names(dict)) dict[[cl]] <- NA_character_
    }
    dict
}

##Normalise a DOI for COMPARISON only. Mirrors normalize() in
##automated_finding/doi_hygiene.py, which is the definition; the two are pinned
##together by a parity test in tests/test_dict_union.R rather than by this file
##shelling out to python on every pipeline run.
dict_norm_doi <- function(x) {
    x <- trimws(ifelse(is.na(x), "", as.character(x)))
    x <- trimws(sub("(?i)^\\s*(data\\s+doi|doi)\\s*:\\s*", "", x, perl = TRUE))
    x <- trimws(sub("(?i)^https?://(dx\\.)?doi\\.org/", "", x, perl = TRUE))
    x <- trimws(sub("\\.s[0-9]{3}$", "", x))
    trimws(sub("\\.$", "", x))
}

##Merge the automated rows into the sheet export, column-wise.
##
##Returns a list: `dict` (the merged frame, in the sheet's own column order and
##names, so everything downstream in 02_biblio.R is unchanged) and `provenance`
##(one row per table an automated cell reached, naming which cells).
union_dict <- function(dict, auto, label = "dictionary") {
    if (is.null(auto) || !nrow(auto)) {
        return(list(dict = ensure_dict_auto_cols(dict),
                    provenance = dict_provenance_frame()))
    }
    dict <- ensure_dict_auto_cols(dict)
    map <- resolve_dict_cols(dict, label)

    ##Columns eligible to be filled: everything but the key and the human's own
    ##authorship fields.
    fillable <- setdiff(DICT_AUTO_COLS, DICT_NEVER_FILL)

    dkey <- dict_key(dict[[map[["table.lower"]]]])
    dkey[dict_blank(dkey)] <- dict_key(dict[[map[["table"]]]])[dict_blank(dkey)]
    akey <- dict_key(auto[["table.lower"]])
    akey[dict_blank(akey)] <- dict_key(auto[["table"]])[dict_blank(akey)]

    idx <- match(akey, dkey)
    hit <- !is.na(idx)

    filled <- character(0)   ##"table\tcolumn;column"
    nfill  <- 0L
    ncleared <- 0L

    ##(a) tables the sheet already has: fill only the cells the human left blank.
    for (i in which(hit)) {
        row <- idx[i]
        got <- character(0)

        ##THE ONE EXCEPTION to "a human cell wins the cell it occupies", and it
        ##is narrow on purpose (#1690, Ben 2026-09-06). When the automated file
        ##says a table's `DOI (for data)` is exactly the value the sheet holds in
        ##`DOI (for paper)`, the sheet is citing a data deposit as the paper. The
        ##paper cell is cleared IN THE EXPORT so the site and the packages stop
        ##publishing it; the sheet itself is untouched, and every cleared cell is
        ##named in biblio_provenance.csv.
        ##
        ##Equality, not "the sheet's value looks like a deposit DOI": this may
        ##only ever remove a value the automated file has demonstrably preserved
        ##in the other column. Anything wider could silently drop the only
        ##citation a row has.
        ddoi <- auto[["DOI (for data)"]][i]
        pcol <- map[["DOI (for paper)"]]
        if (!dict_blank(ddoi) &&
            !dict_blank(dict[[pcol]][row]) &&
            identical(dict_norm_doi(dict[[pcol]][row]), dict_norm_doi(ddoi))) {
            dict[[pcol]][row] <- NA_character_
            got <- c(got, "-DOI (for paper)")
            ncleared <- ncleared + 1L
        }

        for (cl in fillable) {
            dcol <- map[[cl]]
            if (!dict_blank(dict[[dcol]][row])) next        ##human wins this cell
            val <- auto[[cl]][i]
            if (dict_blank(val)) next
            dict[[dcol]][row] <- val
            got <- c(got, cl)
        }
        if (length(got)) {
            filled <- c(filled, paste0(auto[["table"]][i], "\t",
                                       paste(got, collapse = "; ")))
            nfill <- nfill + 1L
        }
    }

    ##(b) tables the sheet does not have at all: the automated row is the row.
    add <- which(!hit)
    if (length(add)) {
        blankrow <- dict[0, , drop = FALSE]
        blankrow[seq_along(add), ] <- NA_character_
        for (cl in DICT_AUTO_COLS) blankrow[[map[[cl]]]] <- auto[[cl]][add]
        dict <- rbind(dict, blankrow)
        for (i in add) {
            got <- DICT_AUTO_COLS[vapply(DICT_AUTO_COLS,
                                         function(cl) !dict_blank(auto[[cl]][i]),
                                         logical(1))]
            got <- setdiff(got, DICT_KEY_COLS)
            filled <- c(filled, paste0(auto[["table"]][i], "\t",
                                       paste(got, collapse = "; ")))
        }
    }

    message(label, ": unioned ", nrow(auto), " automated row(s) -- ",
            length(add), " new table(s), ", nfill,
            " existing row(s) topped up, ",
            sum(hit) - nfill, " already complete")
    if (ncleared) {
        message(label, ": cleared `DOI (for paper)` on ", ncleared,
                " row(s) where it held the deposit DOI now carried by ",
                "`DOI (for data)` (#1690). The sheet is unchanged; see the ",
                "provenance file for the list.")
    }

    list(dict = dict, provenance = dict_provenance_frame(filled))
}

dict_provenance_frame <- function(filled = character(0)) {
    if (!length(filled)) {
        return(data.frame(table = character(0), columns = character(0),
                          contributor = character(0), generated = character(0),
                          stringsAsFactors = FALSE))
    }
    parts <- strsplit(filled, "\t", fixed = TRUE)
    data.frame(table       = vapply(parts, `[`, character(1), 1L),
               columns     = vapply(parts, `[`, character(1), 2L),
               contributor = DICT_AUTO_CONTRIBUTOR,
               generated   = format(Sys.Date(), "%Y-%m-%d"),
               stringsAsFactors = FALSE)
}

##Sidecar rather than a column in biblio.csv: the published schema is read by
##Rpkg, Python-pkg and the site, and none of them should have to change to gain
##an audit trail. Committed, unlike 03_tags.R's -- see .gitignore.
write_dict_provenance <- function(prov, out) {
    readr::write_csv(prov, out)
    message("  wrote ", nrow(prov), " provenance row(s) to ", out)
    invisible(NULL)
}

##The custom licence terms, under one stable name, whatever the sheet calls
##them. Tolerant across all four dictionary layouts by design: core carries two
##`Custom License` columns and the second is the operative one (it follows
##`Derived License`, and is what IRW redistributes under); comps/nominal/simsyn
##carry one. Returns NA for a sheet with none rather than failing -- an absent
##licence-terms column is not an error, it is a sheet that has never needed one.
##
##Why this exists: 238 Public tables publish `Derived_License = "Custom"` -- the
##bare word, with no terms attached anywhere a user can reach. The terms were
##added to biblio.csv once by metadata/hotfixes/fix-licenses.R (Rpkg#93, retired
##2026-09-06), and the next 02_biblio.R run erased them by rewriting from a
##fixed column list.
##Carrying the column here is what stops that cycle.
dict_terms_column <- function(dict) {
    nm <- names(dict)
    if ("Custom License (derived)" %in% nm) return(as.character(dict[["Custom License (derived)"]]))
    cust <- which(dict_base_names(nm) == "Custom License")
    if (length(cust) >= 2L) return(as.character(dict[[nm[cust[2]]]]))
    if (length(cust) == 1L) return(as.character(dict[[nm[cust[1]]]]))
    rep(NA_character_, nrow(dict))
}

##Attach `DOI__for_data_` to every biblio row, and retire the deposit DOI from
##`DOI__for_paper_` where the dictionary has split the two (#1690).
##
##Across ALL rows, for the same reason apply_custom_license_terms() is: 02
##builds biblio.csv incrementally and only `new_data_rows` reads the dictionary,
##so a change to a long-published row reaches nobody otherwise. Every one of the
##979 rows this is for was published months ago.
##
##The clear is conditional on three things agreeing, not one: the dictionary
##must now hold the deposit DOI in `DOI (for data)`, it must have no paper DOI
##for that row, and the value biblio is carrying must BE that deposit DOI. A row
##whose paper DOI is something else keeps it.
apply_data_doi <- function(biblio, dict, label = "core") {
    if (!"DOI (for data)" %in% names(dict)) {
        biblio$DOI__for_data_ <- NA_character_
        return(biblio)
    }
    src <- data.frame(.key  = dict_key(dict$table),
                      ddoi  = as.character(dict[["DOI (for data)"]]),
                      pdoi  = as.character(dict[["DOI (for paper)"]]),
                      stringsAsFactors = FALSE)
    src <- src[!duplicated(src$.key), ]
    i <- match(dict_key(biblio$table), src$.key)

    biblio$DOI__for_data_ <- ifelse(is.na(i) | dict_blank(src$ddoi[i]),
                                    NA_character_, src$ddoi[i])

    clear <- !is.na(i) &
             !dict_blank(src$ddoi[i]) &
             dict_blank(src$pdoi[i]) &
             !dict_blank(biblio$DOI__for_paper_) &
             dict_norm_doi(biblio$DOI__for_paper_) == dict_norm_doi(src$ddoi[i])
    clear[is.na(clear)] <- FALSE
    biblio$DOI__for_paper_[clear] <- NA_character_

    message(label, ": ", sum(!is.na(biblio$DOI__for_data_)),
            " row(s) carry a data DOI; cleared `DOI__for_paper_` on ",
            sum(clear), " row(s) that were citing the deposit as the paper")
    biblio
}

##Attach the custom licence terms to every biblio row.
##
##Extracted from 02_biblio.R so it can be replayed offline against the real
##biblio.csv without a Redivis read or a BibTeX call -- see
##tests/manual_dict_test.sh, which is how this gets exercised on production data
##before a batch goes anywhere near the sheet.
##
##Joined across ALL rows on purpose. The tables carrying custom terms are
##long-published, so they never appear in `new_data_rows`, and a carry-through
##on new rows alone would deliver the terms to nobody.
apply_custom_license_terms <- function(biblio, dict, label = "core") {
    terms <- data.frame(.key = dict_key(dict$table),
                        Custom_License_Terms = dict_terms_column(dict),
                        stringsAsFactors = FALSE)
    terms <- terms[!duplicated(terms$.key) & !dict_blank(terms$Custom_License_Terms), ]
    biblio$Custom_License_Terms <- terms$Custom_License_Terms[match(dict_key(biblio$table),
                                                                   terms$.key)]
    message(label, ": ", sum(!is.na(biblio$Custom_License_Terms)),
            " row(s) carry custom licence terms")
    biblio
}

##---------------------------------------------------------------------------
##Refresh published biblio rows from the dictionary (issue #2001).
##
##getrows() builds `new_data_rows` as the dictionary rows ABSENT from the live
##Redivis biblio table (or lacking BibTeX) and binds them on. A dictionary row
##that already has a biblio row is never re-read, so a correction typed into the
##sheet for an already-published table reaches nobody. Measured 2026-09-05: 226
##of 4,261 rows disagree on at least one of the five columns below -- 62 pure
##fills, 163 genuine conflicts.
##
##The rule:
##
##  FILL BLANKS, PREFER THE DICTIONARY ON CONFLICT, AND NEVER BLANK A BIBLIO
##  VALUE FROM AN EMPTY DICTIONARY CELL.
##
##That last clause is not hypothetical -- `cdm_timss03` holds a paper DOI in
##biblio that the dictionary lacks -- and without it this repeats the pattern
##that removed provenance for four live su_2024_* tables.
##
##BibTeX is deliberately NOT refreshed: seed_from_local() caches it because
##regenerating costs a DOI fetch plus a Claude call per row, and the model does
##not return byte-identical BibTeX twice.
##
##Note on a truncated sheet: this cannot damage biblio. A short read yields
##FEWER matches, and a blank dictionary cell is skipped rather than written, so
##the failure mode is "no change", not "wrong change". That is why there is no
##minimum-rows oracle here, unlike drop_dead_dict_rows().

##biblio's column name -> the dictionary's, most-preferred spelling first. The
##four dictionary sheets have drifted on the licence column: core spells it
##`Derived License`, comps/nom/sim `Derived_License` (confirmed 2026-08-02).
BIBLIO_REFRESH_COLS <- list(
    Description     = "Description",
    Reference_x     = "Reference",
    DOI__for_paper_ = "DOI (for paper)",
    URL__for_data_  = "URL (for data)",
    Derived_License = c("Derived License", "Derived_License")
)

##Comparison normalisation, per column. Two values that differ only here are
##treated as equal, so the first run rewrites 226 rows rather than 4,261.
##
##  DOI      -- dict_norm_doi(), the repo's one definition, pinned to
##              doi_hygiene.py by a parity test. A resolver prefix is not a
##              different DOI.
##  licence  -- "CC BY 4.0" / "cc by 4.0" is a spelling difference, not a
##              relicensing.
##  the rest -- whitespace only. Case IS significant in a Description; an
##              instrument name that changed case changed.
biblio_norm <- function(x, col) {
    if (identical(col, "DOI__for_paper_")) return(dict_norm_doi(x))
    x <- gsub("\\s+", " ", trimws(as.character(x)))
    if (identical(col, "Derived_License")) x <- tolower(x)
    x
}

##Strip the .csv some dictionary rows still carry, so the key matches biblio's
##(getrows() strips it from biblio before writing).
biblio_key <- function(x) sub("\\.csv$", "", dict_key(x))

##The dictionary column backing one biblio column, or NULL when the sheet has
##none. Returning NULL rather than failing: comps/nom/sim are independently
##maintained and a sheet that has never had a column is not an error.
dict_source_column <- function(dict, candidates) {
    for (cl in candidates) if (cl %in% names(dict)) return(as.character(dict[[cl]]))
    NULL
}

refresh_biblio_from_dict <- function(biblio, dict, label = "core", log.file = NULL) {
    key <- biblio_key(dict$table)
    keep <- !dict_blank(key) & !duplicated(key)
    if (sum(!keep) > 0) {
        message(label, ": ", sum(!keep), " duplicate/nameless dictionary row(s) ",
                "ignored for the refresh (first occurrence wins)")
    }
    dict <- dict[keep, , drop = FALSE]
    key  <- key[keep]

    idx <- match(biblio_key(biblio$table), key)

    changes <- list()
    for (bcol in names(BIBLIO_REFRESH_COLS)) {
        if (!bcol %in% names(biblio)) next
        dvals <- dict_source_column(dict, BIBLIO_REFRESH_COLS[[bcol]])
        if (is.null(dvals)) next

        new <- dvals[idx]                      ##NA where the dictionary has no row
        old <- as.character(biblio[[bcol]])
        ##A blank dictionary cell never wins -- including for a table the
        ##dictionary does not mention at all, which is the same case here.
        move <- !dict_blank(new) &
                (dict_blank(old) | biblio_norm(old, bcol) != biblio_norm(new, bcol))
        move[is.na(move)] <- FALSE
        if (!any(move)) next

        changes[[bcol]] <- data.frame(
            table  = biblio$table[move],
            column = bcol,
            kind   = ifelse(dict_blank(old[move]), "fill", "conflict"),
            was    = old[move],
            now    = new[move],
            stringsAsFactors = FALSE)
        biblio[[bcol]][move] <- new[move]
    }

    log <- if (length(changes)) do.call(rbind, changes) else
        data.frame(table = character(0), column = character(0), kind = character(0),
                   was = character(0), now = character(0), stringsAsFactors = FALSE)
    log <- log[order(log$table, log$column), , drop = FALSE]
    message(label, ": refreshed ", nrow(log), " cell(s) across ",
            length(unique(log$table)), " table(s) from the dictionary (",
            sum(log$kind == "fill"), " fill, ", sum(log$kind == "conflict"),
            " conflict)")
    ##Always written, even when empty -- "nothing drifted" is a useful statement,
    ##and it makes the first run reviewable as a list rather than only as a
    ##226-row diff of biblio.csv.
    if (!is.null(log.file)) {
        readr::write_csv(log, log.file)
        message("  wrote ", nrow(log), " refresh row(s) to ", log.file)
    }
    list(biblio = biblio, log = log)
}

##---------------------------------------------------------------------------
##Description corrections (#1898, #1925, #1929, #1951, #1972).
##
##THE PROBLEM THIS SOLVES. union_dict() above fills only the cells a human left
##blank -- "a human cell wins the cell it occupies". That is right for a sparse
##row being topped up, and it means a dictionary Description that is *wrong* has
##no route to a fix at all: dictionary_auto.csv cannot reach an occupied cell,
##and refresh_biblio_from_dict() re-asserts the sheet's value onto every biblio
##row on every run. Five tables were shipping the name of an instrument they do
##not contain.
##
##Ben will not hand-edit the sheet to land a fix (#1690, 2026-09-06), so this is
##the same shape as the `DOI (for paper)` clear in union_dict() and as
##tag_normalize.R: the correction is applied to the EXPORT and the sheet is left
##alone. This table is the audit trail -- each entry carries the issue that
##established it and the evidence in one line, which is more reviewable than a
##provenance CSV row.
##
##THE GUARD. `superseded` must match the sheet's current Description exactly
##(whitespace-normalised). This is deliberately narrower than "the Description
##looks wrong":
##
##  * it can only ever replace a value we have demonstrably read and judged, and
##  * it DISARMS ITSELF. The moment someone corrects the sheet cell by hand, the
##    strings stop matching, the override stops firing, and the human's text
##    wins -- which is the rule this is an exception to, restored automatically.
##
##A non-matching entry is a warning, not a silent no-op and not a stopped run:
##stale entries must be visible (they mean "delete me"), but a weekly pipeline
##should not fail because someone improved a sentence in the sheet.
DESCRIPTION_OVERRIDES <- list(
    list(
        table      = "cdm_timss07",
        issue      = "#1898",
        superseded = "Subsample of TIMSS items from Australia with Q matrix",
        corrected  = paste("Subsample of TIMSS 2007 grade 4 mathematics items from Austria",
                           "(booklets 4 and 5) with Q matrix"),
        ##CDM's own docs for data.timss07.G4.lee: "a sample of 698 Austrian
        ##students ... booklets 4 and 5". The live table is 25 items over n=698,
        ##which is the 14 block-M04 plus 11 block-M05 items exactly. Not
        ##cosmetic: the booklets were the German translation, so "Australia"
        ##also implies the wrong administered language. cdm_timss11 already says
        ##Austria and needs nothing.
        why = "CDM documents the Austrian sample; 25 items over n=698 matches booklets 4+5"
    ),
    list(
        table      = "COACH_Chen_2022_CSQ",
        issue      = "#1925",
        superseded = "Client Satisfaction Questionnaire 8-item",
        corrected  = paste("Consultation Satisfaction Questionnaire short form (CSQ-9),",
                           "items 1-8, 5-point agree-disagree"),
        ##Larsen's CSQ-8 is a 4-point service-satisfaction scale. The live table
        ##is 8 items over 5 categories and the deposit's codebook gives
        ##doctor-consultation statements matching Baker's CSQ-9 items 1-8 word
        ##for word, item 9 not administered. The study's own codebook also
        ##mislabels the block, so the sheet is repeating an upstream error.
        why = "8 items x 5 categories; Larsen's CSQ-8 has no 5-point form"
    ),
    list(
        table      = "conner_2017_vitality",
        issue      = "#1929",
        superseded = "Subjective Vitality Scale (4 items, 0-100 continuous), baseline/follow-up, N=171.",
        corrected  = paste("SF-36 Vitality (energy/fatigue) subscale, 4 items scored 0-100",
                           "in steps of 20 (6 ordinal levels), baseline/follow-up, N=171.",
                           "The 'worn out' and 'tired' items are stored already reverse-scored."),
        ##The superseded text is internally inconsistent on its own terms: the
        ##SVS is a 6- or 7-item 1-7 Likert scale, so "4 items" cannot be it. The
        ##study's S1 Dataset labels these vital1-4 as SF-36 Vitality. metadata
        ##independently gives 4 items over 6 discrete levels, which is SF-36
        ##scoring (0/20/40/60/80/100) and also makes "0-100 continuous" wrong.
        ##wolf_2017_study1_vitality (6 items) is the corpus's genuine SVS.
        why = "4 items x 6 ordinal levels = SF-36 scoring; the SVS is 6-7 items on 1-7"
    ),
    list(
        table      = "cordova2019_clinical_edu_environment",
        issue      = "#1951",
        superseded = "Perception of clinical educational environment by physiotherapy interns (DREEM-based, Chile)",
        corrected  = paste("Perception of clinical educational environment by physiotherapy",
                           "interns (PHEEM, 40 items, Chile)"),
        ##Different instruments by different authors: DREEM is 50 items
        ##(undergraduate learning environment), PHEEM is 40 (postgraduate /
        ##clinical). The companion paper's Methods says PHEEM and reproduces the
        ##40 items; the live table is item_01..item_40. The corpus's real DREEM,
        ##agarwal_2023_dreem, has 50 -- so the mislabel made this look like a
        ##sibling of a table measuring something else.
        why = "40 items = PHEEM; the corpus's genuine DREEM (agarwal_2023_dreem) has 50"
    ),
    list(
        table      = "evpromisi_stone_2021_cdiag",
        issue      = "#1972",
        superseded = "PROMIS fatigue",
        corrected  = paste("Study's own 12-item chronic-diagnosis checklist (3 response levels).",
                           "Not a PROMIS instrument, despite the evpromisi_ prefix."),
        ##Corroborated independently of the codebook, which is the thing under
        ##suspicion: every PROMIS fatigue short form is scored on 5 points and
        ##this table has 3 response levels. Its four evpromisi_ siblings ARE
        ##PROMIS (anxiety 7 items, depression 8, pain intensity 6, global 10 over
        ##11 levels) and are correctly described, so this is one row not a
        ##family. Fixing it also fixes the bad `promis` collection membership,
        ##which comes from rule:cname:promis -- the construct name derived from
        ##this Description -- and so self-corrects on the next 10_collections.R.
        why = "3 response levels; every PROMIS fatigue short form is 5-point"
    )
)

##Whitespace-normalised comparison. The sheet stores stray double spaces and
##trailing blanks that carry no meaning, and an override should not miss because
##of one.
desc_norm <- function(x) {
    x <- trimws(as.character(ifelse(is.na(x), "", x)))
    gsub("[[:space:]]+", " ", x)
}

##Apply the corrections to biblio's Description, by exact match on `superseded`.
##
##Runs on EVERY row rather than only new ones, and must run AFTER
##refresh_biblio_from_dict() -- that is what re-asserts the sheet's value, so an
##override placed before it would be overwritten on every run.
apply_description_overrides <- function(biblio, label = "core",
                                        overrides = DESCRIPTION_OVERRIDES) {
    if (!length(overrides) || !"Description" %in% names(biblio)) return(biblio)
    applied <- character(0)
    stale   <- character(0)
    for (ov in overrides) {
        row <- which(dict_key(biblio$table) == dict_key(ov$table))
        if (!length(row)) next                    ##not in this source's biblio
        row <- row[1]
        if (identical(desc_norm(biblio$Description[row]), desc_norm(ov$superseded))) {
            biblio$Description[row] <- ov$corrected
            applied <- c(applied, ov$table)
        } else if (identical(desc_norm(biblio$Description[row]), desc_norm(ov$corrected))) {
            ##Already correct in the sheet: the human got there first. The entry
            ##has done its job and should be deleted, but this is not a problem.
            stale <- c(stale, paste0(ov$table, " (sheet now matches the correction)"))
        } else {
            stale <- c(stale, paste0(ov$table, " (", ov$issue, ": sheet says something else)"))
        }
    }
    message(label, ": applied ", length(applied), " of ", length(overrides),
            " Description override(s)")
    if (length(stale)) {
        warning(label, ": ", length(stale), " Description override(s) did not match and were ",
                "skipped -- delete the entry in DESCRIPTION_OVERRIDES if the sheet is now ",
                "right: ", paste(stale, collapse = "; "), call. = FALSE)
    }
    biblio
}

##---------------------------------------------------------------------------
##Second-source attribution (#1694).
##
##A table can be built from more than one deposit, and biblio carries exactly
##one licence and one reference. `project_kids_*` is the case that surfaced it:
##all 23 tables take every `resp` from the item-level deposit (CC BY 4.0,
##10.33009/ldbase.1620837890.bcf8), and take two covariates -- `treat` and
##`cov_project` -- from PK_FullData.csv in a SECOND LDbase deposit released
##under ODC-By (10.33009/ldbase.1620844399.85a0). See data/project_kids_items.R.
##
##Ruling (Ben, 2026-09-07): record both, change neither. ODC-By and CC BY 4.0
##are both attribution-only -- neither is share-alike, NC or ND -- so there is
##no licence conflict to resolve and `Derived_License` stays CC BY 4.0, which is
##what governs the response data. What was wrong is that the record named one
##source when the tables draw on two, so a reuser attributing from biblio alone
##would under-attribute.
##
##This fills `Custom_License_Terms`, which 02_biblio.R already carries for every
##row, rather than overriding anything: the cell is blank on all 23. It is kept
##separate from DESCRIPTION_OVERRIDES because it is not a correction -- nothing
##here supersedes a value a human wrote -- and so it needs no exact-match guard.
##A non-blank cell is left alone, on the same "a human cell wins" rule.
LICENSE_ATTRIBUTION <- list(
    list(
        tables = "^project_kids_",
        issue  = "#1694",
        terms  = paste(
            "Response data: Project KIDS Item level Data (LDbase,",
            "doi:10.33009/ldbase.1620837890.bcf8), CC BY 4.0.",
            "The `treat` and `cov_project` columns are derived from",
            "PK_FullData.csv in Project KIDS Total Scores data (LDbase,",
            "doi:10.33009/ldbase.1620844399.85a0), which is released under",
            "ODC-By 1.0 and must be attributed separately.")
    )
)

##Attach second-source attribution where a table has more than one deposit.
##Runs after apply_custom_license_terms(), which sets the column from the sheet.
apply_license_attribution <- function(biblio, label = "core",
                                      spec = LICENSE_ATTRIBUTION) {
    if (!length(spec)) return(biblio)
    if (!"Custom_License_Terms" %in% names(biblio)) {
        biblio$Custom_License_Terms <- NA_character_
    }
    n <- 0L
    for (s in spec) {
        hit <- grepl(s$tables, biblio$table) & dict_blank(biblio$Custom_License_Terms)
        hit[is.na(hit)] <- FALSE
        biblio$Custom_License_Terms[hit] <- s$terms
        n <- n + sum(hit)
    }
    message(label, ": attached second-source attribution to ", n, " row(s)")
    biblio
}

##---------------------------------------------------------------------------
##Licence of record for the OSF deposits that state none.
##
##115 published tables across 23 OSF projects carry a blank `Derived_License`.
##OSF makes setting a licence optional and defaults to none, so a blank here
##means the DEPOSIT is silent rather than that nobody checked -- confirmed
##directly for osf.io/3xvys, which the OSF API reports as `license: NONE SET`.
##
##RULING (Ben, 2026-09-07): these reached IRW under emailed permission from the
##depositors; record them as such. That is HIS ruling written down, not
##something this repo established -- no correspondence is cited or held here.
##The value belongs in the Data Dictionary sheet, and this is a stopgap so that
##users stop seeing a blank licence in the meantime.
##
##KEYED ON THE OSF PROJECT, not the 115 table names. A table added later from
##the same deposit arrived under the same permission, so it should inherit it;
##115 names would also go stale the moment one is renamed.
##
##BLANK-ONLY. A licence recorded in the sheet always wins, so this can never
##overwrite a real one -- which matters for osf.io/3xvys specifically, where
###2058 asks the depositor to set a public licence. If that lands, the sheet
##supersedes this automatically and the entry can be deleted.
OSF_PERMISSION_PROJECTS <- c(
    "qtqpb",  # 19  eammi_grahe_2018_*
    "75crd",  # 15  parentalempathy_gonzalez_2021_*
    "4fdw9",  # 10  darkfactorfrench_pischel_2026_*
    "rjbx2",  #  9  hachenberger_2025_*
    "3w6ap",  #  7  kazarovytska_2026_*
    "t3a9r",  #  7  transyouth_leshin_2026_*
    "zevcs",  #  7  personalitychange_kramer_2025_*
    "3xvys",  #  6  parenting_anunciacao_2025_*  -- see #2058
    "6nm2s",  #  6  thirdpartypunishmentunfairsharing_mcauliffe_*
    "rf9k8",  #  5  talaifar_2025_*
    "69nwe",  #  4  smpi_lorenzoluaces_2020_*
    "g8dvj",  #  4  morgan_2026_music_personality_*
    "c6rqy",  #  2  christensen_2018_*
    "gvx7s",  #  2  itemrandom_buchanan
    "kqxd5",  #  2  west_2021_aggnet_*
    "snmqt",  #  2  mclaughlin_samuel_2025_*
    "umdg3",  #  2  haehner_2026_personality_subsaharan_*
    "9cm75",  #  1  steinberg_2023_mentalizing_momentary
    "frwq4",  #  1  kay_2025_antonyms
    "mbywd",  #  1  west_2022_psychnet_pclsv
    "thdf5",  #  1  vollbracht_et_al_2026_ambulatory_assessment
    "twgcu",  #  1  schoen_2019_to_2022_mkt
    "zajk6"   #  1  kalimahnorms_alzahrani
)
OSF_PERMISSION_VALUE <- "Permission via Email"

apply_osf_permission <- function(biblio, label = "core",
                                 projects = OSF_PERMISSION_PROJECTS,
                                 value = OSF_PERMISSION_VALUE) {
    if (!length(projects) ||
        !all(c("URL__for_data_", "Derived_License") %in% names(biblio))) {
        return(biblio)
    }
    ##`\\b` would not anchor here: OSF ids are alphanumeric, so "qtqpb" could
    ##match a longer id starting with it. Require the id to end the path
    ##segment instead.
    pat <- paste0("osf\\.io/(", paste(projects, collapse = "|"), ")(/|$|[?#])")
    hit <- grepl(pat, biblio$URL__for_data_) & dict_blank(biblio$Derived_License)
    hit[is.na(hit)] <- FALSE
    biblio$Derived_License[hit] <- value
    message(label, ": set `", value, "` on ", sum(hit),
            " OSF row(s) that had no licence")
    biblio
}

##---------------------------------------------------------------------------
##The shape of a table name (#2079).
##
##Nothing in the dictionary path ever asserted that `table` holds a table NAME.
##dict_key() is tolower(trimws()), which is happy to key a row on a sentence, so
##a citation string typed into the wrong column travelled from the sheet to
##dictionary_auto.csv to biblio.csv on main and asserted a licence and a DOI for
##a table that does not exist. One cell, one phantom biblio row, no error
##anywhere along the way.
##
##The pattern is the repo's existing convention for a machine-readable name (cf.
##`_TERM_OK_RE` in automated_finding/irw_lint_covariates.py), widened to the
##cases table names actually use: 307 names in this corpus are not all-lowercase,
##and names carry `.`, `-` and a trailing `.csv` in some dictionary rows. Checked
##against all 4,238 rows of metadata.csv and all 4,273 of biblio.csv on
##2026-09-08: zero false positives, one true positive.
DICT_NAME_RE <- "^[A-Za-z0-9][A-Za-z0-9._-]{1,80}$"

##Blank is NOT unshaped: a blank key is a different defect with its own handling
##(refresh_biblio_from_dict() already reports duplicate/nameless rows), and
##folding the two would make this message lie about what is wrong with the cell.
dict_name_ok <- function(x) {
    x <- trimws(as.character(x))
    dict_blank(x) | grepl(DICT_NAME_RE, x)
}

##Drop rows whose `table` cell is not a name, and SAY SO. Reports rather than
##fails on purpose: the sheet is the human surface, and a whole metadata run
##must not stop because someone typed in the wrong column. Per #1732 this must
##not write to the sheet either -- reject at export, name the cell in the log,
##and leave a human to clean it.
##
##Applied to both the dictionary and biblio, because they are two doors on the
##same room: the dictionary gate stops the row being created, and the biblio gate
##removes the one already sitting on main. The second is not redundant -- biblio
##is read back from Redivis at the top of every run, so a row that got in once
##survives every later run unless something takes it out.
drop_unshaped_dict_rows <- function(df, label, what = "dictionary") {
    if (is.null(df) || !nrow(df) || !"table" %in% names(df)) return(df)
    keep <- dict_name_ok(df[["table"]])
    keep[is.na(keep)] <- TRUE
    if (any(!keep)) {
        message(label, ": dropping ", sum(!keep), " ", what, " row(s) whose ",
                "`table` cell is not a table name (#2079) -- fix the cell at ",
                "the source; nothing here edits the sheet:")
        for (v in df[["table"]][!keep]) {
            message("    ", substr(gsub("\\s+", " ", v), 1L, 120L))
        }
    }
    df[keep, , drop = FALSE]
}
