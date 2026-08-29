# Usage: Rscript audit_batch.R <batch_dir> [output_csv] [--resp-dir <dir>]
#
# --resp-dir audits against local IRW response CSVs (<dir>/<table>.csv)
# instead of live Redivis data, for tables that are not published yet -- the
# automated_finding pipeline generates item text at processing time from the
# CSVs staged in irw_output/ (see automated_finding SKILL.md Step 3.5). A
# table with no CSV in <dir> is an ERROR row, not a silent fall back to live:
# mixing the two sources within one report would make it unreadable.
# Without the flag the behaviour is unchanged: live data.
#
# Batch-level sanity audit: for every <table>__items.csv in <batch_dir>,
# merges it against the live Redivis response data.
#
# It does NOT download the response tables. Everything this script needs from
# live data -- the item set, the resp set, each item's own resp levels, and each
# item's row count -- is one GROUP BY, so it asks Redivis for the summary instead
# of exporting the rows to compute it here. That is both faster and quota-safe:
# on 2026-08-18 the account's 200GB/30-day export limit was exhausted, and since
# the core warehouse is 181.8GB a single full pass over it spends ~91% of a
# month's allowance. Exports are capped; queries are not. irw::irw_fetch() is
# kept only as a fallback for the case where the query route itself fails.
# and runs the same checks validate_items.R does per-table (item-set,
# resp-set, required columns) PLUS the checks SKILL.md's Step 5 calls out
# as necessary but that validate_items.R doesn't currently automate:
#   - row-count-per-item anomalies (a matching item *set* doesn't rule out
#     one item code silently standing in for two different questions --
#     this is the check that caught that case in practice, per SKILL.md)
#   - item_text / option_text coverage (fraction blank)
#   - duplicate item rows within one table's csv (ambiguous merge)
#
# This does not replace validate_items.R -- run that per-table during
# extraction as the hard gate before a file is ever written. This script is
# for auditing an already-written batch folder as a whole, producing one
# summary row per table plus a printed detail section for anything that
# needs a human look.
#
# Output: <batch_dir>/audit_report.csv (or the path in argv[2]), one row per
# table, plus a console summary. Never modifies the {table}__items.csv files
# or notes.csv -- read-only against batch output, write-only to the report.

args <- commandArgs(trailingOnly = TRUE)

# --resp-dir <dir>, stripped before the positional args are read so existing
# calls keep working untouched.
resp_dir <- NA_character_
i <- match("--resp-dir", args)
if (!is.na(i)) {
    if (length(args) < i + 1) stop("--resp-dir needs a directory")
    resp_dir <- args[i + 1]
    args <- args[-c(i, i + 1)]
    if (!dir.exists(resp_dir)) stop("--resp-dir not a directory: ", resp_dir)
}

if (length(args) < 1) {
    stop("Usage: Rscript audit_batch.R <batch_dir> [output_csv] [--resp-dir <dir>]")
}
batch_dir <- sub("/$", "", args[1])
out_path <- if (length(args) >= 2) args[2] else file.path(batch_dir, "audit_report.csv")

# Resolve the helper next to this script, however the script was invoked.
script_dir <- {
    a <- commandArgs(trailingOnly = FALSE)
    f <- sub("^--file=", "", a[grep("^--file=", a)])
    if (length(f)) dirname(normalizePath(f[1])) else "."
}
source(file.path(script_dir, "fetch_resp.R"))

files <- list.files(batch_dir, pattern = "__items\\.csv$", full.names = TRUE)
if (length(files) == 0) stop("No *__items.csv files found in ", batch_dir)

required_cols <- c("table", "section_id", "item", "instrument", "instructions",
                    "section_prompt", "item_text", "correct_response", "option_text")

is_blank <- function(x) is.na(x) | trimws(as.character(x)) == ""

# Does this file already use the corpus's on-disk null convention (the NA
# token, as write.csv emits it)? Must be checked against raw bytes: read.csv
# maps unquoted-empty, quoted-empty and the NA token all to the same
# in-memory NA, so a parsed-value check cannot see the difference and would
# silently pass an inconsistent file. See normalize_nulls.R for the evidence
# that NA is the convention across the 422 published tables.
uses_canonical_nulls <- function(path, items) {
    for (cn in names(items)) {
        if (!is.character(items[[cn]])) next
        blank <- !is.na(items[[cn]]) & trimws(items[[cn]]) == ""
        items[[cn]][blank] <- NA_character_
    }
    want <- utils::capture.output(write.csv(items, row.names = FALSE))
    identical(want, readLines(path, warn = FALSE))
}

