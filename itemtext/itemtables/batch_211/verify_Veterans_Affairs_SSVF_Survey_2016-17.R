# verify_Veterans_Affairs_SSVF_Survey_2016-17.R
#
# THE CLAIM. `item` in this table is a bare integer that the IRW processing
# script (data/Veterans Affairs SSVF Survey 2016-17.R) INVENTS:
#
#     items <- as.data.frame(unique(df$item)); items <- mutate(items, item_id = row_number())
#
# i.e. item N = the Nth surviving column of the FOIA spreadsheet, after
# df[,-c(2:29)] and after dropping negative/date.range/f37/q7/q8.4.[abc]_6_text.
# Core model section 3 says: re-run the script rather than reason about it.
#
# CHECK 1 (decisive, pins item -> source column). Reproduce the script's column
# order from the raw .xlsx and its per-item n (count of non-missing responses
# with resp != 6, which `filter(resp != 6)` also drops NA for), and compare to
# the live per-item n from irw::irw_table_sets(). 59 items must match exactly.
#
# CHECK 2 (pins source column -> item text for the 13 service sub-rows). The
# 2016-17 spreadsheet labels its service grid positionally (Q8.3-a_1..8,
# Q8.4-a_1..6); the wording comes from the FOIA data dictionary, which names
# those positions for the 2018-2020 spreadsheet (Q3_3_1..8, Q3_4_1..5). The
# falsifiable prediction is that position k in one file is the same service as
# position k in the other, so the "did you need this service" rate at position k
# should agree across the two files. It does, but see the Note: it does NOT
# separate positions 1-4 of the public-benefits block from each other.
#
# No irw_fetch() anywhere: table_sets() is a server-side aggregate.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "Veterans_Affairs_SSVF_Survey_2016-17"
BASE  <- "https://raw.githubusercontent.com/data-liberation-project/va-ssvf-survey-data/main/data/raw/"
CACHE <- file.path("itemtext", ".cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- file.path(".cache", TABLE)
dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)

get_raw <- function(local, remote) {
    p <- file.path(CACHE, local)
    if (!file.exists(p))
        download.file(paste0(BASE, remote), p, quiet = TRUE, mode = "wb")
    p
}
p16 <- get_raw("raw_2016_17.xlsx", "FINAL%20Data%20-%20FY%202016-2017_Excluding%20PII.xlsx")
p18 <- get_raw("raw_2018_20.xlsx", "FINAL%20Data%20-%20FY%202018-2020_Excluding%20PII.xlsx")

r16 <- suppressWarnings(read_excel(p16, col_types = "text"))
r18 <- suppressWarnings(read_excel(p18, col_types = "text"))

## ---- CHECK 1: re-run the processing script's item numbering ----------------
nm   <- tolower(make.names(names(r16)))
keep <- c(1, 30:length(nm))
drop <- c("negative", "date.range", "f37", "q7",
          "q8.4.a_6_text", "q8.4.b_6_text", "q8.4.c_6_text")
keep <- keep[!nm[keep] %in% drop]
cols <- nm[keep][-1]

num <- function(x) suppressWarnings(as.numeric(trimws(x)))
repro <- vapply(keep[-1], function(j) {
    v <- num(r16[[j]]); sum(!is.na(v) & v != 6)
}, numeric(1))
names(repro) <- as.character(seq_along(repro))

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- as.data.frame(s$per_item)
livn <- setNames(as.numeric(live$n), as.character(live$item))
livn <- livn[names(repro)]

cat("CHECK 1 -- re-run of the processing script's column ordering\n")
cat(sprintf("%-5s %-14s %10s %10s %6s\n", "item", "source column", "reproduced", "live n", "ok"))
for (i in seq_along(repro))
    cat(sprintf("%-5s %-14s %10d %10d %6s\n", names(repro)[i], cols[i],
                repro[i], livn[i], if (identical(repro[[i]], livn[[i]])) "ok" else "MISMATCH"))
n_bad <- sum(repro != livn)
cat(sprintf("\nitems matching exactly: %d of %d ; reproduced total rows %d vs live %d\n\n",
            sum(repro == livn), length(repro), sum(repro), s$n_rows))

## ---- CHECK 2: cross-file service-position agreement ------------------------
rate <- function(df, col) {
    v <- num(df[[col]]); v <- v[!is.na(v) & v %in% c(1, 2)]
    100 * sum(v == 1) / length(v)
}
svc8 <- c("Health care", "Daily living", "Personal financial planning", "Transportation",
          "Income support", "Legal", "Child care", "Housing counseling")
svc5 <- c("Rental Assistance", "Utility fee payment assistance",
          "Security and utility deposits", "Moving costs", "Purchase of emergency supplies")

cat("CHECK 2 -- 'did you need this service' % Yes, by grid position\n")
cat(sprintf("%-32s %10s %10s %8s\n", "shipped label at that position", "FY16-17", "FY18-20", "diff"))
d8 <- numeric(8)
for (k in 1:8) {
    a <- rate(r16, sprintf("Q8.3-a_%d", k)); b <- rate(r18, sprintf("Q3_3_%d_A", k))
    d8[k] <- a - b
    cat(sprintf("%-32s %10.1f %10.1f %8.1f\n", svc8[k], a, b, a - b))
}
d5 <- numeric(5)
for (k in 1:5) {
    a <- rate(r16, sprintf("Q8.4-a_%d", k)); b <- rate(r18, sprintf("Q3_4_%d_A", k))
    d5[k] <- a - b
    cat(sprintf("%-32s %10.1f %10.1f %8.1f\n", svc5[k], a, b, a - b))
}
worst <- max(abs(c(d8, d5)))
cat(sprintf("\nlargest positional disagreement: %.1f percentage points (tolerance 5.0)\n\n", worst))

cat("Note -- what this does NOT establish:\n",
    "  * Within the 8-service public-benefits grid, positions 1-4 (Health care,\n",
    "    Daily living, Personal financial planning, Transportation) span only\n",
    "    46.3-50.6% need in FY16-17 and 46.5-52.8% in FY18-20, so Check 2 places\n",
    "    them as a SET but does not separate them from one another. Positions 5-8\n",
    "    (Income support 63, Legal 29, Child care 8, Housing counseling 68) and all\n",
    "    five Other Supportive Services rows are individually separated.\n",
    "  * Item 7 ('Q8 into') ships no item_text, and the sixth Other-Supportive-\n",
    "    Services row (items 43/49/55) ships the block stem without a sub-label,\n",
    "    because the FOIA release publishes neither.\n",
    "  * Item 58's wording is the 2015 form's; the FY16-17 form's own phrasing of\n",
    "    that item is not published.\n", sep = "")

cat(if (n_bad == 0 && worst <= 5) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
