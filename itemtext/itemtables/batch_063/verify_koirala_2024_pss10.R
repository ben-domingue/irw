# verify_koirala_2024_pss10.R -- Step 5b, mapping evidence BANKED for a blocked table.
#
# STATUS: koirala_2024_pss10 is BLOCKED on instrument rights (PSS family; irw#1945
# 2026-09-05, irw#1955 2026-09-06, extended to the whole PSS family 2026-09-07).
# No {table}__items.csv was written, so there is no shipped item_text mapping for
# this script to verify. What it does instead is bank the code->source-column
# identity so that, if the rights ruling is ever reversed, the extraction is a
# re-run rather than a restart. The verification row is recorded NO_ROUTE.
#
# THE CLAIM BANKED: the IRW codes PSS1..PSS10 ARE the SPSS column names of the
# study's S1 File (data/koirala_2024_pss_bcs.py melts PSS_COLS = ["PSS1".."PSS10"]
# BY NAME, not positionally), and the .sav's variable labels carry the PSS-10
# stems verbatim against those same names -- so item_text would be data_labels.
#
# The falsifiable prediction: per-item live n must equal the per-item count of
# MAPPABLE source values (the five labelled anchors Never..Very often), which is
# NOT simply the non-missing count -- four columns each carry one stray unlabelled
# 5.0 that the processing script's label map drops. That 317/316 pattern is a
# fingerprint: it is wrong for any permutation of the ten codes.
#
# Live side uses irw::irw_table_sets() (server-side aggregate), NOT irw_fetch(),
# so this script costs no Redivis export quota.

suppressMessages(library(irw))

TABLE  <- "koirala_2024_pss10"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0305588.s001")
CACHE  <- file.path("itemtext", ".cache", TABLE, "s001.sav")
if (!file.exists(CACHE)) CACHE <- file.path(".cache", TABLE, "s001.sav")
if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(SI_URL, CACHE, mode = "wb", quiet = TRUE)
}

items <- paste0("PSS", 1:10)
ANCHORS <- c("Never", "Almost never", "Sometimes", "Fairly often", "Very often")

sav <- haven::read_sav(CACHE)
stopifnot(all(items %in% names(sav)))

# Source side: count values whose SPSS value label is one of the five anchors.
src_n <- sapply(items, function(v) {
    x   <- sav[[v]]
    lab <- attr(x, "labels")
    ok  <- as.numeric(lab[names(lab) %in% ANCHORS])
    sum(x %in% ok, na.rm = TRUE)
})

# Live side: server-side per-item aggregate, no export.
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(as.integer(pi$n), pi$item)[items]

cat(sprintf("%-7s %10s %10s %8s\n", "item", "n_source", "n_live", "match"))
for (i in items)
    cat(sprintf("%-7s %10d %10d %8s\n", i, src_n[[i]], live_n[[i]],
                ifelse(src_n[[i]] == live_n[[i]], "OK", "MISMATCH")))

n_ok <- sum(src_n == live_n)
cat(sprintf("\nper-item n reconciled: %d/10\n", n_ok))

# Anchor coding: the .sav's own value labels are Never=0 .. Very often=4, which is
# exactly MAP_PSS in data/koirala_2024_pss_bcs.py, and the live resp set is 0..4.
lab1 <- attr(sav[["PSS1"]], "labels")
cat("PSS1 value labels: ",
    paste(sprintf("%s=%g", names(lab1), as.numeric(lab1)), collapse = ", "), "\n", sep = "")
cat("live resp set: ", paste(sort(s$resp), collapse = ","), "\n", sep = "")
resp_ok <- identical(sort(as.numeric(s$resp)), c(0, 1, 2, 3, 4))

# Storage direction: PSS_Sum1 in the .sav equals the RAW column sum, not the
# canonically reverse-scored one -- so the live table stores raw, unreversed values.
raw <- rowSums(sapply(items, function(v) as.numeric(sav[[v]])))
rev <- raw
for (i in c(4, 5, 7, 8)) rev <- rev - as.numeric(sav[[paste0("PSS", i)]]) +
                                 (4 - as.numeric(sav[[paste0("PSS", i)]]))
cat(sprintf("PSS_Sum1 == raw sum: %d/%d ; == canonically reversed sum: %d/%d\n",
            sum(sav$PSS_Sum1 == raw, na.rm = TRUE), nrow(sav),
            sum(sav$PSS_Sum1 == rev, na.rm = TRUE), nrow(sav)))

cat("\nNote: this establishes only that the IRW item codes are the source column\n",
    "names verbatim and that the 0-4 anchor coding is the .sav's own value-label\n",
    "coding. It establishes NO item_text mapping, because this table is BLOCKED on\n",
    "the PSS rights ruling and no item text was written or uploaded.\n", sep = "")

cat(if (n_ok == 10 && resp_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
