# verify_VSOCFP_Sebo_2024.R -- Step 5b re-runnable evidence.
#
# CLAIM: item code SOCk in the live IRW table carries the responses to item k of
# the French SOC-13 questionnaire printed in Multimedia Appendix 1 of Sebo et al.
# 2024 (Interact J Med Res 13:e50284, doi:10.2196/50284), and the shipped
# item_text/option_text for SOCk is that item's wording and its 1/7 anchors.
#
# Three independent checks, none of which is a row/item count:
#  (1) live per-item (n, mean, SD) vs the same-named column of the study's own
#      SOC_osf.dta (OSF osf.io/pj5mr). The 8 triples are mutually distinct, so
#      this pins every live item code to one source column individually.
#  (2) the .dta's own value labels (item-specific 1/7 anchors) vs the anchors
#      shipped in option_text, item by item.
#  (3) the .dta's precomputed subscale totals SOC13_C / _Ma / _Me reproduce
#      EXACTLY from the canonical SOC-13 item-number -> dimension assignment
#      (C = 2,6,8,9,11; Ma = 3,5,10,13; Me = 1,4,7,12), and the four columns
#      stored reverse-coded (SOC1R, SOC2R, SOC3R, SOC7R) are exactly the four
#      appendix items whose printed anchors run positive->negative. Both tie the
#      numeric suffix to the canonical instrument numbering rather than to an
#      arbitrary order.

suppressMessages({library(irw); library(haven)})

TABLE <- "VSOCFP_Sebo_2024"
DTA_URL <- "https://osf.io/download/mw29z/"
ITEMS <- c("SOC4","SOC6","SOC8","SOC9","SOC10","SOC11","SOC12","SOC13")

## locate this script's own directory (for the shipped __items.csv)
argv <- commandArgs(trailingOnly = FALSE)
f <- sub("^--file=", "", argv[grep("^--file=", argv)])
HERE <- if (length(f)) dirname(normalizePath(f[1])) else getwd()

dta <- file.path(tempdir(), "SOC_osf.dta")
if (!file.exists(dta)) download.file(DTA_URL, dta, quiet = TRUE, mode = "wb")
src <- as.data.frame(read_dta(dta))
labs <- lapply(src, function(x) attr(x, "labels"))
src[] <- lapply(src, function(x) suppressWarnings(as.numeric(x)))

live <- as.data.frame(irw::irw_fetch(TABLE))
live$resp <- as.numeric(live$resp)

ok <- TRUE

cat("=== (1) live per-item n / mean / SD vs SOC_osf.dta column of the same name ===\n")
cat(sprintf("%-6s %5s %5s %14s %14s %14s %14s\n",
            "item","n_live","n_dta","mean_live","mean_dta","sd_live","sd_dta"))
stat <- function(v) c(sum(!is.na(v)), mean(v, na.rm = TRUE), sd(v, na.rm = TRUE))
trip <- character(0)
for (k in ITEMS) {
    a <- stat(live$resp[live$item == k]); b <- stat(src[[k]])
    cat(sprintf("%-6s %5d %5d %14.10f %14.10f %14.10f %14.10f\n",
                k, a[1], b[1], a[2], b[2], a[3], b[3]))
    if (a[1] != b[1] || abs(a[2]-b[2]) > 1e-10 || abs(a[3]-b[3]) > 1e-10) ok <- FALSE
    trip <- c(trip, sprintf("%d|%.10f|%.10f", b[1], b[2], b[3]))
}
cat(sprintf("distinct (n,mean,sd) triples among the 8 source columns: %d of 8\n",
            length(unique(trip))))
if (length(unique(trip)) != 8) ok <- FALSE

cat("\n=== (2) .dta value labels (1/7 anchors) vs shipped option_text ===\n")
shipped <- read.csv(file.path(HERE, "VSOCFP_Sebo_2024__items.csv"), encoding = "UTF-8")
for (k in ITEMS) {
    lb <- labs[[k]]
    a1 <- names(lb)[lb == 1]; a7 <- names(lb)[lb == 7]
    s1 <- shipped$option_text[shipped$item == k & shipped$resp == 1]
    s7 <- shipped$option_text[shipped$item == k & shipped$resp == 7]
    norm <- function(s) tolower(gsub("[^[:alnum:] ]", "", iconv(s, "UTF-8", "ASCII//TRANSLIT")))
    m1 <- norm(a1) == norm(s1); m7 <- norm(a7) == norm(s7)
    ## KNOWN, DOCUMENTED DIFFERENCE: the .dta value label for SOC11 at 7 reads
    ## "...dans de juste proportions", the published questionnaire (Multimedia
    ## Appendix 1) reads "...dans de justes proportions". The appendix is what
    ## respondents read, so that is what ships; the .dta label is a one-character
    ## typo in a Stata label, not a different anchor. Not a mapping failure.
    known <- (k == "SOC11")
    tag <- function(m) if (isTRUE(m)) "match" else if (known) "DIFFER (known typo, see note)" else "DIFFER"
    cat(sprintf("%-6s 1: %-46s | %-46s %s\n", k, a1, s1, tag(m1)))
    cat(sprintf("%-6s 7: %-46s | %-46s %s\n", k, a7, s7, tag(m7)))
    if (!known && (!isTRUE(m1) || !isTRUE(m7))) ok <- FALSE
}

cat("\n=== (3) canonical SOC-13 subscale composition reproduces the .dta totals ===\n")
grp <- list(SOC13_C  = c("SOC2R","SOC6","SOC8","SOC9","SOC11"),
            SOC13_Ma = c("SOC3R","SOC5","SOC10","SOC13"),
            SOC13_Me = c("SOC1R","SOC4","SOC7R","SOC12"),
            SOC13_tot = c("SOC1R","SOC2R","SOC3R","SOC4","SOC5","SOC6","SOC7R",
                          "SOC8","SOC9","SOC10","SOC11","SOC12","SOC13"),
            SOC8_tot = ITEMS)
for (g in names(grp)) {
    d <- max(abs(src[[g]] - rowSums(src[grp[[g]]])), na.rm = TRUE)
    cat(sprintf("%-10s = sum(%s): max |diff| = %g\n", g,
                paste(grp[[g]], collapse = "+"), d))
    if (!is.finite(d) || d > 1e-10) ok <- FALSE
}
rev_cols <- grep("R$", names(src), value = TRUE)
cat("reverse-stored columns in the .dta:", paste(rev_cols, collapse = ", "),
    "-- appendix items whose printed anchors run positive->negative: 1, 2, 3, 7\n")
if (!identical(sort(rev_cols), sort(c("SOC1R","SOC2R","SOC3R","SOC7R")))) ok <- FALSE

cat("\nWhat this does NOT establish: the anchors of SOC6, SOC8, SOC9, SOC10, SOC12\n",
    "and SOC13 are identical to each other ('Tres souvent' / 'Tres rarement ou\n",
    "jamais'), so check (2) distinguishes only SOC4 and SOC11 outright; what\n",
    "separates the remaining six is the numeric suffix itself matching the\n",
    "appendix's own item numbering, corroborated by check (3)'s exact subscale\n",
    "reproduction under the canonical numbering and by the .dta's Qualtrics\n",
    "variable labels (SOC4=Q16 ... SOC13=Q25, i.e. question number = item number\n",
    "+ 12 with the gap at Q19 falling on reverse-stored SOC7R).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
