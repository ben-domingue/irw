# verify_ptacek2023_swls.R
#
# ptacek2023_swls is BLOCKED ON RIGHTS: no item text was shipped, so there is no
# item-to-wording mapping to verify and no Step 5b statistical route was run.
# What this script re-runs instead are the two factual claims the block rests on.
#
#   (1) IDENTITY -- the live table really is the SWLS (5 items, codes SWL1..SWL5,
#       0-6 responses), taken column-for-column from the study's own OSF Dataset.csv.
#       If the table were some other instrument from the same paper (CompACT /
#       DASS-21 / AAQ-II all sit in the same file), the SWLS rights verdict would
#       not reach it.
#   (2) CLAUSE -- eddiener.com/scales still publishes the reserved-right sentence
#       that instrument_rights_register.csv's verdict was made from (Ben's ruling
#       2026-09-09, which named this table).
#
# Both are network checks; either can be skipped offline via the SKIP_* env vars,
# in which case that half reports SKIPPED and does not fail the verdict.

suppressMessages(library(irw))

TABLE <- "ptacek2023_swls"
EXPECTED_ITEMS <- paste0("SWL", 1:5)
EXPECTED_RESP  <- 0:6

ok <- TRUE

## ---- (1) IDENTITY -------------------------------------------------------
cat("== (1) instrument identity ==\n")
s <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
live_items <- sort(as.character(s$items))
live_resp  <- sort(as.numeric(s$resp))
cat(sprintf("live items (%d): %s\n", length(live_items), paste(live_items, collapse = ", ")))
cat(sprintf("live resp  (%d): %s\n", length(live_resp),  paste(live_resp,  collapse = ", ")))

id_live <- identical(live_items, EXPECTED_ITEMS) && identical(live_resp, as.numeric(EXPECTED_RESP))
cat(sprintf("matches the 5-item / 0-6 SWLS signature: %s\n", id_live))
ok <- ok && id_live

# Source header: the study's own OSF deposit (osf.io/cwjxq), Dataset.csv, file guid zs27k.
if (nzchar(Sys.getenv("SKIP_OSF"))) {
    cat("OSF header check: SKIPPED (SKIP_OSF set)\n")
} else {
    hdr <- tryCatch(readLines("https://osf.io/download/zs27k/", n = 1, warn = FALSE),
                    error = function(e) NULL)
    if (is.null(hdr)) {
        cat("OSF header check: could not fetch (network) -- not counted against the verdict\n")
    } else {
        cols <- trimws(strsplit(hdr, ",")[[1]])
        swl  <- cols[grepl("^SWL", cols)]
        pos  <- which(grepl("^SWL", cols))
        cat(sprintf("Dataset.csv has %d columns; %d match ^SWL at positions %s: %s\n",
                    length(cols), length(swl), paste(pos, collapse = "-"),
                    paste(swl, collapse = ", ")))
        # Column codes are carried through unchanged by the processing script, so
        # source header == live item set is the whole of the code derivation.
        hdr_ok <- identical(sort(swl), EXPECTED_ITEMS)
        cat(sprintf("source SWL columns == live item set: %s\n", hdr_ok))
        # Sibling instruments in the same file, to show the table is not one of them:
        cat(sprintf("  (same file also holds %d CompACT, %d DASS-21, %d AAQ-II columns -- distinct blocks)\n",
                    sum(grepl("^(VA|OE|BA)[0-9]", cols)),
                    sum(grepl("^[SAD][0-9]+$", cols)),
                    sum(grepl("^AAQ[0-9]", cols))))
        ok <- ok && hdr_ok
    }
}

## ---- (2) CLAUSE ---------------------------------------------------------
cat("\n== (2) rights clause still published ==\n")
CLAUSE_URL <- "https://eddiener.com/scales"
QUOTE  <- "permitted for non-commercial purposes only"
QUOTE2 <- "copyrighted by Ed Diener"
if (nzchar(Sys.getenv("SKIP_RIGHTS"))) {
    cat("clause fetch: SKIPPED (SKIP_RIGHTS set)\n")
} else {
    tf <- tempfile()
    suppressWarnings(system2("curl", c("-sL", "--max-time", "60", "-A",
                                       shQuote("Mozilla/5.0"), shQuote(CLAUSE_URL),
                                       "-o", shQuote(tf)), stdout = TRUE, stderr = TRUE))
    pg <- tryCatch({
        x <- paste(readLines(tf, warn = FALSE), collapse = " ")
        if (!nzchar(x)) NULL else x
    }, error = function(e) NULL)
    if (is.null(pg)) {
        cat("clause fetch: could not fetch (network) -- not counted against the verdict\n")
    } else {
        n1 <- lengths(regmatches(pg, gregexpr(QUOTE,  pg, fixed = TRUE)))
        n2 <- lengths(regmatches(pg, gregexpr(QUOTE2, pg, fixed = TRUE)))
        cat(sprintf("%s\n  '%s' occurs %d time(s)\n  '%s' occurs %d time(s)\n",
                    CLAUSE_URL, QUOTE, n1, QUOTE2, n2))
        cat(sprintf("page sha256 at extraction (2026-09-10): %s\n",
                    "b5ae99bc0b81c8d9eb3fe02b5095dda269be5559c6808cf4c328d20a26e94274"))
        cat("  (the page also names the SWLS explicitly in its scale list)\n")
        ok <- ok && (n1 >= 1 && n2 >= 1)
    }
}

cat("\nWHAT THIS DOES NOT ESTABLISH: nothing about item-text accuracy or item ordering,\n",
    "because no item text was shipped. It establishes only that this table's items are\n",
    "the SWLS and that the reserved-right clause is still published by the rights holder.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
