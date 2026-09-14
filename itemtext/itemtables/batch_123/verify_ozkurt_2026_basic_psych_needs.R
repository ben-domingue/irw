# verify_ozkurt_2026_basic_psych_needs.R
#
# What is being verified: item <-> item_text for BPNS1..BPNS14, and the
# direction of the option_text <-> resp anchors.
#
# The wording ships from S6 File (the study's "Measurement Instruments Used in
# the Study" DOCX), whose Table 3 lists the 14 BNSSS items against an "Original
# item no." column, 1..14. The live item codes are BPNS1..BPNS14, taken verbatim
# from the S2 File .sav column names by data/ozkurt_2026_wrestlers.py. So the
# claim under test is: BPNS<k> is the item S6 numbers <k>.
#
# Three falsifiable links, none of which is an item count:
#
#   Link A (route 9, response-frequency matching). S1 File .xlsx is the same 374
#     respondents with DIFFERENT column headers: it numbers its BPNS columns
#     "1.Competence" .. "14.Relatedness". Rows are ordered differently between
#     the two deposits, so the columns are tied by their 5-level response-count
#     vectors. For each k, the count vector of S1 header "k.<Subdim>" must equal
#     that of .sav column BPNS<k>, and must match NO OTHER BPNS column -- a
#     unique bijection, which is what rules out a permutation.
#   Link B. The live IRW table's per-item count vectors must equal the .sav's, so
#     the bijection reaches the shipped codes and not just the source file.
#   Link C. S6's subdimension for item k (Competence 1-5, Autonomy 6-9,
#     Relatedness 10-14) must agree with the subdimension spelled in the S1
#     header name for the column that matched, and with the .sav's own variable
#     label ("Competence1" .. "Relatedness5"). Three of the study's own files
#     have to agree on which block each code sits in.
#
#   Anchor direction (route 8). S6 states 1 = Strongly Disagree .. 5 = Strongly
#     Agree. Every item mean must sit well above the 3.0 midpoint: the reversed
#     reading would have national-team wrestlers disagreeing that they are
#     skilled at their own sport. Reported per item.
#
# What this does NOT establish: S6's item numbers and S1's header numbers are
# both the authors' own numbering, so a mis-numbering consistent across their two
# files would be invisible here. That residual is addressed outside this script,
# in provenance: S6's items 1-14 pair one-for-one and IN ORDER with the 14 items
# of Ng, Lonsdale & Hodge (2011) Table 1 (Comp1-5, Choice1-4, Relate1-5), which
# is a source the authors did not write.
#
# The live table is 374 x 14 = 5236 rows, so irw_fetch() here is a negligible
# export.

suppressMessages(library(irw))

TABLE <- "ozkurt_2026_basic_psych_needs"
BASE  <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0353067."

# S6 File Table 3: subdimension per "Original item no."
S6_SUB <- c(rep("Competence", 5), rep("Autonomy", 4), rep("Relatedness", 5))
ITEMS  <- paste0("BPNS", 1:14)

ok <- TRUE

## ---- fetch the two deposits -------------------------------------------------
tmp_x <- tempfile(fileext = ".xlsx"); tmp_s <- tempfile(fileext = ".sav")
download.file(paste0(BASE, "s001"), tmp_x, quiet = TRUE, mode = "wb")
download.file(paste0(BASE, "s002"), tmp_s, quiet = TRUE, mode = "wb")

x   <- as.data.frame(readxl::read_excel(tmp_x))
sav <- haven::read_sav(tmp_s)

hdr <- paste0(1:14, ".", S6_SUB)          # S1 File's own BPNS column headers
stopifnot(all(hdr %in% names(x)), all(ITEMS %in% names(sav)))

cnt <- function(v) as.integer(table(factor(as.integer(v), levels = 1:5)))

sav_cnt  <- sapply(ITEMS, function(c) cnt(sav[[c]]))
s1_cnt   <- sapply(hdr,   function(h) cnt(x[[h]]))

## ---- Link B: live table vs the .sav ----------------------------------------
d <- irw::irw_fetch(TABLE)
live_cnt <- sapply(ITEMS, function(i) cnt(d$resp[d$item == i]))
cat("Link B -- live per-item response counts vs S2 File .sav column counts\n")
cat(sprintf("%-8s %-22s %-22s %s\n", "item", "live 1..5", ".sav 1..5", "match"))
for (i in seq_along(ITEMS)) {
    m <- identical(live_cnt[, i], sav_cnt[, i]); ok <- ok && m
    cat(sprintf("%-8s %-22s %-22s %s\n", ITEMS[i],
                paste(live_cnt[, i], collapse = " "),
                paste(sav_cnt[, i],  collapse = " "), ifelse(m, "yes", "NO")))
}

## ---- Link A: S1 numbered header -> .sav column, uniquely --------------------
cat("\nLink A -- S1 File numbered header vs .sav column, by 5-level count vector\n")
cat(sprintf("%-16s %-22s %-10s %s\n", "S1 header", "counts 1..5", "expected", "unique match among BPNS1-14"))
for (i in seq_along(hdr)) {
    hits <- ITEMS[apply(sav_cnt, 2, function(cc) identical(cc, s1_cnt[, i]))]
    good <- length(hits) == 1 && hits == ITEMS[i]; ok <- ok && good
    cat(sprintf("%-16s %-22s %-10s %s\n", hdr[i],
                paste(s1_cnt[, i], collapse = " "), ITEMS[i],
                paste(hits, collapse = ",")))
}

## ---- Link C: subdimension agreement across three files ---------------------
lab <- sapply(ITEMS, function(c) {
    l <- attr(sav[[c]], "label"); if (is.null(l)) NA_character_ else l
})
cat("\nLink C -- S6 subdimension vs S1 header vs .sav variable label\n")
cat(sprintf("%-8s %-12s %-16s %-14s %s\n", "item", "S6", "S1 header", ".sav label", "agree"))
for (i in seq_along(ITEMS)) {
    lab_sub <- sub("[0-9]+$", "", as.character(lab[i]))
    agree <- identical(lab_sub, S6_SUB[i]) && grepl(S6_SUB[i], hdr[i], fixed = TRUE)
    ok <- ok && agree
    cat(sprintf("%-8s %-12s %-16s %-14s %s\n", ITEMS[i], S6_SUB[i], hdr[i],
                lab[i], ifelse(agree, "yes", "NO")))
}

## ---- anchor direction ------------------------------------------------------
mu <- tapply(d$resp, factor(d$item, levels = ITEMS), mean)
cat("\nAnchor direction -- item means on the shipped 1 = Strongly Disagree .. 5 = Strongly Agree\n")
cat(paste(sprintf("%s=%.2f", ITEMS, mu), collapse = "  "), "\n")
cat(sprintf("min item mean %.2f, max %.2f (midpoint 3.00)\n", min(mu), max(mu)))
dir_ok <- min(mu) > 3.5; ok <- ok && dir_ok
cat("Reversed anchors would put every mean at", sprintf("%.2f", 6 - max(mu)),
    "-", sprintf("%.2f", 6 - min(mu)),
    "i.e. elite national-team wrestlers mostly disagreeing that they are skilled\n")
cat("at their own sport; Ng et al. (2011) report 5.58-6.07 on a 1-7 version of the\n")
cat("same items, the same end of the scale.\n")

cat("\nNot established here: a mis-numbering consistent across S1 and S6 (both the\n")
cat("authors' own files) would be invisible; the pairing with Ng et al. (2011)\n")
cat("Table 1's item order, recorded in provenance, is what covers that.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
