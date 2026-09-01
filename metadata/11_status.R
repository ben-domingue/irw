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

status <- list(
    generated   = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
    source      = "metadata/11_status.R -- local pipeline CSVs, no Redivis calls",
    n_tables    = n,
    coverage    = list(
        tags     = list(n = n_tags, pct = pct(n_tags)),
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
    itemtext        = n_text,
    itemtext_pct    = pct(n_text),
    orphan_tag_rows = status$orphan_tag_rows
)
##Append, never rewrite: the history is the deliverable, and one bad run
##must not be able to erase what earlier runs recorded. Re-running on a day
##when nothing moved is a no-op rather than a duplicate row -- the pipeline
##gets run repeatedly while debugging, and a history padded with identical
##rows is harder to read the trend out of.
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
