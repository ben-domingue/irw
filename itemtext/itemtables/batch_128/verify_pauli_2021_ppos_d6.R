# verify_pauli_2021_ppos_d6.R -- batch_128, 2026-09-09
#
# THIS TABLE SHIPPED NO ITEM TEXT. It is BLOCKED on instrument rights
# (itemtext/instrument_rights_register.csv, row "Patient-Practitioner Orientation
# Scale (PPOS, 18-item; incl. PPOS-D12/D6 translations)", verdict = block), so
# there is no item_text <-> item mapping to re-run: mapping_basis = unknown,
# Step 5b status = NO_ROUTE.
#
# What this script re-runs is the two claims the round actually made:
#
#   (A) IDENTITY / CODE DERIVATION -- that pauli_2021_ppos_d6 really is the six
#       German PPOS-D6 items of Pauli & Wilhelmy (2021), and that ppos1..ppos6
#       are the source workbook's v1.1..v1.6 in order. data/pauli_2021_ppos_d6.py
#       renames those columns POSITIONALLY, so the falsifiable prediction is that
#       each live item's n equals the count of non-sentinel (!= -99) values in the
#       corresponding workbook column: 328, 330, 331, 331, 331, 322.
#       Read from irw::irw_table_sets(), NOT irw_fetch() -- server-side aggregates,
#       no export against the 200GB/30-day quota.
#
#   (B) RIGHTS -- that the El Centro Measures Library PPOS page still carries the
#       permission-required clause the block rests on, byte-identical to the copy
#       hashed into the register.
#
#   VERDICT: PASS = identity reproduces AND the clause is still there; block stands.
#   VERDICT: FAIL = either check did not reproduce; a human should look before this
#                   table is re-queued or the block is relied on again.
#
# What this does NOT establish: nothing about item_text, because none was shipped.
# And the n-vector pins the six-column block and its two endpoints (328 -> ppos1,
# 322 -> ppos6); the three middle items tie at 331, so this route alone would not
# separate ppos3/ppos4/ppos5 from each other. That would only matter if the table
# were ever unblocked and extracted.

suppressMessages(library(irw))

TABLE    <- "pauli_2021_ppos_d6"
ZIP_URL  <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8667738/supplementaryFiles"
XLSX     <- "peerj-09-12604-s003.xlsx"
XLSX_SHA <- "c65863c0ae916c5968482d95f2e2312b58c70f1b20a5284aeb1f6f1875d614ca"
SHEET    <- "PPOS-D6 raw dataset2"
SRC_COLS <- paste0("v1.", 1:6)
ITEMS    <- paste0("ppos", 1:6)
EXPECT_N <- c(328, 330, 331, 331, 331, 322)   # as read 2026-09-09

RIGHTS_URL <- "https://elcentro.sonhs.miami.edu/research/measures-library/ppos/index.html"
RIGHTS_SHA <- "576df50afb0cb53a1c52f17ec1a6d24229546aa361a06e48702c3087697168b5"
CLAUSE     <- "copyrighted so please contact the author for permission to use the scale"

UA <- "Mozilla/5.0 (X11; Linux x86_64)"
ok_identity <- FALSE
ok_rights   <- FALSE

cat(sprintf("table : %s\n\n", TABLE))

## ------------------------------------------------- (A) identity / code derivation
cat("== (A) live per-item n vs the source workbook's v1.1..v1.6 ==\n")

live_n <- tryCatch({
    s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
    pi <- as.data.frame(s$per_item)
    ncol_n <- intersect(c("n", "n_resp", "count"), names(pi))[1]
    setNames(as.numeric(pi[[ncol_n]]), as.character(pi$item))[ITEMS]
}, error = function(e) { cat("irw_table_sets error: ", conditionMessage(e), "\n", sep = ""); NULL })

