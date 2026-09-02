# Usage: Rscript draft_issues_qmd.R <batch_dir> [<batch_dir> ...] [-o <outfile>]
#
# Turns the structured provenance recorded per batch into draft YAML issue entries
# for the public item-text issues page (itemtext_issues.qmd in the datapages/irw
# repo, checked out locally at ../../irw_site/itemtext_issues.qmd -- note it is a
# sibling of src/, NOT ../irw_site/).
#
# This script only DRAFTS. Since 2026-08-18 the agent applies the edit to that
# page directly (SKILL.md Step 6c); the draft is a starting point whose wording
# is meant to be rewritten, not pasted.
#
# Two things this script cannot see, both of which have cost real callouts:
#   1. Blocked tables write no CSV but still have a provenance row with empty
#      fields, which templated into "the origin of the item text was not
#      recorded" -- nonsense for a table that shipped no text. Such rows are now
#      skipped: a table earns a callout only if its __items.csv exists.
#   2. A caveat recorded ONLY in notes.csv, with no public_note and clean
#      structured fields, produces no draft at all. Three batch_009 tables were
#      missed that way. Every shipped table with no draft is now listed in a
#      REVIEW section at the end of the output with its full note, so the
#      triager reads it and decides rather than trusting the draft set to be
#      complete.
#
# Input: each batch dir's provenance.csv, with columns
#   table, mapping_basis, text_source, source_ref, note
# and optionally `public_note` -- a hand-written one-sentence caveat that, when
# present, is used verbatim instead of the generated sentence.
#
# A table earns a callout when its provenance says the item text is not a
# direct, verified transcript of what this study's participants actually saw:
#   mapping_basis in {paper_order, reconstructed, unknown}  -- code-to-text
#     alignment rests on an assumption rather than an explicit mapping
#   text_source  in {canonical_instrument, translated_substitute, unknown}
#     -- the words came from somewhere other than this study's own materials
# Tables that are data_labels + study_materials need no caveat: the source data
# file itself ties each item code to its text.

args <- commandArgs(trailingOnly = TRUE)
if (!length(args)) stop("Usage: Rscript draft_issues_qmd.R <batch_dir> [...] [-o <outfile>]")

out_path <- "fixes/itemtext_issues_draft.md"
if ("-o" %in% args) {
    i <- which(args == "-o")
    out_path <- args[i + 1]
    args <- args[-c(i, i + 1)]
}
batch_dirs <- sub("/$", "", args)

FLAG_MAPPING <- c("paper_order", "reconstructed", "unknown")
FLAG_TEXT    <- c("canonical_instrument", "translated_substitute", "unknown")

sentence_for <- function(r) {
    if (!is.null(r$public_note) && !is.na(r$public_note) && nzchar(trimws(r$public_note))) {
        return(trimws(r$public_note))
    }
    parts <- character(0)
    parts <- c(parts, switch(r$text_source,
        # Do NOT assume the instrument's native language is English: xue_2025_*
        # and zhou_2016_* administered natively-Chinese instruments and what
        # ships is an English rendering, so "the published original-language
        # instrument" was false for them. Say only what is always true of this
        # value -- the shipped text is not the administered wording.
        translated_substitute = paste("the item text here is not the wording respondents read:",
                                       "the study was administered in another language and only an",
                                       "English version of the instrument could be recovered"),
        canonical_instrument  = paste("item text comes from the published original instrument",
                                       "rather than this study's own materials"),
        unknown               = "the origin of the item text was not recorded during extraction",
        NULL))
    parts <- c(parts, switch(r$mapping_basis,
        paper_order   = paste("the item-to-text alignment is inferred from the order items appear",
                               "in the source, not from an explicit code-to-text mapping"),
        reconstructed = paste("the item-to-text alignment was reconstructed rather than read from",
                               "an explicit mapping"),
        unknown       = "the basis for the item-to-text alignment was not recorded",
        NULL))
    if (!length(parts)) return(NA_character_)
    s <- paste(parts, collapse = "; ")
    paste0(toupper(substring(s, 1, 1)), substring(s, 2))
}

