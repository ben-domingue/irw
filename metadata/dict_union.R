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
