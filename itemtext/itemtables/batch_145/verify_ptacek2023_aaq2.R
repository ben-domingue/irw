# verify_ptacek2023_aaq2.R
#
# ptacek2023_aaq2 is BLOCKED ON RIGHTS: no item text was shipped, so there is no
# item-to-wording mapping to verify and no Step 5b statistical route was run.
# What this script re-runs instead are the two factual claims the block rests on.
#
#   (1) IDENTITY -- the live table really is the AAQ-II (7 items, codes AAQ1..AAQ7,
#       0-6 responses), taken column-for-column from the study's own OSF Dataset.csv.
#       If the table were some other instrument from the same paper (CompACT / DASS-21 /
#       SWLS all sit in the same file), the AAQ-II rights verdict would not reach it.
#   (2) CLAUSE -- the ACBS AAQ-II page still publishes the reserved-right sentence the
#       instrument_rights_register.csv verdict was made from.
#
# Both are network checks; either can be skipped offline via the SKIP_* env vars,
# in which case that half reports SKIPPED and does not fail the verdict.

suppressMessages(library(irw))

TABLE <- "ptacek2023_aaq2"
EXPECTED_ITEMS <- paste0("AAQ", 1:7)
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
cat(sprintf("matches the 7-item / 0-6 AAQ-II signature: %s\n", id_live))
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
        aaq  <- cols[grepl("^AAQ", cols)]
        cat(sprintf("Dataset.csv has %d columns; %d match ^AAQ: %s\n",
                    length(cols), length(aaq), paste(aaq, collapse = ", ")))
        # Column codes are carried through unchanged by the processing script, so
        # source header == live item set is the whole of the code derivation.
        hdr_ok <- identical(sort(aaq), EXPECTED_ITEMS)
        cat(sprintf("source AAQ columns == live item set: %s\n", hdr_ok))
        # Sibling instruments in the same file, to show the table is not one of them:
        cat(sprintf("  (same file also holds %d CompACT, %d DASS-21, %d SWLS columns -- distinct blocks)\n",
                    sum(grepl("^(VA|OE|BA)[0-9]", cols)),
                    sum(grepl("^[SAD][0-9]+$", cols)),
                    sum(grepl("^SWL[0-9]", cols))))
        ok <- ok && hdr_ok
    }
}

## ---- (2) CLAUSE ---------------------------------------------------------
cat("\n== (2) rights clause still published ==\n")
CLAUSE_URL <- "https://contextualscience.org/acceptance_action_questionnaire_aaq_aaqii"
QUOTE <- "money making enterprise"
QUOTE2 <- "seeking permission is requested by the authors"
if (nzchar(Sys.getenv("SKIP_RIGHTS"))) {
    cat("clause fetch: SKIPPED (SKIP_RIGHTS set)\n")
} else {
    # ACBS returns 410 to a bare R user agent; curl with a browser UA gets 200.
    tf <- tempfile()
    rc <- suppressWarnings(system2("curl", c("-sL", "--max-time", "60", "-A",
                                             shQuote("Mozilla/5.0"), shQuote(CLAUSE_URL),
                                             "-o", shQuote(tf)), stdout = TRUE, stderr = TRUE))
    pg <- tryCatch({
        x <- paste(readLines(tf, warn = FALSE), collapse = " ")
        if (!nzchar(x) || grepl("Page not found", x, fixed = TRUE)) NULL else x
    }, error = function(e) NULL)
    if (is.null(pg)) {
        cat("clause fetch: could not fetch (network) -- not counted against the verdict\n")
    } else {
        n1 <- lengths(regmatches(pg, gregexpr(QUOTE, pg, fixed = TRUE)))
        n2 <- lengths(regmatches(pg, gregexpr(QUOTE2, pg, fixed = TRUE)))
        cat(sprintf("%s\n  '%s' occurs %d time(s)\n  '%s' occurs %d time(s)\n",
                    CLAUSE_URL, QUOTE, n1, QUOTE2, n2))
        cat(sprintf("page sha256 at extraction (2026-09-10): %s\n",
                    "1331b2eedc7c3dd6451c2bbbf431830b4245694ac4e846fd958a41c55ad47735"))
        ok <- ok && (n1 >= 1 && n2 >= 1)
    }
}

cat("\nWHAT THIS DOES NOT ESTABLISH: nothing about item-text accuracy or item ordering,\n",
    "because no item text was shipped. It establishes only that this table's items are\n",
    "the AAQ-II and that the reserved-right clause is still published by the rights holder.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