rows <- list()
undrafted <- list()
blocked <- list()
for (d in batch_dirs) {
    p <- file.path(d, "provenance.csv")
    if (!file.exists(p)) {
        message("skipping ", d, " -- no provenance.csv")
        next
    }
    prov <- read.csv(p, stringsAsFactors = FALSE)
    notes_path <- file.path(d, "notes.csv")
    notes <- if (file.exists(notes_path)) read.csv(notes_path, stringsAsFactors = FALSE) else NULL
    for (i in seq_len(nrow(prov))) {
        r <- as.list(prov[i, ])
        # A blocked table wrote no CSV, so it has nothing to warn the public about.
        # Careful: a CSV is ALSO absent once a table has been uploaded and promoted
        # out of the batch folder, and those very much do need callouts -- tell the
        # two apart by provenance's `uploaded` stamp, not by the file alone.
        shipped <- file.exists(file.path(d, paste0(r$table, "__items.csv"))) ||
            (!is.null(r$uploaded) && !is.na(r$uploaded) && nzchar(trimws(r$uploaded)))
        if (!shipped) {
            blocked[[length(blocked) + 1]] <- r$table
            next
        }
        # A hand-written public_note always earns a callout, even when the
        # structured fields look clean: some caveats are orthogonal to
        # provenance (e.g. aguirre_camacho_2021_champion, whose item text is
        # correctly sourced but whose scale anchors are in a different
        # language than its items).
        has_public_note <- !is.null(r$public_note) && !is.na(r$public_note) &&
            nzchar(trimws(r$public_note))
        if (!has_public_note &&
            !(r$mapping_basis %in% FLAG_MAPPING || r$text_source %in% FLAG_TEXT)) {
            nt <- if (!is.null(notes) && r$table %in% notes$table)
                paste(notes$note[notes$table == r$table], collapse = " | ") else ""
            undrafted[[length(undrafted) + 1]] <- list(table = r$table, batch = basename(d), note = nt)
            next
        }
        r$batch <- basename(d)
        r$sentence <- sentence_for(r)
        if (is.na(r$sentence)) next
        rows[[length(rows) + 1]] <- r
    }
}

if (!length(rows) && !length(undrafted)) {
    cat("Nothing to draft or review across:", paste(batch_dirs, collapse = ", "), "\n")
    quit(save = "no")
}

dir.create(dirname(out_path), showWarnings = FALSE, recursive = TRUE)
con <- file(out_path, "w")
writeLines(c(
    sprintf("# Draft `itemtext_issues.qmd` additions -- generated %s", format(Sys.Date())),
    "",
    "Draft only -- nothing here has been pasted into the live page",
    "(`../../irw_site/itemtext_issues.qmd`, datapages/irw repo). Generated by",
    "`draft_issues_qmd.R` from each batch's `provenance.csv`. Review the wording",
    "before pasting: the sentences below are templated from structured provenance",
    "fields and are deliberately conservative, so some will read as more alarming",
    "than the underlying situation warrants.",
    "",
    "The page is one YAML `issues` list inside an R `yaml.load(r\"---( ... )---\")`",
    "block, rendered as a searchable table -- append the entries below before the",
    "closing `)---\")` and re-check that the YAML parses. Order does not matter; the",
    "page sorts by table name. A table whose `uploaded` stamp is still blank gets no",
    "entry until it ships, and `check_issues_page.R` will re-report it once it does.",
    "",
    sprintf("Source batches: %s", paste(batch_dirs, collapse = ", ")),
    ""), con)

for (r in rows) {
    writeLines(c(
        sprintf("## `%s` (%s)", r$table, r$batch),
        "",
        sprintf("<!-- mapping_basis=%s text_source=%s%s -->",
                r$mapping_basis, r$text_source,
                if (nzchar(trimws(r$source_ref))) paste0(" source=", trimws(r$source_ref)) else ""),
        sprintf("<!-- full note: %s -->", gsub("-->", "--&gt;", r$note)),
        "",
        "```yaml",
        sprintf("- table: %s", r$table),
        "  issue: |-",
        paste0("    ", gsub("[\r\n]+", " ", r$sentence)),
        "```",
        ""), con)
}
if (length(undrafted)) {
    writeLines(c(
        "---",
        "",
        "## REVIEW THESE TOO -- no draft generated",
        "",
        "These tables shipped but earned no draft callout: their provenance carries no",
        "`public_note` and its structured fields look clean. That is NOT the same as",
        "having no caveat -- this script cannot see anything recorded only in",
        "`notes.csv`, and three batch_009 tables were missed exactly that way. Read each",
        "note below and decide; if it warrants a callout, write one by hand.",
        ""), con)
    for (u in undrafted) {
        writeLines(c(
            sprintf("- **`%s`** (%s)", u$table, u$batch),
            if (nzchar(u$note)) paste0("    - ", gsub("[\r\n]+", " ", u$note))
            else "    - (no notes.csv entry either)",
            ""), con)
    }
}

if (length(blocked)) {
    writeLines(c(
        "---",
        "",
        sprintf("Skipped %d table%s with a provenance row but no shipped CSV (blocked at",
                length(blocked), if (length(blocked) == 1L) "" else "s"),
        sprintf("extraction): %s", paste(sprintf("`%s`", unlist(blocked)), collapse = ", ")),
        ""), con)
}

close(con)

cat(sprintf("Wrote %d draft entr%s to %s\n", length(rows),
            if (length(rows) == 1L) "y" else "ies", out_path))
if (length(undrafted))
    cat(sprintf("  plus %d shipped table%s with no draft -- READ the REVIEW section\n",
                length(undrafted), if (length(undrafted) == 1L) "" else "s"))
if (length(blocked))
    cat(sprintf("  skipped %d blocked table%s (nothing shipped)\n",
                length(blocked), if (length(blocked) == 1L) "" else "s"))
