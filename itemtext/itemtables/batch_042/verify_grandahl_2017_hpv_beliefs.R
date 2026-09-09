# verify_grandahl_2017_hpv_beliefs.R -- Step 5b, route 9 (response-frequency matching).
#
# CLAIM UNDER TEST. Two things at once:
#  (a) each IRW item code is the SPSS column of the same name in the study's own
#      deposit (S2 File, journal.pone.0187193.s003), whose variable label supplied
#      the shipped item_text; and
#  (b) the option_text<->resp direction is REVERSED relative to the .sav's value
#      labels, because data/grandahl_2017_hpv_beliefs.py maps the label strings
#      "Totally disagree"->1 ... "Totally agree"->5 while the .sav codes
#      1="Totally agree" ... 5="Totally disagree", 6="Do not know" (dropped).
#
# Prediction: counting the .sav's LABEL per column and the live table's INTEGER per
# item must match cell for cell across all 15 items x 5 levels. A swapped pair of
# items, or any permuted/flipped response level, breaks it.

suppressMessages(library(irw))
suppressMessages(library(haven))

TABLE <- "grandahl_2017_hpv_beliefs"
SAV <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0187193.s003"

MAP <- c("Totally disagree" = 1, "Partly disagree" = 2,
         "Neither agree or disagree" = 3, "Partly agree" = 4,
         "Totally agree" = 5)   # note: OPPOSITE of the .sav's own 1..5 codes

tmp <- tempfile(fileext = ".sav")
utils::download.file(SAV, tmp, quiet = TRUE, mode = "wb")
sav <- haven::read_sav(tmp)

d <- irw::irw_fetch(TABLE)
items <- sort(unique(as.character(d$item)))

cat(sprintf("%-28s %-22s %-22s %s\n", "item", "sav label counts 1..5",
            "live resp counts 1..5", "match"))
bad <- 0
for (it in items) {
    lab <- as.character(haven::as_factor(sav[[it]]))
    a <- as.integer(table(factor(MAP[lab], levels = 1:5)))
    b <- as.integer(table(factor(d$resp[d$item == it], levels = 1:5)))
    ok <- identical(a, b)
    bad <- bad + !ok
    cat(sprintf("%-28s %-22s %-22s %s\n", it,
                paste(a, collapse = ","), paste(b, collapse = ","),
                if (ok) "OK" else "MISMATCH"))
}
cat(sprintf("\nitems mismatching: %d of %d (75 cells compared)\n", bad, length(items)))

# Distinctness: the route only separates two items if their count vectors differ.
vecs <- sapply(items, function(it)
    paste(as.integer(table(factor(d$resp[d$item == it], levels = 1:5))), collapse = ","))
dupes <- sum(duplicated(vecs))
cat(sprintf("duplicate count-vectors among items: %d (0 => every item is distinguished)\n", dupes))

cat("Note: this pins item identity and the full 1..5 response direction. It does NOT\n",
    "check the WORDS -- those are the .sav variable labels, the study's own English\n",
    "for a questionnaire administered in Swedish, which no data check can validate.\n", sep = "")

cat(if (bad == 0 && dupes == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
