## Flesch-Kincaid grade for a table's item text (ben-domingue/irw#3229).
##
## Shared by 08_itemtext.R (new tables) and hotfixes/fk_grade_per_item.R (the
## one-off back-fill). Published as itemtext_metadata.FK_grade.
##
## DEFINITION: the MEDIAN, over a table's items, of each item's own
## Flesch-Kincaid grade level, computed on English text only -- the original
## wording when the administration was English, the `*_translated` column when
## it was not. NA when there is no English text to score.
##
## Why per item. It used to be one score over the table's items pasted together
## as a single document. quanteda's sentence splitter does not break at ". "
## when the next item starts with a lower-case letter, so a word list became one
## "sentence" thousands of words long: `mturkddm_lexical`, whose items are
## single words, published a grade of 3,588.9, and 135 tables were above 20.
## Scoring each item as its own document cannot merge items, and the median is
## a typical item rather than a total.
##
## Why English only. The formula's constants are fitted to English syllable and
## sentence lengths; on Spanish or German text it returns a number that is not a
## grade level of anything. It had been computed for every language.
##
## What it is NOT: a validated readability measure for survey items, which are
## short and often not sentences. A one-word item scores near zero or below
## (monosyllables give about -3.4). Read it as a rough ordering of how wordy and
## polysyllabic a table's items are.
fk_grade <- function(texts) {
    texts <- trimws(as.character(texts))
    texts <- texts[!is.na(texts) & nzchar(texts)]
    if (length(texts) == 0) return(NA_real_)
    fk <- quanteda.textstats::textstat_readability(
        quanteda::corpus(texts), measure = "Flesch.Kincaid")$Flesch.Kincaid
    fk <- fk[is.finite(fk)]
    if (length(fk) == 0) return(NA_real_)
    stats::median(fk)
}

## Is this table's scored text English? `translated` = the table carries an
## English translation (item_text_translated), which is what gets scored.
## `language` = the table's administered language as itemtext_metadata records
## it (a semicolon list for a multi-language administration).
fk_text_is_english <- function(translated, language) {
    isTRUE(translated) || identical(trimws(as.character(language)), "English")
}
