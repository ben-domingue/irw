#!/usr/bin/env Rscript
##
## Validate every item text provenance.csv against the one vocabulary.
##
##   Rscript itemtext/check_provenance.R          # exit 1 if anything is off
##
## Why this exists. On 2026-09-02 a `translation_source` column was added twice,
## in two files, with two vocabularies: `official_instrument_english` /
## `study_supplied` / `machine_translation` / `mixed` in
## `language_backfill/backfill_provenance.csv` (#1815), and `published` / `ai`
## in `itemtables/batch_015/provenance.csv` (#1820). Same column, same concept,
## different values, neither aware of the other -- the exact shape of defect
## ARCHITECTURE.md's Rule 1 exists to prevent.
##
## So the values live in `provenance_vocab.csv` and nowhere else. SKILL.md and
## language_backfill/README.md describe when to reach for each, and point here
## for what they are. Rule 2: a vocabulary enforced by something that exits
## non-zero beats any number of paragraphs listing the allowed values -- which
## is how TAG_VOCAB in metadata/tag_normalize.R already works.
##
## It also reports which tables owe a public issues-page entry, because that is
## a property of the value: a machine_translation table needs one, per the
## 2026-09-02 ratification.

here <- dirname(sub("^--file=", "",
                    grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
if (!length(here) || is.na(here)) here <- "itemtext"

vocab_path <- file.path(here, "provenance_vocab.csv")
if (!file.exists(vocab_path)) stop("no provenance_vocab.csv beside this script")
vocab <- read.csv(vocab_path, stringsAsFactors = FALSE)

## Every provenance record, wherever it lives. The glob is deliberately wider
## than check_issues_page.R's `itemtables/batch_*/`: the language backfill's 78
## tables sit outside that pattern, which is why nothing noticed that 60 of
## them owed an issues-page entry.
files <- c(Sys.glob(file.path(here, "itemtables", "batch_*", "provenance.csv")),
           Sys.glob(file.path(here, "language_backfill", "*provenance.csv")))
files <- files[file.exists(files)]
if (!length(files)) stop("no provenance.csv found under ", here)

allowed <- vocab$value[vocab$field == "translation_source"]
bad <- list()
needs_note <- character(0)
n_rows <- 0L

for (f in files) {
    x <- read.csv(f, stringsAsFactors = FALSE, colClasses = "character")
    n_rows <- n_rows + nrow(x)
    if (!"translation_source" %in% names(x)) next
    vals <- ifelse(is.na(x$translation_source), "", trimws(x$translation_source))
    off  <- which(!vals %in% allowed)
    if (length(off))
        bad[[f]] <- sprintf("  %-44s %s", x$table[off], sQuote(vals[off]))
    needs_note <- c(needs_note, x$table[vals == "machine_translation"])
}

cat(sprintf("checked %d provenance rows in %d file(s)\n", n_rows, length(files)))

if (length(bad)) {
    cat("\nUNKNOWN translation_source values:\n")
    for (f in names(bad)) {
        cat(" ", f, "\n"); cat(bad[[f]], sep = "\n"); cat("\n")
    }
    cat("Allowed (from provenance_vocab.csv):",
        paste(sQuote(allowed[nzchar(allowed)]), collapse = ", "),
        "and empty.\n")
}

## A machine translation is IRW-generated content, so it is disclosed publicly.
page <- file.path(here, "..", "..", "irw_site", "itemtext_issues.qmd")
if (file.exists(page) && length(needs_note)) {
    txt <- paste(readLines(page, warn = FALSE), collapse = "\n")
    undisclosed <- needs_note[!vapply(needs_note, grepl, logical(1),
                                      x = txt, fixed = TRUE)]
    cat(sprintf("\nmachine_translation tables: %d, of which %d have no entry on the public issues page\n",
                length(needs_note), length(undisclosed)))
    if (length(undisclosed)) {
        cat("  ", paste(utils::head(undisclosed, 8), collapse = ", "),
            if (length(undisclosed) > 8) sprintf(" ... and %d more", length(undisclosed) - 8) else "",
            "\n", sep = "")
        cat("  Each ships English this project generated; the 2026-09-02 ruling is\n",
            "  that those carry a line on the issues page.\n", sep = "")
    }
} else {
    undisclosed <- character(0)
}

quit(status = if (length(bad) || length(undisclosed)) 1L else 0L)
