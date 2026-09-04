# verify_CPDMMC_Kunnari_2020_PDP.R -- Step 5b route 9 (response-frequency matching).
#
# CLAIM UNDER TEST. The item text for each of the 18 PDP items was taken from
# PDP_codebook.pdf (osf.io/rx234), which keys each judgment question to a code
# (AB_C, AB_IC, ...) that data/CPDMMC_Kunnari_2020.R carries straight through
# from the column names of PDP_data.csv (osf.io/3z6wg). The option text was
# taken from the same codebook's "1 = Acceptable, 2 = Unacceptable" line, mapped
# onto the IRW table's 0/1 after the recode noted in the processing script.
#
# THE FALSIFIABLE PREDICTION. If (a) live `item` X really is source column X and
# (b) raw 1 -> resp 0 / raw 2 -> resp 1, then for every item the live count of
# resp==0 equals the raw count of "1" in that column, and likewise for 1/2.
# All 18 items have a distinct (n0, n1) pair, so no permutation of the 18 codes
# and no flip of the two option labels can survive this check.

suppressMessages(library(irw))

TABLE <- "CPDMMC_Kunnari_2020_PDP"
RAW_URL <- "https://osf.io/download/3z6wg/"   # PDP_data.csv, OSF project vmy4q

ITEMS <- c("AB_C","AB_IC","AR_C","AR_IC","BC_C","BC_IC","CA_C","CA_IC","HT_C",
           "HT_IC","REL_C","REL_IC","TM_C","TM_IC","TOR_C","TOR_IC","VP_C","VP_IC")

raw <- read.csv(RAW_URL, stringsAsFactors = FALSE)
d   <- irw::irw_fetch(TABLE)

cat(sprintf("%-8s %10s %10s %10s %10s  %s\n",
            "item", "raw_1", "live_0", "raw_2", "live_1", "match"))
ok <- TRUE
for (it in ITEMS) {
    r1 <- sum(raw[[it]] == 1, na.rm = TRUE)
    r2 <- sum(raw[[it]] == 2, na.rm = TRUE)
    l0 <- sum(d$item == it & d$resp == 0, na.rm = TRUE)
    l1 <- sum(d$item == it & d$resp == 1, na.rm = TRUE)
    hit <- (r1 == l0) && (r2 == l1)
    ok  <- ok && hit
    cat(sprintf("%-8s %10d %10d %10d %10d  %s\n", it, r1, l0, r2, l1,
                if (hit) "OK" else "MISMATCH"))
}

# The check is only decisive if the 18 count-pairs are mutually distinct --
# otherwise two items could be swapped without changing any number above.
pairs <- vapply(ITEMS, function(it)
    paste(sum(raw[[it]] == 1, na.rm = TRUE), sum(raw[[it]] == 2, na.rm = TRUE)),
    character(1))
ndup <- length(pairs) - length(unique(pairs))
cat(sprintf("\ndistinct (n1,n2) count-pairs: %d of %d (duplicates: %d)\n",
            length(unique(pairs)), length(pairs), ndup))

cat("Note: this pins every item code to its source column and pins the option\n",
    "labels to resp 0/1 (a flip would swap every column of the table above).\n",
    "It does NOT check the transcription of the vignette/question wording itself,\n",
    "which comes verbatim from Materials.pdf and PDP_codebook.pdf.\n", sep = "")

cat(if (ok && ndup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
