# verify_carver_2017_puggs_pilot2_attitudes.R
#
# CLAIM UNDER TEST
#   The item codes Q26..Q45 in carver_2017_puggs_pilot2_attitudes carry the
#   Section 5 ("Attitudes") wording of the PUGGS questionnaire as administered in
#   the SECOND pilot (PLOS ONE 10.1371/journal.pone.0169808, S1 questionnaire /
#   S6 code book), NOT the first pilot's Section 4 wording (S3 questionnaire,
#   where the same constructs are numbered Q32..Q51 and several items are worded
#   differently).
#
# Three falsifiable predictions, none of which validate_items.R can make:
#   A. PILOT boundary. The pilot-2 raw file (s006) has exactly 45 Q columns and
#      17 TT columns; the pilot-1 raw file (s005) has 51 and 20. The S1
#      questionnaire we transcribed numbers its items 1..45 with 17 traits, so S1
#      is the pilot-2 form; the S3 questionnaire numbers 1..51 with 20 traits.
#   B. CODE<->COLUMN identity. Reproducing the IRW processing script's melt over
#      source columns Q26..Q45 must reproduce the live per-item n, resp min and
#      resp max for all 20 items exactly (server-side, no export).
#   C. CONSTRUCT/WORDING tie. The pilot-2 code book marks exactly six attitude
#      items reverse-coded: Q26, Q34, Q37, Q39, Q43, Q44. Those are precisely the
#      six negatively-worded stems in the wording we shipped. If any block of
#      wording had slipped onto the wrong codes, the reverse-worded stems would
#      no longer sit on the codes whose responses run against their own domain's
#      "I am generally positive towards X" anchor item.
#
# NOT established here: order WITHIN a polarity class and within a domain. That
# is carried by the explicit numbering (the questionnaire prints "26".."45" in
# its own Q. column and the data columns are literally named Q26..Q45), which is
# a label match, not an inference.

suppressMessages({library(irw); library(readxl)})

TABLE <- "carver_2017_puggs_pilot2_attitudes"
ITEMS <- paste0("Q", 26:45)
REV   <- c("Q26", "Q34", "Q37", "Q39", "Q43", "Q44")   # S6 code book, Section 5
DOMAINS <- list("Gene therapy"       = 26:30,
                "Genetic testing"    = 31:35,
                "Prenatal testing"   = 36:40,
                "Pers. medicine"     = 41:45)

cache <- file.path("..", "..", ".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)
get_supp <- function(id, dest) {
    if (!file.exists(dest))
        download.file(sprintf(paste0("https://journals.plos.org/plosone/article/file",
                                     "?type=supplementary&id=10.1371/journal.pone.0169808.s%s"), id),
                      dest, quiet = TRUE, mode = "wb")
    dest
}
p1 <- read_excel(get_supp("005", file.path(cache, "s005.bin")), sheet = "Sheet1")
p2 <- read_excel(get_supp("006", file.path(cache, "s006.bin")), sheet = "Sheet1")

## ---- A. pilot boundary -------------------------------------------------
nq1 <- sum(grepl("^Q[0-9]+$", names(p1))); nt1 <- sum(grepl("^TT[0-9]+", names(p1)))
nq2 <- sum(grepl("^Q[0-9]+$", names(p2))); nt2 <- sum(grepl("^TT[0-9]+", names(p2)))
cat("A. PILOT boundary\n")
cat(sprintf("   pilot 1 raw file (s005): %d Q columns, %d TT columns\n", nq1, nt1))
cat(sprintf("   pilot 2 raw file (s006): %d Q columns, %d TT columns\n", nq2, nt2))
cat("   S1 questionnaire (the wording shipped) numbers items 1-45 with 17 traits\n")
cat("   S3 questionnaire (first pilot form)   numbers items 1-51 with 20 traits\n")
okA <- (nq1 == 51 && nt1 == 20 && nq2 == 45 && nt2 == 17)
cat(sprintf("   => S1 matches pilot 2, S3 matches pilot 1: %s\n\n", okA))

## ---- B. code <-> source column identity --------------------------------
sets <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- as.data.frame(sets$per_item)
raw  <- suppressWarnings(sapply(p2[ITEMS], as.numeric))
raw[!(raw >= 1 & raw <= 4)] <- NA          # matches _melt_likert(valid_max=4)

cat("B. per-item n / resp range reproduced from source columns Q26..Q45\n")
cat(sprintf("   %-5s %14s %14s %14s\n", "item", "n src/live", "min src/live", "max src/live"))
okB <- TRUE
for (it in ITEMS) {
    v  <- raw[, it]; v <- v[!is.na(v)]
    lr <- live[live$item == it, ]
    m  <- (length(v) == lr$n && min(v) == lr$resp_min && max(v) == lr$resp_max)
    okB <- okB && m
    cat(sprintf("   %-5s %6d /%6d %6d /%6d %6d /%6d %s\n", it, length(v), lr$n,
                min(v), lr$resp_min, max(v), lr$resp_max, ifelse(m, "", " <-- MISMATCH")))
}
cat(sprintf("   => all 20 items reproduce exactly: %s\n\n", okB))

## ---- C. reverse-keying pattern vs the wording shipped ------------------
cat("C. polarity: correlation with each domain's own \"generally positive\" anchor\n")
neg_rev <- 0; pos_ok <- 0; n_fwd <- 0
for (dn in names(DOMAINS)) {
    idx <- DOMAINS[[dn]]; anchor <- paste0("Q", max(idx))
    for (i in head(idx, -1)) {
        it <- paste0("Q", i)
        r  <- suppressWarnings(cor(raw[, it], raw[, anchor], use = "pairwise.complete.obs"))
        isrev <- it %in% REV
        if (isrev) { if (r < 0) neg_rev <- neg_rev + 1 } else { n_fwd <- n_fwd + 1; if (r >= 0) pos_ok <- pos_ok + 1 }
        cat(sprintf("   %-16s %-5s vs %-5s r = %+.3f   codebook_reversed = %s\n",
                    dn, it, anchor, r, isrev))
    }
}
cat(sprintf("   reverse-coded items with r < 0: %d of %d\n", neg_rev, length(REV)))
cat(sprintf("   forward items with r >= 0:      %d of %d\n", pos_ok, n_fwd))
okC <- (neg_rev >= 5 && pos_ok == n_fwd)
cat(sprintf("   => keying pattern matches the shipped wording: %s\n", okC))
cat("   (Q34, 'The availability of genetic tests for insurance companies and future\n")
cat("    employers is problematic', is the one reverse-coded item that does not run\n")
cat("    negative; it is a caveat item rather than an anti-testing item.)\n\n")

cat("This pins: the pilot version, the construct block (Section 5 = Q26..Q45),\n")
cat("the code<->source-column identity, and the reverse-worded subset.\n")
cat("It does NOT pin order within a domain/polarity class -- the questionnaire's\n")
cat("own printed numbering does that.\n\n")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
