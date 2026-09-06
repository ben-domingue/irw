# verify_evpromisi_stone_2021_ddpainin.R
#
# NOTE: this table was BLOCKED on rights (HealthMeasures/PROMIS Terms of Use bar
# redistribution of PROMIS instruments) and NO __items.csv was shipped. This script
# records the mapping check that had already been completed, so the verdict does not
# have to be rebuilt if the rights question is ever resolved in favour of shipping.
#
# CLAIM being verified: each live item code DDPAININ03/08/09/10/14/20 carries the
# item stem the study's own codebooks give for that same code, and resp 1..5 is the
# codebook's 1=Not at all .. 5=Very much coding, unpermuted.
#
# FALSIFIABLE PREDICTION: the IRW table is a straight per-column melt of the two
# daily-diary SAS files in Harvard Dataverse doi:10.7910/DVN/G4E2SR (community and
# osteoarthritis samples). So for EVERY item and EVERY response level, the count of
# that level in the raw column named by the item code must equal the count in the
# live table for that item within that sample group. If item_text for any two items
# were swapped, or if the resp ladder were reversed, the count vectors would no
# longer line up -- all six items have distinct count vectors within each group.

suppressMessages(library(irw))
suppressMessages(library(haven))

TABLE <- "evpromisi_stone_2021_ddpainin"
ITEMS <- c("DDPAININ03","DDPAININ08","DDPAININ09","DDPAININ10","DDPAININ14","DDPAININ20")
LEVELS <- 1:5

# Dataverse file ids: community-sample daily file, osteoarthritis-sample daily file.
FILES <- c(CS = 4807827, OA = 4807813)
cache <- file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)

raw_counts <- list()
for (g in names(FILES)) {
    fp <- file.path(cache, sprintf("daily_%s.sas7bdat", tolower(g)))
    if (!file.exists(fp))
        download.file(sprintf("https://dataverse.harvard.edu/api/access/datafile/%d", FILES[[g]]),
                      fp, quiet = TRUE, mode = "wb")
    r <- haven::read_sas(fp)
    raw_counts[[g]] <- t(sapply(ITEMS, function(it)
        sapply(LEVELS, function(k) sum(r[[it]] == k, na.rm = TRUE))))
}

d <- irw::irw_fetch(TABLE)
mismatch <- 0L
for (g in names(FILES)) {
    live <- t(sapply(ITEMS, function(it)
        sapply(LEVELS, function(k) sum(d$item == it & d$resp == k & d$group == g, na.rm = TRUE))))
    cat("=== group", g, "(raw Dataverse counts vs live IRW counts, levels 1..5)\n")
    for (i in seq_along(ITEMS)) {
        rc <- raw_counts[[g]][i, ]; lc <- live[i, ]
        cat(sprintf("%-11s raw %-28s live %-28s %s\n", ITEMS[i],
                    paste(rc, collapse = " "), paste(lc, collapse = " "),
                    if (all(rc == lc)) "match" else "MISMATCH"))
        mismatch <- mismatch + sum(rc != lc)
    }
    # the vectors must also be mutually distinct, or matching would prove nothing
    keys <- apply(raw_counts[[g]], 1, paste, collapse = "-")
    cat(sprintf("distinct count vectors within group: %d of %d\n\n", length(unique(keys)), length(ITEMS)))
}
cat(sprintf("total mismatched cells: %d of %d\n", mismatch, 2 * length(ITEMS) * length(LEVELS)))
cat("Does NOT establish: the fidelity of the transcribed wording itself (single source,\n",
    "the study codebooks), nor the hernia-surgery sample, which the deposit contains but\n",
    "the IRW table does not include.\n", sep = "")
cat(if (mismatch == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
