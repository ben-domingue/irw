##Manual harness for the dictionary write path (#1732), run against PRODUCTION
##data. Run it from the metadata directory:
##
##    Rscript tests/manual_dict_test.R tier-a
##    Rscript tests/manual_dict_test.R tier-b
##
##This is NOT tests/test_dict_union.R. That one runs in CI on fixtures and must
##stay offline and deterministic. This one reads the live dictionary sheet and
##the committed biblio.csv, because the failures worth catching before a real
##batch are the ones fixtures cannot show: 4,380 rows, the duplicate
##`Custom License` names, and the real mix of NA / "" / "NA" that raters type.
##
##Neither tier writes anything outside tempdir(). Nothing here touches Redivis,
##Anthropic, the Google Sheet, or the tracked dictionary_auto.csv -- it stages
##through the real writer with IRW_DICT_AUTO_PATH pointed at a scratch file, so
##the quoting and the refusals are the production ones.
##
##  tier-a         the merge rule against the live sheet
##  tier-b         the whole export path replayed on the real biblio.csv
##  tier-c-replay  a real past batch re-run through the new path, asserting it
##                 would have produced byte-identical rows to the human paste
##
##tier-c-replay is the cheap half of Tier C. It takes a batch of rows a human
##actually pasted into the sheet, removes them from a COPY of the sheet, stages
##them through stage_dict_row.py, unions them back, and asserts the result is
##byte-identical to what is live. That is the whole question -- would the new
##path have produced the same dictionary? -- answered against real history,
##offline, with no dataset to process and nothing to upload.
##
##It cannot test BibTeX generation on a genuinely new row. Only a real batch
##does that, and it is written up in the pull request.

suppressMessages(library(readr))
source("dict_union.R")

MODE <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(MODE) || !MODE %in% c("tier-a", "tier-b", "tier-c-replay")) {
    stop("usage: Rscript tests/manual_dict_test.R [tier-a|tier-b|tier-c-replay]")
}
##tier-c-replay takes the batch date as a second argument, e.g. "8/27/2026".
##Defaults to the largest automated batch in the sheet.
BATCH_DATE <- commandArgs(trailingOnly = TRUE)[2]

DICT_URL <- paste0("https://docs.google.com/spreadsheets/d/",
                   "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s",
                   "/export?format=csv&gid=1337607315")
STAGER <- "../automated_finding/stage_dict_row.py"

##Element-wise equality that treats every flavour of blank as equal, so a
##round trip through "" / NA / "NA" is not reported as a change.
identical_chr <- function(a, b) {
    a[dict_blank(a)] <- ""; b[dict_blank(b)] <- ""
    a == b
}

failures <- 0L
check <- function(cond, what) {
    if (isTRUE(cond)) cat("  ok   -", what, "\n")
    else { cat("  FAIL -", what, "\n"); failures <<- failures + 1L }
}

##Stage one row through the real writer, into a scratch file.
stage <- function(path, json) {
    out <- system2(c("python3"), c(STAGER),
                   env = paste0("IRW_DICT_AUTO_PATH=", path),
                   input = json, stdout = TRUE, stderr = TRUE)
    status <- attr(out, "status")
    if (!is.null(status) && status != 0L) stop(paste(out, collapse = "\n"))
    invisible(out)
}

cat("reading the live dictionary sheet ...\n")
dict <- suppressWarnings(read_csv(DICT_URL,
                                  col_types = cols(.default = col_character()),
                                  progress = FALSE))
cat("  ", nrow(dict), "rows,", ncol(dict), "columns\n")

##A real table whose dictionary row is present but missing one published field.
##Chosen from the sheet rather than hardcoded: the sheet is edited daily, and a
##hardcoded subject would quietly stop being sparse.
pick_sparse_subject <- function(dict, column) {
    live <- read_csv("metadata.csv", show_col_types = FALSE, progress = FALSE)
    ok <- dict_key(dict$table) %in% dict_key(live$table) &
          trimws(as.character(dict[["Public Reshare?"]])) == "Public" &
          dict_blank(dict[[column]]) &
          !dict_blank(dict[["Description"]])
    if (!any(ok)) stop("no sparse subject found for ", column)
    dict$table[which(ok)[1]]
}

