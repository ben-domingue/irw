## Incremental update: processes only tables not yet in itemtext_metadata,
## then appends to the existing table and writes an updated CSV.
## For a full recompute (e.g. new columns), use hotfixes/08_itemtext_recompute.R.
## Requires: quanteda, quanteda.textstats

library(redivis)
source("redivis_config.R")
library(quanteda)
library(quanteda.textstats)

script_path <- grep("--file=", commandArgs(FALSE), value = TRUE)
here <- if (length(script_path)) dirname(normalizePath(sub("--file=", "", script_path[1]))) else getwd()

remove <- NULL  # c("table_name") to exclude specific tables

## all tables with item text
lt <- irw::irw_list_itemtext_tables()
lt <- lt[!lt %in% remove]

## tables already in Redivis
user    <- redivis$user(IRW_OWNER)
dataset <- user$dataset("irw_meta")
table   <- dataset$table("itemtext_metadata")
published <- as.data.frame(table$to_tibble())
## Start from the repo CSV, not the published table; see base_guard.R. The
## column set is whatever published carries, so a column added upstream still
## arrives; FK_grade is back-filled below either way.
source(file.path(here, "base_guard.R"))
source(file.path(here, "itemtext_prune.R"))
existing <- choose_base(file.path(here, "itemtext_metadata.csv"), published, names(published),
                        label = "itemtext_metadata.csv")

## only process tables not yet present
tables.new <- lt[!lt %in% existing$table]
## A run with nothing new still has work to do, so this no longer quits here.
## It used to, which meant two things that act on EXISTING rows only ran on runs
## that happened to add a table: `prune_unserved_itemtext` (#3240), which is how
## a withdrawn table's row leaves the file, and the language fill below (#3224).
## A quiet week should not postpone a withdrawal's bookkeeping.
if (length(tables.new) == 0) {
    message("No new tables to process; updating existing rows only.")
}

fk_score <- function(texts) {
    texts <- texts[!is.na(texts) & nchar(trimws(texts)) > 0]
    if (length(texts) == 0) return(NA_real_)
    texts <- ifelse(grepl("[.!?]\\s*$", trimws(texts)), texts, paste0(trimws(texts), "."))
    corp <- quanteda::corpus(paste(texts, collapse = " "))
    quanteda.textstats::textstat_readability(corp, measure = "Flesch.Kincaid")$Flesch.Kincaid
}

## IRW's published null is the literal string "NA", so a cell reading NA is unset
## rather than a language called NA (see irw-corpus-listing-and-null-traps).
UNSET_LANGUAGE <- c("", "NA", "N/A", "null", "NULL", "None")

## One language per table for itemtext_metadata (irw#3224).
##
## Ruled 2026-10-28: every table that serves item text must SAY what language
## respondents read, with `unknown` a permitted explicit value. The field lives
## here rather than on the 2,746 shard tables themselves: 1,095 of them have no
## `language` column at all, and adding one to each would be 1,095 replace-uploads
## and 1,095 publish decisions to record a fact that belongs in the per-table
## record anyway.
##
## A multi-language administration keeps the standard's semicolon list.
collapse_language <- function(values) {
    v <- trimws(as.character(values))
    v <- v[!is.na(v) & !(v %in% UNSET_LANGUAGE)]
    if (length(v) == 0) return(NA_character_)
    paste(sort(unique(v)), collapse = "; ")
}

summarize_table <- function(x) {
    lang <- collapse_language(x$language)
    data.frame(
        table                    = unique(x$table),
        instrument               = unique(x$instrument)[1],
        mean_word                = mean(x$nw,        na.rm = TRUE),
        mean_character           = mean(x$nc,        na.rm = TRUE),
        mean_character_responses = mean(x$nc.option, na.rm = TRUE),
        FK_grade                 = fk_score(x$item_text),
        ## No language column on a table built under the current standard means
        ## an English administration -- the standard says to omit it rather than
        ## emit it empty (references/itemtext_standard.md). That inference is
        ## sound for a table arriving NOW and is exactly what it is not for a
        ## table published before 2026-09-01, when no table had the column; those
        ## are filled from itemtext/itemtext_language.csv instead.
        language                 = if (is.na(lang)) "English" else lang,
        language_source          = if (is.na(lang)) "standard_omission" else "table"
    )
}

