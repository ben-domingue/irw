# verify_cucchi_2018_tas20.R
#
# mapping_basis = data_labels: the study's own SPSS file (peerj-06-5756-s003.sav,
# CC BY 4.0 PeerJ deposit) labels every column "TASn: <item wording>", so the
# item<->item_text axis is tied at the source and needs no statistical route.
#
# What this script verifies is the OTHER axis -- option_text <-> resp. The study
# never published its anchors, so the shipped 1 = Strongly disagree .. 5 =
# Strongly agree comes from the canonical TAS-20. That direction is a falsifiable
# claim, because the .sav also stores the scored total (`TAS`): under standard
# TAS-20 scoring exactly canonical items 4, 5, 10, 18 and 19 are reverse-keyed,
# and under the SPSS numbering those are TAS9, TAS13, TAS15, TAS18, TAS19. If the
# anchors ran the other way (1 = Strongly agree) the reverse-keyed set would be
# the complementary 15 items and the stored total would not reconstruct.
#
# Fetches its own data from the public PeerJ supplementary endpoint; makes no
# irw_fetch() call, so it costs no Redivis export quota.

suppressMessages({library(haven); library(utils)})

URL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6211265/supplementaryFiles"
tmpzip <- tempfile(fileext = ".zip"); dir <- tempfile(); dir.create(dir)
download.file(URL, tmpzip, quiet = TRUE, mode = "wb")
unzip(tmpzip, files = "peerj-06-5756-s003.sav", exdir = dir)
d <- haven::read_sav(file.path(dir, "peerj-06-5756-s003.sav"))

items <- paste0("TAS", 1:20)
REV   <- c("TAS9", "TAS13", "TAS15", "TAS18", "TAS19")   # canonical 4, 5, 10, 18, 19
d <- d[stats::complete.cases(d[, c(items, "TAS")]), ]
cat(sprintf("complete cases: %d\n", nrow(d)))

raw <- rowSums(d[, items])
rev <- raw
for (c_ in REV) rev <- rev - d[[c_]] + (6 - d[[c_]])
stored <- d[["TAS"]]

cat(sprintf("stored TAS total: mean %.2f, range %d-%d\n",
            mean(stored), min(stored), max(stored)))
cat(sprintf("plain row sum reproduces stored total for %5.1f%% of respondents\n",
            100 * mean(raw == stored)))
cat(sprintf("row sum with {%s} reverse-keyed reproduces it for %5.1f%%\n",
            paste(REV, collapse = ","), 100 * mean(rev == stored)))

# Corrected item-total correlations on the RAW items: the five reverse items
# should sit at or below zero, the other fifteen above it.
cat("\ncorrected item-total r (raw, unreversed):\n")
for (c_ in items) {
    r <- stats::cor(d[[c_]], rowSums(d[, setdiff(items, c_)]))
    cat(sprintf("  %-6s %6.3f %s\n", c_, r, if (c_ %in% REV) "<- reverse-keyed" else ""))
}

ok <- all(rev == stored) && !all(raw == stored)
cat("\nNote: this route pins the ANCHOR DIRECTION and separates the five reverse-keyed\n",
    "items from the other fifteen. It does NOT distinguish, say, TAS1 from TAS3 --\n",
    "the .sav's own variable labels (mapping_basis=data_labels) are what do that.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