# Every result row must carry the same fields, or the rbind below fails on
# the first table that errors out.
error_row <- function(table, note) {
    list(table = table, status = "ERROR", n_items_live = NA,
         n_items_candidate = NA, item_set_match = NA, resp_set_match = NA,
         uses_raw_resp = NA, canonical_nulls = NA, pct_item_text_missing = NA,
         pct_option_text_missing = NA, note = note)
}

# ---------------------------------------------------------------------------
# live_sets(table): everything this script needs from live data -- the item set,
# the resp set, each item's row count, and each item's own resp levels -- with
# no export.
#
# Shard resolution and the canonical item/resp sets come from
# irw::irw_table_sets() (Rpkg#121, in irw >= 1.0.1). This file used to carry its
# own copy of both; the package owns that logic now so the two cannot drift, and
# its resp coercion is the one that matches irw_fetch() (the literal "NA" token
# and blanks drop out).
#
# The per-item detail is one further GROUP BY against the qualified reference the
# package resolved. irw_table_sets(per_item = TRUE) is deliberately NOT used for
# it: it returns each item's resp min/max/level COUNT, and the per-item coverage
# check below needs the actual SET of levels an item's respondents used (it is
# what caught the alkouri_2025_* defect). Its `n` also counts only non-missing
# resp, where the row-count anomaly check wants each item's TOTAL rows,
# missingness included -- so `resp` is left NULL rather than filtered out, and
# the rows still count.
live_sets <- function(table) {
    s <- irw::irw_table_sets(table, source = "core", per_item = FALSE)
    sql <- sprintf(paste(
        "SELECT CAST(item AS STRING) AS item,",
        "  CASE WHEN resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
        "       THEN SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) END AS resp,",
        "  COUNT(*) AS n",
        "FROM `%s` GROUP BY 1, 2"), s$table)
    d <- suppressWarnings(redivis::redivis$query(sql)$to_tibble())
    item <- as.character(d$item)
    resp <- as.numeric(d$resp)
    n <- as.numeric(d$n)

    counts <- tapply(n, item, sum)
    levels <- tapply(resp, item, function(v) sort(unique(v[!is.na(v)])))
    list(items = as.character(s$items),
         resp = suppressWarnings(as.numeric(s$resp)),
         counts = counts,
         levels = levels)
}

# <resp-dir>/<table>.csv -- the automated_finding staging convention
# (irw_output/<table>.csv, one CSV per measurement scale, named for the table).
local_resp_path <- function(table) {
    p <- file.path(resp_dir, paste0(table, ".csv"))
    if (!file.exists(p)) {
        stop("no response CSV at ", p,
             " -- every table in the batch needs one when --resp-dir is used")
    }
    p
}

