# verify_malik_2018_social_motivation.R
#
# CLAIM UNDER TEST. data/malik_2018_physician_motivation.py assigns the IRW item
# codes POSITIONALLY:
#     sc_cols <- c("SC1","SC2","CS4", "SC5".."SC15")   # 14 columns
#     social_<i> <- sc_cols[i]
# so social_3 is the S1 .sav column "CS4" ("I am satisfied with the team work
# around me during work") and NOT "SC3" ("I am satisfied with my personal life
# issues"), which the script's own comment wrongly claims are the same variable.
# Both columns exist in the .sav; SC3 is simply absent from the IRW table.
# item_text was taken from the .sav variable labels, so this is the check that
# would break if any two labels were swapped.
#
# METHOD. Re-derive each source column's full 1..5 response-count vector from
# the S1 .sav (applying the script's own filters: integer-valued, in 1..5) and
# compare it cell-for-cell with the live per-item counts. Count vectors, not
# means -- a permutation of any two items breaks this immediately.

suppressMessages(library(irw))

TABLE  <- "malik_2018_social_motivation"
SAV    <- file.path("../../.cache", TABLE, "malik_2018.sav")   # from itemtables/batch_094/
if (!file.exists(SAV)) SAV <- file.path(".cache", TABLE, "malik_2018.sav")
URL    <- "https://doi.org/10.1371/journal.pone.0209546.s001"

# Source columns in the exact order the processing script consumes them.
SRC <- c("SC1", "SC2", "CS4", paste0("SC", 5:15))
ITEMS <- paste0("social_", seq_along(SRC))

if (!file.exists(SAV)) {
    dir.create(dirname(SAV), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(URL, SAV, mode = "wb", quiet = TRUE)
}
if (!requireNamespace("haven", quietly = TRUE))
    stop("need haven to read the S1 .sav")
sav <- haven::read_sav(SAV)

src_counts <- function(col) {
    v <- suppressWarnings(as.numeric(sav[[col]]))
    v <- v[!is.na(v) & v %% 1 == 0 & v >= 1 & v <= 5]
    as.integer(table(factor(v, levels = 1:5)))
}

d <- irw::irw_fetch(TABLE)
live_counts <- function(it) {
    v <- as.numeric(d$resp[d$item == it])
    as.integer(table(factor(v, levels = 1:5)))
}

cat(sprintf("%-11s %-5s %-22s %-22s %s\n",
            "item", "src", "sav counts (1..5)", "live counts (1..5)", "match"))
ok <- TRUE
for (i in seq_along(ITEMS)) {
    a <- src_counts(SRC[i]); b <- live_counts(ITEMS[i])
    m <- identical(a, b); ok <- ok && m
    cat(sprintf("%-11s %-5s %-22s %-22s %s\n", ITEMS[i], SRC[i],
                paste(a, collapse = "/"), paste(b, collapse = "/"),
                if (m) "OK" else "MISMATCH"))
}

# The falsifiable part: SC3 vs CS4 for social_3.
a3 <- src_counts("SC3"); c4 <- src_counts("CS4"); l3 <- live_counts("social_3")
cat(sprintf("\nsocial_3 discriminant -- SC3 %s | CS4 %s | live %s -> %s\n",
            paste(a3, collapse = "/"), paste(c4, collapse = "/"),
            paste(l3, collapse = "/"),
            if (identical(l3, c4) && !identical(l3, a3)) "CS4 (as shipped)" else "AMBIGUOUS/WRONG"))

# Are the 14 count vectors mutually distinct? If so the match is a permutation
# proof, not a coincidence.
vecs <- vapply(SRC, function(x) paste(src_counts(x), collapse = "/"), "")
cat(sprintf("distinct source count vectors: %d of %d\n",
            length(unique(vecs)), length(vecs)))

cat("Note: this establishes item_text<->item for all 14 items and the option_text<->resp\n",
    "direction only insofar as the counts are level-wise identical (they are, so any\n",
    "permutation of the 1..5 anchors would show up here too). It does NOT establish that\n",
    "the .sav's own value labels are themselves correctly oriented -- that is taken from\n",
    "the file at face value.\n", sep = "")

cat(if (ok && identical(l3, c4) && !identical(l3, a3) &&
        length(unique(vecs)) == length(vecs)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