src_n <- tryCatch({
    zf <- tempfile(fileext = ".zip")
    # Europe PMC's supplementaryFiles endpoint 500s for download.file()'s request
    # shape; curl -L with a plain UA works, so shell out.
    system2("curl", c("-sSL", "-A", shQuote(UA), "-o", shQuote(zf), shQuote(ZIP_URL)))
    if (!file.exists(zf) || file.size(zf) < 10000) stop("supplementary zip fetch failed")
    ex <- tempfile(); dir.create(ex)
    # R's internal unzip chokes on this archive; the system unzip handles it.
    system2("unzip", c("-o", "-q", shQuote(zf), shQuote(XLSX), "-d", shQuote(ex)))
    xp <- file.path(ex, XLSX)
    if (requireNamespace("digest", quietly = TRUE))
        cat(sprintf("workbook sha256  : %s  (%s)\n",
                    digest::digest(file = xp, algo = "sha256"),
                    if (identical(digest::digest(file = xp, algo = "sha256"), XLSX_SHA))
                        "byte-identical to the copy read on 2026-09-09"
                    else "DIFFERS from the recorded copy"))
    if (!requireNamespace("readxl", quietly = TRUE)) stop("package 'readxl' not available")
    d <- as.data.frame(readxl::read_excel(xp, sheet = SHEET))
    vapply(SRC_COLS, function(cc) sum(!is.na(d[[cc]]) & d[[cc]] != -99), numeric(1))
}, error = function(e) { cat("source fetch error: ", conditionMessage(e), "\n", sep = ""); NULL })

if (is.null(live_n) || is.null(src_n)) {
    cat("could not obtain both sides; identity NOT re-confirmed this run\n")
} else {
    cat(sprintf("\n%-8s %-8s %10s %10s %8s\n", "live", "source", "live n", "source n", "diff"))
    for (i in seq_along(ITEMS))
        cat(sprintf("%-8s %-8s %10.0f %10.0f %8.0f\n",
                    ITEMS[i], SRC_COLS[i], live_n[i], src_n[i], live_n[i] - src_n[i]))
    cat(sprintf("\nexpected n vector (2026-09-09): %s\n", paste(EXPECT_N, collapse = " ")))
    ok_identity <- all(live_n == src_n) && all(live_n == EXPECT_N)
    cat(sprintf("=> positional rename v1.i -> ppos{i} reproduces item for item: %s\n",
                if (ok_identity) "YES" else "NO"))
}

## ------------------------------------------------------------------ (B) rights
cat("\n== (B) rights clause still on the holder-linked page ==\n")
ht <- tempfile(fileext = ".html")
got <- tryCatch({
    utils::download.file(RIGHTS_URL, ht, quiet = TRUE, mode = "wb",
                         headers = c("User-Agent" = UA))
    file.exists(ht) && file.size(ht) > 10000
}, error = function(e) { cat("fetch error: ", conditionMessage(e), "\n", sep = ""); FALSE })

if (!got) {
    cat("could not re-fetch the El Centro PPOS page; clause NOT re-confirmed this run\n")
} else {
    sha <- if (requireNamespace("digest", quietly = TRUE))
        digest::digest(file = ht, algo = "sha256") else NA_character_
    cat(sprintf("fetched bytes    : %d\n", file.size(ht)))
    cat(sprintf("fetched sha256   : %s  (%s)\n", sha,
                if (identical(sha, RIGHTS_SHA)) "byte-identical to the register's recorded hash"
                else "DIFFERS from the register -- page may have been revised"))
    txt <- paste(readLines(ht, warn = FALSE), collapse = "\n")
    hit <- grepl(CLAUSE, txt, fixed = TRUE)
    cat(sprintf("clause present   : %s\n", if (hit) "YES" else "NO"))
    if (hit) cat(sprintf("clause           : \"%s\"\n", CLAUSE))
    ok_rights <- hit
}

cat("\nNote: this script verifies the BLOCK and the code derivation, not any item_text --\n",
    "no item text was shipped for this table. The three items tied at n=331 (ppos3/4/5)\n",
    "are not separated by this route.\n", sep = "")

cat(if (ok_identity && ok_rights) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