audit_one <- function(path) {
    table <- sub("__items\\.csv$", "", basename(path))
    items <- tryCatch(read.csv(path, stringsAsFactors = FALSE),
                       error = function(e) NULL)
    if (is.null(items)) {
        return(error_row(table, "could not read csv"))
    }

    live <- tryCatch(
        if (is.na(resp_dir)) live_sets(table) else resp_sets_local(local_resp_path(table)),
        error = function(e) conditionMessage(e))
    if (is.character(live)) {
        return(error_row(table, paste0(
            if (is.na(resp_dir)) "could not read live data: " else "could not read response CSV: ",
            live)))
    }
    if (!length(live$items)) {
        return(error_row(table, "live table has no item values"))
    }

    notes <- character(0)
    status <- "PASS"

    # -- on-disk null convention --
    canonical_nulls <- tryCatch(uses_canonical_nulls(path, items),
                                 error = function(e) NA)
    if (isFALSE(canonical_nulls)) {
        status <- "WARN"
        notes <- c(notes, paste0(
            "on-disk null/quoting form deviates from the corpus convention ",
            "(NA token as write.csv emits it) -- run normalize_nulls.R on this batch"))
    }

    # -- required columns --
    missing_cols <- setdiff(required_cols, names(items))
    if (length(missing_cols)) {
        status <- "WARN"
        notes <- c(notes, paste0("missing columns: ", paste(missing_cols, collapse = ", ")))
    }

    has_resp <- "resp" %in% names(items) && any(!is_blank(items$resp))
    raw_resp_col <- if ("raw_resp" %in% names(items)) "raw_resp"
                    else if ("resp_raw" %in% names(items)) "resp_raw" else NA

    # -- item set match --
    live_items <- live$items
    cand_items <- unique(items$item)
    missing_items <- setdiff(live_items, cand_items)
    extra_items <- setdiff(cand_items, live_items)
    if (length(missing_items) || length(extra_items)) {
        status <- "FAIL"
        if (length(missing_items)) notes <- c(notes, paste0(
            "item set: ", length(missing_items), " live item(s) missing from csv (",
            paste(utils::head(missing_items, 10), collapse = ", "),
            if (length(missing_items) > 10) ", ..." else "", ")"))
        if (length(extra_items)) notes <- c(notes, paste0(
            "item set: ", length(extra_items), " csv item(s) not in live data (",
            paste(utils::head(extra_items, 10), collapse = ", "),
            if (length(extra_items) > 10) ", ..." else "", ")"))
    }

    # -- resp set match (skipped when using raw_resp by design) --
    if (has_resp) {
        live_resp <- sort(live$resp)
        cand_resp <- sort(unique(items$resp))
        missing_resp <- setdiff(live_resp, cand_resp)
        extra_resp <- setdiff(cand_resp, live_resp)
        if (length(missing_resp) || length(extra_resp)) {
            status <- "FAIL"
            notes <- c(notes, paste0(
                "resp set mismatch: missing=", paste(utils::head(missing_resp, 10), collapse = ";"),
                " extra=", paste(utils::head(extra_resp, 10), collapse = ";")))
        }
    } else if (is.na(raw_resp_col)) {
        status <- "FAIL"
        notes <- c(notes, "no resp or raw_resp/resp_raw column with any values")
    } else {
        notes <- c(notes, paste0("using ", raw_resp_col, " (no scoring key recoverable) -- resp-set check skipped by design"))
    }

    # -- duplicate item rows within the candidate csv (ambiguous merge) --
    dup_items <- cand_items[duplicated(items$item) | duplicated(items$item, fromLast = TRUE)]
    if (length(unique(dup_items))) {
        # only a real problem if item_text/resp differ across the duplicate rows
        problematic <- character(0)
        for (it in unique(dup_items)) {
            sub <- items[items$item == it, , drop = FALSE]
            if ("item_text" %in% names(sub) && length(unique(trimws(as.character(sub$item_text)))) > 1) {
                problematic <- c(problematic, it)
            }
        }
        if (length(problematic)) {
            status <- "FAIL"
            notes <- c(notes, paste0("duplicate item rows with conflicting item_text: ",
                                      paste(utils::head(problematic, 10), collapse = ", ")))
        }
    }

    # -- row-count-per-item anomaly (conflation check, per SKILL.md Step 5) --
    # A matching item *set* doesn't rule out one item code silently standing
    # in for two different questions -- flag items whose live row count is a
    # clear outlier relative to the table's typical per-item row count.
    live_counts <- live$counts
    if (length(live_counts) >= 3) {
        med <- stats::median(live_counts)
        if (med > 0) {
            ratio <- live_counts / med
            anomalous <- names(live_counts)[ratio > 1.5 | ratio < (1 / 1.5)]
            if (length(anomalous)) {
                status <- if (status == "PASS") "WARN" else status
                notes <- c(notes, paste0(
                    "row-count anomaly (possible item-code conflation or missingness skew), median=",
                    med, ": ", paste(utils::head(anomalous, 10), collapse = ", "),
                    if (length(anomalous) > 10) ", ..." else ""))
            }
        }
    }

    # -- item_text / option_text coverage --
    if ("item_text" %in% names(items)) {
        pct_missing_text <- round(100 * mean(is_blank(items$item_text)), 1)
        if (pct_missing_text > 0) {
            status <- if (status == "PASS") "WARN" else status
            notes <- c(notes, paste0(pct_missing_text, "% of rows have blank item_text"))
        }
    } else {
        pct_missing_text <- NA
    }
    if ("option_text" %in% names(items)) {
        pct_missing_opt <- round(100 * mean(is_blank(items$option_text)), 1)
        if (pct_missing_opt > 0) {
            notes <- c(notes, paste0(pct_missing_opt, "% of rows have blank option_text"))
        }
        # Blank option_text is legitimate table-wide (day counts, behaviour-scored
        # items, unlabeled scale points), which is why the coverage figure above
        # only notes rather than warns. What is NOT legitimate is the asymmetric
        # case: some items carry their option rows while other items in the same
        # table carry none. That means those items' response options can't be
        # linked to any resp value, and it slips past validate_items.R because the
        # resp *set* over the whole table still matches. Caught in the wild on
        # alkouri_2025_coping / alkouri_2025_icu_stressors (2026-08-17), where
        # item_01 had all five options and items 2..n had a single NA-resp row.
        if ("item" %in% names(items)) {
            opts_per_item <- tapply(!is_blank(items$option_text), items$item, sum)
            with_opts <- sum(opts_per_item > 0)
            without <- names(opts_per_item)[opts_per_item == 0]
            if (with_opts > 0 && length(without) > 0) {
                status <- "WARN"
                notes <- c(notes, paste0(
                    length(without), " of ", length(opts_per_item),
                    " items have NO option_text rows while others do (",
                    paste(utils::head(without, 6), collapse = ", "),
                    if (length(without) > 6) ", ..." else "", ")"))
            }

            # Per-item resp coverage. validate_items.R compares the resp SET over
            # the whole table, so an item can be missing option rows for levels
            # that its own respondents actually used and still pass -- the table's
            # other items supply those values. Joining itemtext to the response
            # data on (item, resp) then silently drops those responses. This is a
            # finer-grained version of the check above and would have caught the
            # alkouri_2025_* defect on its own.
            if ("resp" %in% names(items)) {
                live_lv <- live$levels
                cand_lv <- tapply(suppressWarnings(as.numeric(items$resp)), items$item,
                                  function(v) sort(unique(v[!is.na(v)])))
                gaps <- character(0)
                for (i in names(live_lv)) {
                    m <- setdiff(live_lv[[i]], cand_lv[[i]])
                    if (length(m)) gaps <- c(gaps, paste0(i, "(", paste(m, collapse = ","), ")"))
                }
                if (length(gaps)) {
                    status <- "WARN"
                    notes <- c(notes, paste0(
                        length(gaps), " item(s) have live resp values with no option_text row: ",
                        paste(utils::head(gaps, 6), collapse = ", "),
                        if (length(gaps) > 6) ", ..." else ""))
                }
            }
        }
        # Padding an unlabeled scale point with its own number is worse than
        # leaving it blank: it reads as a real label downstream, and it
        # inflates the coverage figure above so the table looks cleaner than
        # a table that honestly left the same gap empty. Caught in the wild
        # on agogue_2020 (2026-08-17), where a 1-7 scale with only endpoint
        # anchors had "2".."6" written into option_text.
        if ("resp" %in% names(items)) {
            padded <- !is_blank(items$option_text) &
                trimws(as.character(items$option_text)) == trimws(as.character(items$resp))
            # A labeled option whose resp is NA (e.g. a "Don't know" choice the
            # source offered but that maps to missing in the live data) makes the
            # == comparison NA, not FALSE -- and any(NA) is NA, which is an error
            # inside if(). Such a row is by definition not padded.
            padded[is.na(padded)] <- FALSE
            if (any(padded)) {
                status <- "WARN"
                notes <- c(notes, paste0(
                    "option_text is just the resp value for ", sum(padded),
                    " row(s) (resp: ", paste(sort(unique(items$resp[padded])), collapse = ","),
                    ") -- unlabeled scale points should be blank, not padded with the number"))
            }
        }
    } else {
        pct_missing_opt <- NA
    }

    list(
        table = table,
        status = status,
        n_items_live = length(live_items),
        n_items_candidate = length(cand_items),
        item_set_match = length(missing_items) == 0 && length(extra_items) == 0,
        resp_set_match = if (has_resp) length(setdiff(sort(unique(live$resp)), sort(unique(items$resp)))) == 0 &&
                                        length(setdiff(sort(unique(items$resp)), sort(unique(live$resp)))) == 0
                          else NA,
        uses_raw_resp = !is.na(raw_resp_col),
        canonical_nulls = canonical_nulls,
        pct_item_text_missing = pct_missing_text,
        pct_option_text_missing = pct_missing_opt,
        note = paste(notes, collapse = " | ")
    )
}

