##Tags: one hand-annotated Google Sheet per source.
##
##Mirrors the per-source `dbs` structure 02_biblio.R already uses. `core` is the
##long-standing "IRW Tags" sheet; `nom` was added for issue #1689, which found
##the non-core branches had nowhere to record tags. `comp` and `sim` are
##deliberately absent -- see Rpkg/inst/developer/tags.md for why.

library(gsheet)

##Multi-select normalisation for `sample` and `construct type`, applied after
##the sheet export and before write_csv. See tag_normalize.R and issue #1720.
##The Google Sheet itself is deliberately not modified.
source("tag_normalize.R")

##Columns kept, by POSITION, from the 13-column sheet:
##  1 table, 6:12 Age Range .. Primary Language(s), 3 Construct Name
##
##DO NOT "tidy" this into a by-name selection without reading the note below.
##Column 4 ("Context Text") is omitted on purpose: it holds verbatim excerpts
##from source papers, and this positional selection is the only thing keeping
##that raw text out of the public CSVs. Reordering the sheet silently changes
##what gets published. See .claude/skills/irw-site-update/SKILL.md.
KEEP_COLS <- c(1, 6:12, 3)

##Row 1 of every tags sheet is a template/instruction row, not data, and is
##dropped. Verify rather than assume: a sheet missing this row would otherwise
##lose its first real table without any error.
INSTRUCTION_SENTINEL <- "should match what is on redivis"

get_tags <- function(db) {
    tag <- gsheet2tbl(db$url)

    if (ncol(tag) < max(KEEP_COLS)) {
        stop(db$name, ": expected at least ", max(KEEP_COLS),
             " columns, found ", ncol(tag),
             ". Sheet layout changed -- re-check KEEP_COLS before proceeding.")
    }

    first <- trimws(as.character(tag[[1]][1]))
    if (is.na(first) || !identical(tolower(first), INSTRUCTION_SENTINEL)) {
        stop(db$name, ": expected the instruction row ('", INSTRUCTION_SENTINEL,
             "') directly under the header, found '", first,
             "'. Refusing to drop row 1 -- it looks like real data.")
    }

    ##Everything below this line reproduces the original core-only script's
    ##behaviour exactly; do not "fix" it here without regenerating and
    ##reviewing tags.csv, which feeds the public Redivis table.
    tag <- tag[-1, KEEP_COLS]
    names(tag) <- tolower(names(tag))
    tag$table <- tolower(tag$table)

    tag <- tag[!is.na(tag$table), ]
    ##Rows naming a table but carrying no tags are counted, not dropped --
    ##long-standing behaviour, and the count is the useful signal here.
    n <- apply(tag[, -1], 1, function(x) sum(!is.na(x)))
    print(paste0(db$name, ": ", nrow(tag), " rows -> ", db$file.out,
                 " (", sum(n == 0), " named but untagged)"))

    ##Normalise the multi-select columns before writing. Fails loudly on any
    ##atom outside the controlled vocabulary rather than publishing it.
    tag <- normalize_tag_columns(tag)

    readr::write_csv(tag, db$file.out)
    invisible(tag)
}

dbs <- list(
    core = list(name = "core",
                url = 'https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123',
                file.out = "tags.csv"),
    nom  = list(name = "nom",
                url = 'https://docs.google.com/spreadsheets/d/1v3toO6OPts_HIjcjHTOb9_v2Ne2oXZSTkGTeO6fUyrg/edit?gid=126134123#gid=126134123',
                file.out = "nominal_tags.csv")
)

for (i in seq_along(dbs)) {
    get_tags(dbs[[i]])
}
