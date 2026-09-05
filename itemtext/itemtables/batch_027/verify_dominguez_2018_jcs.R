# Step 5b verification for dominguez_2018_jcs (batch_027).
#
# CLAIM UNDER TEST. data/dominguez_2018_job_crafting.py assigns the IRW codes
# POSITIONALLY: item_N <- the Nth entry of the hard-coded column list
# [6,7,8,9,10, 12..17, 19..23, 25..29] of the S1 File workbook
# (PLOS ONE 10.1371/journal.pone.0197276.s001, sheet "Hoja1"). The shipped
# item_text is the canonical Tims/Bakker/Derks (2012) DJCS item N. So the claim
# has two halves:
#   (a) item_N really is workbook column position N of that list, and
#   (b) that workbook's "Item N" numbering is the canonical DJCS numbering.
#
# WHAT THIS SCRIPT CHECKS
#   1. (a) outright, cell for cell: for each of the 21 items it compares the
#      live item x resp frequency table against the value counts of the
#      corresponding workbook column (after the .py's own 0-5 filter and
#      integer truncation). A shifted or permuted column range breaks this.
#      The live counts come from a server-side GROUP BY, not irw_fetch(), so
#      this costs no Redivis export quota.
#   2. (b) at the SUBSCALE-BLOCK level, via the paper's own published means
#      (Results, "Descriptive findings"): structural 4.50, social 3.86,
#      challenging 3.39, hindering 2.71. Block means computed from the live
#      data under the shipped block assignment (1-5 / 6-11 / 12-16 / 17-21)
#      must reproduce them. A different block order would miss by ~0.5-1.8.
#   3. That the source column labelled "Item 17" is NOT an item response: it
#      takes quarter values (1.5, 2.25, ...) and equals the mean of columns
#      "Item 18".."Item 21" in 200 of 202 rows, which is why item_17 ships with
#      blank item_text.
#
# WHAT IT DOES NOT ESTABLISH: the order of items WITHIN a subscale block.
# Nothing in the response data separates, say, item_2 from item_3; that rests
# on the workbook's own "Item N" column headers agreeing with the canonical
# numbering. Hence status=PARTIAL in verification_dominguez_2018_jcs.csv.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "dominguez_2018_jcs"
COLS  <- c(6,7,8,9,10, 12,13,14,15,16,17, 19,20,21,22,23, 25,26,27,28,29) + 1  # 1-based
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?id=10.1371/journal.pone.0197276.s001&type=supplementary")
PUB <- c(structural = 4.50, hindering = 2.71, social = 3.86, challenging = 3.39)
BLOCKS <- list(structural = 1:5, hindering = 6:11, social = 12:16, challenging = 17:21)

## --- live item x resp counts, server-side (no export) ---------------------
tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source("core"))
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                   "TRIM(CAST(resp AS STRING)) AS resp, COUNT(*) AS n FROM `%s`",
                   "WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                   "GROUP BY item, resp"), tbl$qualified_reference)
live <- as.data.frame(irw:::.irw_query_tibble(q))
live$resp <- as.integer(live$resp)

## --- the source workbook ---------------------------------------------------
f <- tempfile(fileext = ".xlsx")
utils::download.file(SI, f, quiet = TRUE, mode = "wb")
raw <- suppressWarnings(readxl::read_excel(f, sheet = "Hoja1", col_names = FALSE,
                                           .name_repair = "minimal"))
dat <- raw[-(1:2), ]   # rows 1-2 are the scale/subscale/header rows; data follows

srccol <- function(k) {
    v <- suppressWarnings(as.numeric(unlist(dat[[COLS[k]]])))
    v <- v[!is.na(v)]
    as.integer(trunc(v[v >= 0 & v <= 5]))    # the .py's own filter + astype(int)
}

cat("== check 1: live item x resp counts vs source column counts ==\n")
cat(sprintf("%-8s %-6s %-28s %-28s %s\n", "item", "col", "source counts (1..5)",
            "live counts (1..5)", "match"))
ok1 <- TRUE
for (k in 1:21) {
    it <- paste0("item_", k)
    s <- tabulate(srccol(k), nbins = 5)
    l <- tabulate(rep(live$resp[live$item == it], live$n[live$item == it]), nbins = 5)
    m <- identical(as.integer(s), as.integer(l)); ok1 <- ok1 && m
    cat(sprintf("%-8s %-6d %-28s %-28s %s\n", it, COLS[k] - 1,
                paste(s, collapse = "/"), paste(l, collapse = "/"),
                if (m) "yes" else "NO"))
}

## --- block means ------------------------------------------------------------
imean <- sapply(paste0("item_", 1:21), function(it) {
    z <- live[live$item == it, ]; sum(z$resp * z$n) / sum(z$n) })
cat("\n== check 2: subscale block means vs the paper's published means ==\n")
cat(sprintf("%-13s %10s %10s %8s\n", "block", "published", "observed", "diff"))
ok2 <- TRUE
for (b in names(BLOCKS)) {
    o <- mean(imean[BLOCKS[[b]]])
    cat(sprintf("%-13s %10.2f %10.3f %8.3f\n", b, PUB[[b]], o, o - PUB[[b]]))
    if (b != "challenging" && abs(o - PUB[[b]]) > 0.02) ok2 <- FALSE
}
cat("(the challenging block is expected to sit ~0.07 low: its 'Item 17' column is a\n",
    " composite that IRW truncates to an integer -- see check 3)\n", sep = "")

## --- item_17 is a composite, not a response --------------------------------
z  <- suppressWarnings(as.numeric(unlist(dat[[COLS[17]]])))
o4 <- rowMeans(sapply(18:21, function(k) suppressWarnings(as.numeric(unlist(dat[[COLS[k]]])))))
keep <- !is.na(z) & !is.na(o4)
cat("\n== check 3: source column 'Item 17' is a derived composite ==\n")
cat(sprintf("non-integer values in that column: %d of %d\n",
            sum(z[keep] %% 1 != 0), sum(keep)))
cat(sprintf("rows where it equals mean(Item 18..Item 21): %d of %d\n",
            sum(abs(z[keep] - o4[keep]) < 1e-9), sum(keep)))
ok3 <- sum(abs(z[keep] - o4[keep]) < 1e-9) > 0.95 * sum(keep)

cat("\nNote: none of this separates items WITHIN a subscale block; that rests on the\n",
    "workbook's own 'Item N' headers matching the canonical DJCS numbering.\n", sep = "")
cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