results <- lapply(files, function(f) {
    cat("Auditing", basename(f), "...\n")
    tryCatch(audit_one(f), error = function(e) {
        list(table = sub("__items\\.csv$", "", basename(f)), status = "ERROR",
             n_items_live = NA, n_items_candidate = NA, item_set_match = NA,
             resp_set_match = NA, uses_raw_resp = NA, canonical_nulls = NA,
             pct_item_text_missing = NA, pct_option_text_missing = NA,
             note = paste("unexpected error:", conditionMessage(e)))
    })
})

report <- do.call(rbind, lapply(results, as.data.frame, stringsAsFactors = FALSE))
write.csv(report, out_path, row.names = FALSE)

cat("\n=== Summary (", nrow(report), " tables) ===\n", sep = "")
print(table(report$status))
cat("\nWritten to:", out_path, "\n")

flagged <- report[report$status %in% c("WARN", "FAIL", "ERROR"), , drop = FALSE]
if (nrow(flagged)) {
    cat("\n=== Needs a look ===\n")
    for (i in seq_len(nrow(flagged))) {
        cat("[", flagged$status[i], "] ", flagged$table[i], ": ", flagged$note[i], "\n", sep = "")
    }
} else {
    cat("\nAll tables PASS with no anomalies.\n")
}