##--------------------------------------------------------------- tier A ------
if (MODE == "tier-a") {
    cat("\nTIER A -- the merge rule against the live sheet\n\n")

    subject <- pick_sparse_subject(dict, "DOI (for paper)")
    cat("  sparse subject:", subject, "(blank DOI, live, Public)\n")
    before <- dict[dict_key(dict$table) == dict_key(subject), ][1, ]

    scratch <- tempfile(fileext = ".csv")
    on.exit(unlink(scratch), add = TRUE)
    stage(scratch, sprintf(paste0('{"table": "%s", "public_reshare": "Public",',
                                  ' "derived_license": "CC BY 4.0",',
                                  ' "doi": "10.0000/probe-tier-a",',
                                  ' "description": "MACHINE VALUE, must lose"}'),
                           subject))
    stage(scratch, paste0('{"table": "probe_new_2026", "public_reshare": "Public",',
                          ' "derived_license": "CC BY 4.0",',
                          ' "description": "A comma, a \\"quote\\", and prose."}'))

    auto <- read_dict_auto(scratch, "core")
    check(!is.null(auto) && nrow(auto) == 2L,
          "the real writer's output reads back through the real reader")

    res <- suppressMessages(union_dict(dict, auto, "core"))
    m   <- res$dict
    row <- m[dict_key(m$table) == dict_key(subject), ][1, ]

    check(identical(as.character(row[["Description"]]),
                    as.character(before[["Description"]])),
          "the human's Description survives untouched")
    check(identical(as.character(row[["DOI (for paper)"]]), "10.0000/probe-tier-a"),
          "the human's blank DOI is filled")
    check(nrow(m) == nrow(dict) + 1L,
          "one new table appended, the sparse one merged in place")

    newrow <- m[dict_key(m$table) == "probe_new_2026", ][1, ]
    check(grepl("a \"quote\"", as.character(newrow[["Description"]]), fixed = TRUE),
          "a comma and a quote survive the write/read round trip")

    prov <- res$provenance
    subj_prov <- prov[dict_key(prov$table) == dict_key(subject), ]
    check(nrow(subj_prov) == 1L &&
          grepl("DOI (for paper)", subj_prov$columns[1], fixed = TRUE) &&
          !grepl("Description", subj_prov$columns[1], fixed = TRUE),
          "provenance credits the machine with the DOI and not the Description")
}

##--------------------------------------------------------------- tier B ------
if (MODE == "tier-b") {
    cat("\nTIER B -- the export path replayed on the real biblio.csv\n\n")

    biblio <- read_csv("biblio.csv", show_col_types = FALSE, progress = FALSE)
    cat("  biblio.csv:", nrow(biblio), "rows,", ncol(biblio), "columns\n")

    ##What 02_biblio.R does to rows that already exist. The Redivis read and the
    ##BibTeX generation are the parts this cannot replay -- they only ever touch
    ##NEW rows, which Tier C covers with real data.
    out <- suppressMessages(apply_custom_license_terms(biblio, dict, "core"))
    n_terms <- sum(!is.na(out$Custom_License_Terms))
    cat("  rows gaining custom licence terms:", n_terms, "\n")
    check(n_terms > 0L, "custom licence terms reach biblio at all")
    check(nrow(out) == nrow(biblio), "the terms join adds no rows and drops none")

    custom <- out$Derived_License == "Custom" & !is.na(out$Derived_License)
    cat("  tables publishing Derived_License = \"Custom\":", sum(custom),
        "of which now carry terms:", sum(custom & !is.na(out$Custom_License_Terms)), "\n")

    ##Every other published column must be byte-identical. This is the check
    ##that says the change is additive.
    shared <- setdiff(intersect(names(biblio), names(out)), "Custom_License_Terms")
    same <- vapply(shared, function(cl) identical(biblio[[cl]], out[[cl]]), logical(1))
    check(all(same), paste0("all ", length(shared),
                            " pre-existing columns are unchanged"))
    if (!all(same)) cat("     changed:", paste(shared[!same], collapse = ", "), "\n")

    ##The held-row window: a staged row for a table that is not published yet.
    scratch <- tempfile(fileext = ".csv"); pend <- tempfile(fileext = ".csv")
    on.exit(unlink(c(scratch, pend)), add = TRUE)
    stage(scratch, paste0('{"table": "not_yet_published_2026",',
                          ' "public_reshare": "Public",',
                          ' "derived_license": "CC BY 4.0", "description": "draft"}'))
    auto <- read_dict_auto(scratch, "core")
    kept <- suppressMessages(drop_dead_dict_rows(auto, "metadata.csv", "core",
                                                 pending.file = pend))
    held <- read_csv(pend, col_types = cols(.default = col_character()))
    check(nrow(kept) == 0L, "a row for an unpublished table does not reach biblio")
    check(nrow(held) == 1L && held$table[1] == "not_yet_published_2026",
          "it is written to biblio_pending.csv instead of vanishing")

    cat("\n  A real batch sits in that held state between the table upload and\n",
        " the publish click. biblio_pending.csv is how you see it.\n", sep = "")
}

