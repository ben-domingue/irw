## One-time full recompute of itemtext_metadata.csv for ALL tables.
## Run this when adding FK_grade or other new columns to the schema,
## then switch back to 08_itemtext.R for incremental updates.
## Requires: quanteda, quanteda.textstats

library(quanteda)
library(quanteda.textstats)

script_path <- grep("--file=", commandArgs(FALSE), value = TRUE)
here <- if (length(script_path)) dirname(normalizePath(sub("--file=", "", script_path[1]))) else getwd()

lt <- irw::irw_list_itemtext_tables()

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
for (ii in seq_along(lt)) {
    tab <- lt[ii]
    cat(sprintf("[%d/%d] %s\n", ii, length(lt), tab))
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

rows <- lapply(L, summarize_table)
df   <- do.call(rbind, rows)

write.csv(df, file = file.path(here, "itemtext_metadata.csv"), quote = TRUE, row.names = FALSE)
