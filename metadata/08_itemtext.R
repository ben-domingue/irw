## Incremental update: processes only tables not yet in itemtext_metadata,
## then appends to the existing table and writes an updated CSV.
## For a full recompute (e.g. new columns), use 08_itemtext_recompute.R.
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
existing <- as.data.frame(table$to_tibble())

## only process tables not yet present
tables.new <- lt[!lt %in% existing$table]
if (length(tables.new) == 0) {
    message("No new tables to process.")
    quit(save = "no")
}

fk_score <- function(texts) {
    texts <- texts[!is.na(texts) & nchar(trimws(texts)) > 0]
    if (length(texts) == 0) return(NA_real_)
    texts <- ifelse(grepl("[.!?]\\s*$", trimws(texts)), texts, paste0(trimws(texts), "."))
    corp <- quanteda::corpus(paste(texts, collapse = " "))
    quanteda.textstats::textstat_readability(corp, measure = "Flesch.Kincaid")$Flesch.Kincaid
}

summarize_table <- function(x) {
    data.frame(
        table                    = unique(x$table),
        instrument               = unique(x$instrument)[1],
        mean_word                = mean(x$nw,        na.rm = TRUE),
        mean_character           = mean(x$nc,        na.rm = TRUE),
        mean_character_responses = mean(x$nc.option, na.rm = TRUE),
        FK_grade                 = fk_score(x$item_text)
    )
}

L <- list()
for (ii in seq_along(tables.new)) {
    tab <- tables.new[ii]
    cat(sprintf("[%d/%d] %s\n", ii, length(tables.new), tab))
    items <- irw::irw_itemtext(tab)
    z <- if ("item_text_translated" %in% names(items)) items$item_text_translated else items$item_text
    nw        <- lengths(strsplit(z, " "))
    nc        <- nchar(z)
    nc.option <- if ("option_text" %in% names(items)) nchar(items$option_text) else rep(NA_real_, length(z))
    instrument <- if ("instrument"  %in% names(items)) items$instrument        else rep(NA_character_, length(z))
    L[[tab]] <- data.frame(table = tab, instrument = instrument, item = items$item,
                           item_text = z, nw = nw, nc = nc, nc.option = nc.option)
}

save(L, file = file.path(here, "items_alltext.Rdata"))

rows      <- lapply(L, summarize_table)
merge.new <- do.call(rbind, rows)

## align columns: add FK_grade to existing if this is the first run with it
if (!"FK_grade" %in% names(existing)) existing$FK_grade <- NA_real_

df <- rbind(merge.new, existing[, names(merge.new)])
write.csv(df, file = file.path(here, "itemtext_metadata.csv"), quote = TRUE, row.names = FALSE)
