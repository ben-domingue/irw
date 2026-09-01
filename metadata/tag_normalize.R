##Normalisation for the two multi-select tag columns, applied AFTER the Google
##Sheet export and BEFORE tags.csv is written. See issue #1720.
##
##The Google Sheet is deliberately NOT modified. There is no service account
##(issue #1708 / 6.1), and read-side normalisation is idempotent -- it repairs
##rows entered years ago as well as rows entered tomorrow, and reverting is just
##deleting the call in 03_tags.R and re-running. The cost is that raters can
##keep typing the old value into the Sheet and this will silently absorb it;
##fix the Sheet itself once 6.1 lands.
##
##WHY THIS EXISTS. `sample` and `construct type` are multi-select, stored as one
##comma-joined string. One value -- "Internet-based (Mturkers, etc)" -- contains
##a comma, so it has to be quoted, and the quoting is inconsistent in the sheet
##(quoted on most rows, bare on four). That single fact produced three separate
##workarounds in three codebases:
##
##  Rpkg/R/filter.R                    34-line quote-aware parser + special case,
##                                     used by irw_tag_options() but NOT by
##                                     irw_filter(), which does a naive
##                                     strsplit(x, ",") -- so filtering on that
##                                     value silently matches nothing (~446 rows)
##  irw_site/_load-data-explore.qmd:63 swaps the comma for "~", splits, swaps back
##  Python-pkg .../filter.py:82        no workaround at all; simply broken
##
##Renaming the value to "Internet-based" removes the comma, which makes plain
##comma-splitting correct everywhere and lets all three workarounds be deleted.

##Canonical vocabularies. These are the ATOMS, derived by splitting every cell
##in the 2,435-row sheet -- not the joined strings (52 and 66 of those exist,
##but they are combinations, not values). Anything outside these lists is a
##typo or a new value that needs a deliberate decision, so it stops the run.
TAG_VOCAB <- list(
    "sample" = c(
        "Clinical", "Educational", "General/non-specific", "Internet-based",
        "NA", "Non-human", "Program-based", "Representative", "Targeted/specific"
    ),
    "construct type" = c(
        "Affective/mental health", "Behavioral", "Cognitive/educational",
        "Developmental", "NA", "Opinion/attitude", "Other", "Personality",
        "Physical health/functioning"
    )
)

##Renames applied to the whole cell before splitting, longest-first so a prefix
##never shadows a longer match. Fixed strings, not regex.
TAG_RENAMES <- c(
    "Internet-based (Mturkers, etc)" = "Internet-based"
)

##Repairs for atoms that are already corrupt in the exported data: the four
##bare rows split on the value's internal comma, yielding "Internet-based
##(Mturkers" plus a stray "etc)". Applied after splitting.
TAG_ATOM_REPAIRS <- c("Internet-based (Mturkers" = "Internet-based")
TAG_ATOM_DROP    <- c("etc)")

##`sample` holds two facets in one multi-select column (#1760, decided
##2026-09-01). SETTING answers "how were these people reached" and its values
##combine freely. FRAME answers "how broad was the sampling", and there
##`General/non-specific` is the catch-all: it is not used when one of the other
##two applies, so it never co-occurs with them.
##
##Enforced here, on the read side, for the same reason the renames above are:
##the Sheet is not writable from code (#1708 / 6.1), this is idempotent, and it
##repairs rows entered years ago as well as rows entered tomorrow. 181 of the
##2,480 rows in the sheet carry the contradiction today, across 13 studies --
##all of them human rows.
##
##SCOPE, deliberately narrow: only the frame atoms displace `General`. A setting
##atom does not, because it answers a different question -- "Educational,
##General/non-specific" means "recruited through a school, no restricted frame,
##no representativeness claim", which is a real statement and not a conflict.
##133 rows are of that shape and are left alone. Widening this to "any other
##atom displaces General" would leave `General/non-specific` meaning what a
##blank cell already means.
##
##`Representative` and `Targeted/specific` are independent and MAY co-occur: a
##nationally representative sample of teachers is both, and 49 rows say so.
##Never collapse them.
FRAME_RESIDUAL <- "General/non-specific"
FRAME_SPECIFIC <- c("Representative", "Targeted/specific")

##Drops the residual when a more specific frame value is present. Returns atoms
##unchanged for every column other than `sample`.
apply_frame_residual <- function(atoms, column) {
    if (!identical(column, "sample")) return(atoms)
    if (!FRAME_RESIDUAL %in% atoms) return(atoms)
    if (!any(FRAME_SPECIFIC %in% atoms)) return(atoms)
    atoms[atoms != FRAME_RESIDUAL]
}

normalize_multiselect <- function(x, column, vocab = TAG_VOCAB) {
    stopifnot(column %in% names(vocab))
    allowed <- vocab[[column]]

    out <- vapply(x, function(cell) {
        if (is.na(cell)) return(NA_character_)

        ##1. Drop literal quote characters. Most rows store the value as
        ##   "Internet-based (Mturkers, etc)" WITH quotes inside the field.
        cell <- gsub('"', "", cell, fixed = TRUE)

        ##2. Rename before splitting, while the comma-bearing value is intact.
        for (from in names(TAG_RENAMES)) {
            cell <- gsub(from, TAG_RENAMES[[from]], cell, fixed = TRUE)
        }

        ##3. Split, trim, repair already-corrupt atoms, drop the stray tail.
        atoms <- trimws(strsplit(cell, ",", fixed = TRUE)[[1]])
        atoms <- atoms[nzchar(atoms)]
        hit <- atoms %in% names(TAG_ATOM_REPAIRS)
        atoms[hit] <- TAG_ATOM_REPAIRS[atoms[hit]]
        atoms <- atoms[!atoms %in% TAG_ATOM_DROP]

        ##3b. `sample` only: drop the catch-all when a specific frame value is
        ##    present (#1760). Before the vocabulary check below, so the result
        ##    is what gets validated and published.
        atoms <- apply_frame_residual(atoms, column)

        if (!length(atoms)) return(NA_character_)

        ##4. Canonical order + dedupe, so one tag set has exactly one encoding.
        ##   749 rows currently store a set in more than one string form.
        paste(sort(unique(atoms)), collapse = ", ")
    }, character(1), USE.NAMES = FALSE)

    ##5. Refuse to publish an atom nobody has approved.
    seen <- unique(unlist(strsplit(out[!is.na(out)], ", ", fixed = TRUE)))
    bad  <- setdiff(seen, allowed)
    if (length(bad)) {
        stop(sprintf(
            "%s: %d value(s) outside the controlled vocabulary: %s\nAdd them to TAG_VOCAB in tag_normalize.R only after deciding they are real.",
            column, length(bad), paste0('"', bad, '"', collapse = ", ")))
    }
    out
}

##Applies the above to whichever of the multi-select columns are present.
normalize_tag_columns <- function(tag, vocab = TAG_VOCAB) {
    for (column in intersect(names(vocab), names(tag))) {
        tag[[column]] <- normalize_multiselect(tag[[column]], column, vocab)
    }
    tag
}
