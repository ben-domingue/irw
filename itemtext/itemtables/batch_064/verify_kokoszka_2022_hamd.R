# verify_kokoszka_2022_hamd.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the 18 item codes ham1..ham15, ham16a, ham16b, ham17 are the
# HDRS-17's items 1..17 in canonical Hamilton numbering, with item 16 (loss of
# weight) split into its standard alternates 16a ("according to the patient")
# and 16b ("according to weekly measurements"), and the shipped anchors are that
# instrument's anchors for those numbered items.
#
# Two falsifiable predictions, neither of which is about item counts:
#
#  (1) SCALE TOTAL vs. the paper.  If these 18 columns really are the HDRS-17,
#      then summing ham1..ham15 + ONE of {ham16a, ham16b} + ham17 must reproduce
#      the HAM-D descriptives the paper prints in Table 1, separately by gender.
#      This also tests the claim that 16a/16b are ALTERNATE ratings of a single
#      item rather than two distinct items -- summing both overshoots.
#  (2) PER-ITEM RESPONSE RANGE STRUCTURE (Step 5b route 2).  The HDRS-17 scores
#      items 1,2,3,7,8,9,10,11,15 on 0-4 and items 4,5,6,12,13,14,16,17 on 0-2.
#      That is a structural signature of the numbering: an item observed above 2
#      cannot be in the 0-2 class.  Checked against the live table's own maxima.
#
# Route (2) uses irw::irw_table_sets() (server-side aggregate, no export quota
# spend). Route (1) uses the study's own S1 Data, which is the file the IRW
# table was built from -- data/kokoszka_2022_diabetes_distress.py melts exactly
# these columns, so the column names ARE the item codes.

suppressMessages(library(irw))
TABLE <- "kokoszka_2022_hamd"

ok <- TRUE

## ---- (1) published HAM-D total, Kokoszka et al. 2022 PLOS ONE Table 1 -------
# t001: "Hamilton Rating Scale for Depression"  Women M 8.37 SD 7.26 min-max 0-29
#                                               Men   M 6.46 SD 7.49 min-max 0-27
PUB <- data.frame(group = c("women", "men"), M = c(8.37, 6.46), SD = c(7.26, 7.49),
                  min = c(0, 0), max = c(29, 27))

url <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0263766.s001")
tmp <- tempfile(fileext = ".csv")
raw <- try(download.file(url, tmp, quiet = TRUE), silent = TRUE)
if (inherits(raw, "try-error")) {
    cat("could not download S1 Data -- route (1) skipped\n")
} else {
    d <- read.csv2(tmp, fileEncoding = "UTF-8-BOM", check.names = FALSE)
    ham <- c(paste0("ham", 1:15), "ham16a", "ham16b", "ham17")
    for (c_ in ham) d[[c_]] <- suppressWarnings(as.numeric(d[[c_]]))
    base <- c(paste0("ham", 1:15), "ham17")
    tot  <- rowSums(d[, base]) + d[["ham16b"]]    # rate either a or b
    both <- rowSums(d[, ham])                     # the wrong reading, for contrast
    sex  <- d[["pif_a4"]]                         # 0 = women (n=49), 1 = men (n=51)
    cat("-- (1) HAM-D total, ham1..15 + ham16b + ham17, vs paper Table 1 --\n")
    cat(sprintf("%-7s %-9s %6s %6s %6s %6s\n", "group", "source", "M", "SD", "min", "max"))
    for (i in 1:2) {
        g <- if (PUB$group[i] == "women") 0 else 1
        s <- tot[sex == g]; s <- s[!is.na(s)]
        cat(sprintf("%-7s %-9s %6.2f %6.2f %6.0f %6.0f\n", PUB$group[i], "paper",
                    PUB$M[i], PUB$SD[i], PUB$min[i], PUB$max[i]))
        cat(sprintf("%-7s %-9s %6.2f %6.2f %6.0f %6.0f\n", PUB$group[i], "computed",
                    mean(s), sd(s), min(s), max(s)))
        if (abs(mean(s) - PUB$M[i]) > 0.05 || abs(sd(s) - PUB$SD[i]) > 0.05 ||
            min(s) != PUB$min[i] || max(s) != PUB$max[i]) ok <- FALSE
    }
    b <- both[sex == 0]; b <- b[!is.na(b)]
    cat(sprintf("contrast: summing BOTH 16a and 16b gives women M %.2f (paper 8.37)\n",
                mean(b)))
}

## ---- (2) 0-4 vs 0-2 range classes -------------------------------------------
FOURPT <- c("ham1","ham2","ham3","ham7","ham8","ham9","ham10","ham11","ham15")
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
cat("\n-- (2) canonical HDRS-17 range class vs observed maximum --\n")
cat(sprintf("%-8s %-10s %8s %s\n", "item", "class", "obs_max", "consistent"))
viol <- 0
for (k in seq_len(nrow(pi))) {
    it <- pi$item[k]; mx <- pi$resp_max[k]
    cls <- if (it %in% FOURPT) "0-4" else "0-2"
    good <- if (cls == "0-2") mx <= 2 else TRUE
    if (!good) viol <- viol + 1
    cat(sprintf("%-8s %-10s %8s %s\n", it, cls, mx, if (good) "yes" else "NO"))
}
cat(sprintf("violations: %d of %d\n", viol, nrow(pi)))
cat(sprintf("items observed above 2: %s (all in the 0-4 class: %s)\n",
            paste(pi$item[pi$resp_max > 2], collapse = ", "),
            all(pi$item[pi$resp_max > 2] %in% FOURPT)))
if (viol > 0 || !all(pi$item[pi$resp_max > 2] %in% FOURPT)) ok <- FALSE

## ---- what this does NOT establish -------------------------------------------
cat("\nNOT established by either route: the ORDER of items WITHIN a range class.\n",
    "ham4/ham5/ham6 (initial/middle/delayed insomnia) all score 0-2 and are\n",
    "mutually interchangeable under both tests, as are ham12/ham13/ham14; the\n",
    "0-4 items are separated only partially (ham3 = Suicide is pinned by being\n",
    "the least-endorsed 0-4 item, mean 0.15). The assignment of 16a vs 16b to\n",
    "'by patient' vs 'by weekly measurement' comes from the a/b suffix, not the\n",
    "data. Hence the recorded status is PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
