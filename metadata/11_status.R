# 11_status.R
#
# Publishes the IRW's corpus-state numbers from one place, so they stop
# being quoted from memory (issue #1765, sub-action 2.5c).
#
# The problem this solves: the Year 3 roadmap (#1702) reports tag coverage
# as 61.7% and the corpus as ~3,650 tables. Two days later the corpus was
# 4,134 tables and coverage was 55.3% -- it had FALLEN six points, because
# the denominator grew by 484 while tagged tables grew by 35. Nobody
# noticed, because the only way to know the number was to recompute it by
# hand, and the figure in the write-up looked authoritative.
#
# So this emits two files, and the second one is the point:
#
#   status.json          the current numbers, machine-readable
#   status_history.tsv   one appended row per run, so the TREND is visible
#
# A single snapshot goes stale silently. A history makes "coverage fell six
# points" a thing you can see rather than a thing you have to discover.
#
# Both are deliberately TRACKED in git. metadata/**/*.csv is gitignored
# because the pipeline CSVs are large regenerable outputs, but these two are
# small and their whole value is being readable over time and in review --
# hence .tsv rather than .csv for the history, which is the only reason for
# that extension.
#
# Reads the local CSVs that 01/03/08 already produce. No Redivis calls, same
# contract as 09_hero_status.R -- run the pipeline first or these numbers
# describe whatever is on disk.
#
# Usage (from metadata/, like the rest of the numbered scripts):
#   Rscript 11_status.R
#   Rscript 11_status.R --dir . --json status.json --history status_history.tsv