##--------------------------------------------------- tier C (replay) --------
if (MODE == "tier-c-replay") {
    cat("\nTIER C (replay) -- a real batch re-run through the new path\n\n")

    contrib <- trimws(as.character(dict[["Contributor"]]))
    dates   <- trimws(as.character(dict[["Date"]]))
    if (is.na(BATCH_DATE)) {
        tab <- sort(table(dates[contrib == DICT_AUTO_CONTRIBUTOR]), decreasing = TRUE)
        BATCH_DATE <- names(tab)[1]
    }
    sel <- contrib == DICT_AUTO_CONTRIBUTOR & dates == BATCH_DATE
    sel[is.na(sel)] <- FALSE
    cat("  batch:", BATCH_DATE, "--", sum(sel), "rows pasted by hand\n")
    if (sum(sel) == 0L) stop("no automated rows dated ", BATCH_DATE)

    batch <- dict[sel, , drop = FALSE]
    map   <- resolve_dict_cols(dict, "core")

    ##Stage each row through the real writer, from the row's own values. This is
    ##the batch as it would have been staged had stage_dict_row.py existed.
    scratch <- tempfile(fileext = ".csv")
    on.exit(unlink(scratch), add = TRUE)
    payload_keys <- c(description = "Description", url = "URL (for data)",
                      reference = "Reference", doi = "DOI (for paper)",
                      original_license = "Original License",
                      custom_license_source = "Custom License (source)",
                      public_reshare = "Public Reshare?",
                      derived_license = "Derived License",
                      custom_license_derived = "Custom License (derived)",
                      notes = "Notes", date = "Date")
    esc <- function(x) gsub('"', '\\\\"', gsub("\\\\", "\\\\\\\\", x), fixed = FALSE)
    for (i in seq_len(nrow(batch))) {
        bits <- paste0('"table": "', esc(as.character(batch[[map[["table"]]]][i])), '"')
        for (k in names(payload_keys)) {
            v <- as.character(batch[[map[[payload_keys[[k]]]]]][i])
            if (dict_blank(v)) next
            bits <- c(bits, paste0('"', k, '": "', esc(v), '"'))
        }
        stage(scratch, paste0("{", paste(bits, collapse = ", "), "}"))
    }
    auto <- read_dict_auto(scratch, "core")
    check(!is.null(auto) && nrow(auto) == nrow(batch),
          paste0("all ", nrow(batch), " rows survive the real writer and reader"))

    ##The sheet as it was BEFORE the paste.
    before <- dict[!sel, , drop = FALSE]
    res <- suppressMessages(union_dict(before, auto, "core"))
    after <- res$dict
    check(nrow(after) == nrow(dict),
          "the union reproduces the sheet's row count exactly")

    ##Every cell of every replayed row must match what the paste produced.
    cols <- setdiff(DICT_AUTO_COLS, "Contributor")   ##Contributor is forced, not carried
    akey <- dict_key(after[[map[["table"]]]])
    bkey <- dict_key(batch[[map[["table"]]]])
    idx  <- match(bkey, akey)
    diffs <- list()
    for (cl in cols) {
        was <- as.character(batch[[map[[cl]]]])
        now <- as.character(after[[map[[cl]]]])[idx]
        bad <- !(dict_blank(was) & dict_blank(now)) & !identical_chr(was, now)
        if (any(bad)) diffs[[cl]] <- data.frame(table = batch[[map[["table"]]]][bad],
                                                was = was[bad], now = now[bad],
                                                stringsAsFactors = FALSE)
    }
    check(length(diffs) == 0L,
          paste0("all ", nrow(batch), " rows come back byte-identical across ",
                 length(cols), " columns"))
    if (length(diffs)) {
        for (cl in names(diffs)) {
            cat("\n     column:", cl, "--", nrow(diffs[[cl]]), "row(s) differ\n")
            print(utils::head(diffs[[cl]], 3))
        }
    }

    prov <- res$provenance
    check(nrow(prov) == nrow(batch),
          "provenance names every replayed row")
}

cat("\n")
if (failures > 0L) { cat(failures, "FAILURE(S)\n"); quit(status = 1L) }
cat("all checks passed\n")