L <- list()
for (ii in seq_along(tables.new)) {
    tab <- tables.new[ii]
    cat(sprintf("[%d/%d] %s\n", ii, length(tables.new), tab))
    items <- irw::irw_itemtext(tab)
    z <- if ("item_text_translated" %in% names(items)) items$item_text_translated else items$item_text
    # item_text arrives typed by its content: a table whose text is all bare
    # digits (SART stimuli, say) comes back integer, and strsplit rejects a
    # non-character argument. nchar() coerces silently; strsplit does not.
    z         <- as.character(z)
    nw        <- lengths(strsplit(z, " "))
    nc        <- nchar(z)
    nc.option <- if ("option_text" %in% names(items)) nchar(items$option_text) else rep(NA_real_, length(z))
    instrument <- if ("instrument"  %in% names(items)) items$instrument        else rep(NA_character_, length(z))
    ## The administered language, carried per row so summarize_table can collapse
    ## it. A table built under the current standard omits the column entirely for
    ## an English administration, which is why absence is read as English BELOW
    ## rather than here -- the distinction only makes sense once we know the
    ## table is new, and everything in this loop is new (irw#3224).
    language <- if ("language" %in% names(items)) as.character(items$language)
                else rep(NA_character_, length(z))
    L[[tab]] <- data.frame(table = tab, instrument = instrument, item = items$item,
                           item_text = z, nw = nw, nc = nc, nc.option = nc.option,
                           language = language)
}

save(L, file = file.path(here, "items_alltext.Rdata"))

rows      <- lapply(L, summarize_table)
## `do.call(rbind, list())` is NULL, and rbind(NULL, df) is df, so an empty run
## falls through to the existing rows untouched -- but the column set has to come
## from somewhere, so take it from `existing` in that case.
merge.new <- if (length(rows)) do.call(rbind, rows) else NULL

## align columns: add FK_grade to existing if this is the first run with it
if (!"FK_grade" %in% names(existing)) existing$FK_grade <- NA_real_

## The language of every table that was already in the file (irw#3224). A table
## published before 2026-09-01 could not have carried a `language` column, so
## absence says nothing about what respondents read and must not be read as
## English. itemtext/itemtext_language.csv is what was established by reading the
## shipped text and the 2026-09-01 audit; anything it does not cover is
## `unknown`, which is a claim we can defend and upgrade a row at a time.
lang_file <- file.path(here, "..", "itemtext", "itemtext_language.csv")
if (!"language" %in% names(existing)) {
    existing$language <- NA_character_
    existing$language_source <- NA_character_
}
if (file.exists(lang_file)) {
    known <- read.csv(lang_file, stringsAsFactors = FALSE)
    hit <- match(existing$table, known$table)
    fill <- !is.na(hit) & (is.na(existing$language) | existing$language %in% UNSET_LANGUAGE)
    existing$language[fill]        <- known$language[hit[fill]]
    existing$language_source[fill] <- known$language_source[hit[fill]]
    message(sprintf("language: filled %d existing row(s) from %s",
                    sum(fill), basename(lang_file)))
} else {
    message("language: no itemtext_language.csv; existing rows stay as they are")
}
blank <- is.na(existing$language) | existing$language %in% UNSET_LANGUAGE
existing$language[blank]        <- "unknown"
existing$language_source[blank] <- "unestablished"
if (any(blank)) {
    message(sprintf("language: %d existing row(s) left unknown", sum(blank)))
}

keep_cols <- if (is.null(merge.new)) names(existing) else names(merge.new)
df <- rbind(merge.new, existing[, keep_cols])

## Drop rows whose item text is no longer served (see itemtext_prune.R for the
## why, and for the guard that refuses to act on a failed listing).
df <- prune_unserved_itemtext(df, lt)

write.csv(df, file = file.path(here, "itemtext_metadata.csv"), quote = TRUE, row.names = FALSE)