suppressPackageStartupMessages({
    library(readr)
    library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
arg <- function(flag, default) {
    i <- match(flag, args)
    if (is.na(i) || i == length(args)) default else args[[i + 1L]]
}
dir      <- arg("--dir", ".")
json_out <- arg("--json", file.path(dir, "status.json"))
hist_out <- arg("--history", file.path(dir, "status_history.tsv"))

read_or_stop <- function(name) {
    p <- file.path(dir, name)
    if (!file.exists(p)) {
        stop(name, " not found in ", normalizePath(dir, mustWork = FALSE),
             ". Run the pipeline first -- this script reports what is on ",
             "disk and must not invent a number for a file it cannot read.",
             call. = FALSE)
    }
    read_csv(p, show_col_types = FALSE)
}

##Every join here is case-insensitive on purpose. 308 tag rows differ from
##their metadata row only by case, and a case-sensitive join silently drops
##all of them -- which is how tag coverage once read 53% instead of 62%.
key <- function(x) tolower(trimws(as.character(x)))

metadata <- read_or_stop("metadata.csv")
tags     <- read_or_stop("tags.csv")
itemtext <- tryCatch(read_or_stop("itemtext_metadata.csv"), error = function(e) NULL)

live <- key(metadata$table)
n    <- length(live)
if (n == 0L) stop("metadata.csv has no rows; refusing to publish a status file.")

covered <- function(other) if (is.null(other)) NA_integer_ else sum(live %in% key(other))
pct     <- function(k) if (is.na(k)) NA_real_ else round(100 * k / n, 1)

n_tags <- covered(tags$table)
n_text <- covered(if (is.null(itemtext)) NULL else itemtext$table)

##Per-warehouse, because the aggregate hides where the gap actually is: the
##roadmap named w3/w4 as the undertagged shards, and by 2026-08-31 w5 was
##worse than either at 7.8% across 206 tables.
shard <- ifelse(is.na(metadata$dataset) | metadata$dataset == "",
                "unknown", as.character(metadata$dataset))
by_shard <- lapply(split(seq_len(n), shard), function(idx) {
    list(n_tables = length(idx),
         tagged   = sum(live[idx] %in% key(tags$table)),
         pct      = round(100 * sum(live[idx] %in% key(tags$table)) / length(idx), 1))
})

##Coverage per COLUMN, not just "has a row" (#1760, 2026-09-01).
##
##`tags` above counts a live table as covered if it has any row at all. That was
##a fair proxy while every row came from a human filling the whole sheet line.
##It stopped being one when `age range` started being derived from `cov_age`:
##that adds ~775 rows carrying one filled column, which would move the headline
##from 55% to ~74% without anyone having tagged a construct, a sample or an item
##format. A number that jumps 19 points for work nobody did is exactly the kind
##of figure 2.5c exists to stop us quoting.
TAG_COLUMNS <- c("age range", "child age (for child-focused studies)", "sample",
                 "construct type", "measurement tool", "item format",
                 "primary language(s)", "construct name")
filled <- function(x) !is.na(x) & trimws(as.character(x)) != ""
live_rows <- tags[key(tags$table) %in% live, , drop = FALSE]
##`child age` is not filled for every table and should not be: the vocabulary
##says leave it blank unless the sample includes children. Reported against all
##4,134 live tables it reads 17.1% and looks like the worst-covered column in
##the project; against the 903 tables whose `age range` is `Child (<18y)` or
##`Mixed` -- the only ones eligible for a value -- it is 78.4%, and the 195
##blanks are tables with no usable `cov_age` to derive from.
##
##That is a measurement bug, not a coverage gap, and it is the same mistake this
##file was written to stop: quoting a number whose denominator does not match
##the claim (#1767, #1837).
##`construct name` is not a tag column and is no longer reported as a coverage
##gap (Ben's ruling, 2026-09-02, #1837). It holds 2,038 distinct values across
##2,265 tables and 1,871 of them are used exactly once -- "International Math
##Olympiad problems", "Individual differences in story recall". Those are
##descriptions, not categories, and a percentage implies a right answer is being
##missed when there is none to miss. The fill rate is still reported, under a
##name that says what it is.
DESCRIPTION_COLS <- c("construct name")

##Every column belongs to one class, and each class is held to its own success
##criterion (#1837, ruled 2026-09-02; the classes are laid out in
##tags/decisions/1837_construct_type.md and on the site's tags_quality page).
##One number for all eight columns is what made item 2 read as never-finishable:
##
##  derived       computed from the table's own data; should approach 100% of
##                the tables eligible for a value, so a shortfall is a bug.
##                Reported as coverage.
##  tagger        reliably inferable from a source read; coverage is a
##                throughput question, but a coverage figure without the
##                accuracy behind it is misleading. Reported as coverage AND
##                accuracy.
##  definitional  what limits these is the definition, not the tagger: writing
##                `sample`'s rules moved its frame facet 26.9% -> 45.5% -> 54.5%
##                with no tagger change. Reported as DEFINITIONAL STATE -- does
##                each value have a written rule -- with coverage as a footnote.
##  description   free text, not a tag; a fill rate (see above).
TAG_CLASS <- c(
    "age range"                             = "derived",
    "child age (for child-focused studies)" = "derived",
    "primary language(s)"                   = "tagger",
    "item format"                           = "tagger",
    "measurement tool"                      = "tagger",
    "sample"                                = "definitional",
    "construct type"                        = "definitional",
    "construct name"                        = "description"
)
CLASS_CRITERION <- list(
    derived      = "coverage of eligible tables; should approach 100%, a shortfall is a bug",
    tagger       = "coverage and accuracy together; coverage is throughput, accuracy says what it is worth",
    definitional = "share of values with a written decision rule; coverage is a footnote",
    description  = "fill rate of a free-text field; not a coverage target"
)

##Paths are resolved from this script's directory, so `--dir` (where the CSVs
##are) and where the registries live stay independent.
script_dir <- local({
    f <- grep("^--file=", commandArgs(FALSE), value = TRUE)
    if (length(f)) dirname(normalizePath(sub("^--file=", "", f[1]))) else getwd()
})
src_dir <- dirname(script_dir)

##Class 2's accuracy is a measurement, not something this script can compute:
##it comes from a blind scoring run against the hand-tagged set. The file names
##its source so a figure can always be traced to the run that produced it.
ACCURACY_FILE <- file.path(src_dir, "tags", "scoring", "accuracy_current.csv")
accuracy <- if (file.exists(ACCURACY_FILE))
    read_csv(ACCURACY_FILE, show_col_types = FALSE,
             col_types = cols(.default = col_character())) else NULL

##Class 3's state: one row per controlled value, with the verbatim phrase in
##vocab.md that defines it (blank = no written rule yet). The phrase is checked
##against vocab.md on every run, so deleting or rewording a rule turns its value
##back to "undefined" here rather than leaving a stale claim. A value in
##TAG_VOCAB with no row at all also counts as undefined -- adding a value
##without a definition cannot pass silently.
DEFS_FILE  <- file.path(src_dir, "tags", "decisions", "value_definitions.csv")
VOCAB_FILE <- file.path(src_dir, "tags", ".claude", "skills", "irw-auto-tag",
                        "references", "vocab.md")
defs <- if (file.exists(DEFS_FILE))
    read_csv(DEFS_FILE, show_col_types = FALSE,
             col_types = cols(.default = col_character())) else NULL
vocab_text <- if (file.exists(VOCAB_FILE))
    gsub("\\s+", " ", paste(readLines(VOCAB_FILE, warn = FALSE), collapse = " ")) else NULL
##TAG_VOCAB (the enforced value lists) lives in tag_normalize.R; sourcing it
##only defines functions and constants.
tag_vocab <- tryCatch({
    e <- new.env()
    sys.source(file.path(script_dir, "tag_normalize.R"), envir = e)
    e$TAG_VOCAB
}, error = function(err) NULL)

definitional_state <- function(cl) {
    values <- setdiff(tag_vocab[[cl]], "NA")
    if (is.null(values) || is.null(defs) || is.null(vocab_text)) {
        warning("definitional state for `", cl, "` unavailable: missing ",
                paste(c(if (is.null(tag_vocab)) "TAG_VOCAB",
                        if (is.null(defs)) DEFS_FILE,
                        if (is.null(vocab_text)) VOCAB_FILE), collapse = ", "),
                call. = FALSE)
        return(NULL)
    }
    d <- defs[defs$column == cl, , drop = FALSE]
    anchor <- setNames(d$anchor, d$value)
    found <- vapply(values, function(v) {
        a <- anchor[v]
        !is.na(a) && nzchar(trimws(a)) &&
            grepl(gsub("\\s+", " ", trimws(a)), vocab_text, fixed = TRUE)
    }, logical(1))
    stale <- values[!found & values %in% d$value[!is.na(d$anchor) & nzchar(d$anchor)]]
    if (length(stale)) {
        warning("`", cl, "`: the rule text for ", paste(stale, collapse = ", "),
                " is no longer in vocab.md; counted as undefined", call. = FALSE)
    }
    list(values           = length(values),
         values_with_rule = sum(found),
         pct_with_rule    = round(100 * mean(found), 1),
         without_rule     = I(sort(values[!found])),
         rules            = "tags/.claude/skills/irw-auto-tag/references/vocab.md",
         registry         = "tags/decisions/value_definitions.csv")
}

accuracy_of <- function(cl) {
    if (is.null(accuracy)) return(NULL)
    a <- accuracy[accuracy$column == cl, , drop = FALSE]
    if (!nrow(a)) return(NULL)
    num <- function(x) if (is.na(x) || !nzchar(x)) NULL else as.numeric(x)
    Filter(Negate(is.null), list(
        exact_pct     = num(a$exact_pct[1]),
        precision_pct = num(a$precision_pct[1]),
        recall_pct    = num(a$recall_pct[1]),
        n_answered    = num(a$n_answered[1]),
        n_gold        = num(a$n_gold[1]),
        measured      = a$measured[1],
        source        = a$source[1]))
}

ELIGIBLE_WHEN <- list(`child age (for child-focused studies)` =
                      function(d) trimws(as.character(d[["age range"]])) %in%
                                  c("Child (<18y)", "Mixed"))

by_column <- lapply(intersect(TAG_COLUMNS, names(live_rows)), function(cl) {
    gate <- ELIGIBLE_WHEN[[cl]]
    rows <- if (is.null(gate)) live_rows else live_rows[gate(live_rows), , drop = FALSE]
    denom <- if (is.null(gate)) n else length(unique(key(rows$table)))
    k <- length(unique(key(rows$table[filled(rows[[cl]])])))
    cov <- list(n = k, pct = if (denom > 0) round(100 * k / denom, 1) else 0)
    if (!is.null(gate)) {
        cov$denominator <- denom
        cov$of <- "tables whose `age range` is Child (<18y) or Mixed"
        cov$pct_of_all_tables <- pct(k)
    }
    cls <- unname(TAG_CLASS[cl])
    if (is.na(cls)) stop("tag column `", cl, "` has no class in TAG_CLASS (#1837)")
    out <- list(class = cls)
    if (cls == "definitional") {
        ##The headline is the definitional state; coverage moves to a footnote
        ##so it cannot be quoted as though it were the measure (#1837).
        out$definitional <- definitional_state(cl)
        out$coverage_footnote <- cov
    } else {
        out <- c(out, cov)
        if (cls == "tagger") {
            acc <- accuracy_of(cl)
            out$accuracy <- if (is.null(acc)) "not measured" else acc
        }
        if (cl %in% DESCRIPTION_COLS) {
            out$note <- paste("free text, not a controlled vocabulary -- a fill rate,",
                              "not a coverage target (#1837)")
        }
    }
    out
})
names(by_column) <- intersect(TAG_COLUMNS, names(live_rows))

##The filled count for a column whatever its class -- class 3 keeps it in the
##footnote. The history row is a count per column and stays one.
col_n <- function(cl) {
    x <- by_column[[cl]]
    if (is.null(x)) NA_integer_ else if (!is.null(x$n)) x$n else x$coverage_footnote$n
}

status <- list(
    generated   = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
    source      = "metadata/11_status.R -- local pipeline CSVs, no Redivis calls",
    n_tables    = n,
    coverage    = list(
        ##`tags` is "has a row"; `tags_by_column` is what is actually filled.
        ##Quote the column, not the row, whenever the claim is about tagging.
        tags     = list(n = n_tags, pct = pct(n_tags)),
        tags_by_column = by_column,
        ##How to read each column's entry: its class, and what it is held to.
        tag_classes = Map(function(cls, crit) list(
                              criterion = crit,
                              columns   = I(names(TAG_CLASS)[TAG_CLASS == cls])),
                          names(CLASS_CRITERION), CLASS_CRITERION),
        itemtext = list(n = n_text, pct = pct(n_text))
    ),
    tags_by_shard = by_shard,
    ##Orphan rows should be 0 from #1766 onward: 03_tags.R now drops tag rows
    ##for tables that are not live. A non-zero value here means that guard
    ##did not run, or ran against a stale metadata.csv.
    orphan_tag_rows = sum(!(key(tags$table) %in% live))
)

write_json(status, json_out, auto_unbox = TRUE, pretty = TRUE, digits = NA)

row <- data.frame(
    date            = format(Sys.Date()),
    n_tables        = n,
    tagged          = n_tags,
    tagged_pct      = pct(n_tags),
    ##One field per tag column, not just the two that happened to be added
    ##first. `tagged` counts tables with ANY row, and 775 age-only rows from
    ##the #1760 derivation moved it from 55.3% to ~74% without anyone tagging
    ##a construct or a sample -- so it cannot be read as progress on the tag
    ##gap (#1704). These are what a batch is read against.
    age_range       = col_n("age range"),
    child_age       = col_n("child age (for child-focused studies)"),
    sample          = col_n("sample"),
    construct_type  = col_n("construct type"),
    measurement_tool = col_n("measurement tool"),
    item_format     = col_n("item format"),
    primary_languages = col_n("primary language(s)"),
    construct_name  = col_n("construct name"),
    itemtext        = n_text,
    itemtext_pct    = pct(n_text),
    orphan_tag_rows = status$orphan_tag_rows
)
##Append, never rewrite: the history is the deliverable, and one bad run
##must not be able to erase what earlier runs recorded. Re-running on a day
##when nothing moved is a no-op rather than a duplicate row -- the pipeline
##gets run repeatedly while debugging, and a history padded with identical
##rows is harder to read the trend out of.
##Widening the row without widening the file writes a row with more fields than
##the header, and every value after the new columns lands under the wrong name.
##That happened on 2026-09-01 when age_range/construct_type were added: the
##appended row put 2243 in the `itemtext` column. Append-only is right for the
##DATA; the SCHEMA still has to be migrated deliberately.
if (file.exists(hist_out)) {
    hdr <- names(suppressWarnings(read_tsv(hist_out, n_max = 0,
                                           show_col_types = FALSE)))
    if (!identical(hdr, names(row))) {
        extra <- setdiff(hdr, names(row))
        if (length(extra)) {
            stop("status_history.tsv has column(s) this script no longer writes: ",
                 paste(extra, collapse = ", "),
                 ". Refusing to append -- widen `row` or migrate the file by hand.")
        }
        ##Only new columns: migrate in place, backfilling the older rows.
        old_rows <- suppressWarnings(read_tsv(hist_out, show_col_types = FALSE,
                                              col_types = cols(.default = col_character())))
        for (cl in setdiff(names(row), hdr)) old_rows[[cl]] <- NA_character_
        old_rows <- old_rows[, names(row), drop = FALSE]
        write_tsv(old_rows, hist_out)
        cat("status_history.tsv: added column(s) ",
            paste(setdiff(names(row), hdr), collapse = ", "),
            "; ", nrow(old_rows), " earlier row(s) backfilled as NA\n", sep = "")
    }
}

unchanged <- FALSE
if (file.exists(hist_out)) {
    ##Read as character throughout. Type inference would parse `date` as a
    ##Date, and unlist() then strips the class and compares the underlying
    ##day count against the formatted string -- so the guard never fires.
    prev <- suppressWarnings(read_tsv(hist_out, show_col_types = FALSE,
                                      col_types = cols(.default = col_character())))
    if (nrow(prev) > 0L) {
        last <- prev[nrow(prev), , drop = FALSE]
        cmp  <- intersect(names(last), names(row))
        as_chr <- function(d) vapply(d, function(x) as.character(x), character(1))
        unchanged <- identical(as_chr(last[cmp]), as_chr(row[cmp]))
    }
}
if (unchanged) {
    cat("history unchanged since the last run; not appending a duplicate row\n")
} else {
    write_tsv(row, hist_out, append = file.exists(hist_out),
              col_names = !file.exists(hist_out))
}

cat(sprintf("%s: %d tables | tags %d (%.1f%%) | itemtext %d (%.1f%%) | orphan tag rows %d\n",
            row$date, n, n_tags, pct(n_tags), n_text, pct(n_text),
            status$orphan_tag_rows))
cat("wrote ", json_out,
    if (unchanged) paste0("; ", hist_out, " unchanged")
    else paste0("; appended to ", hist_out), "\n", sep = "")
