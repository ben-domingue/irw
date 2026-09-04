# verify_conner_2017_cesd.R
#
# What is being verified: NOT the item<->item_text tie (that is data_labels --
# the PLOS S1 .sav labels every cesd1..cesd20 variable with its full item
# wording, and data/conner_2017_fruit.py renames cesd<i> -> item<i>, a
# number-preserving rename with nothing to infer).
#
# What IS inferred, and what this script checks: the option_text <-> resp tie
# for the four positively-worded CES-D items 4, 8, 12, 16. The .sav's variable
# labels for those four say "(already reverse scored)", while the value labels
# attached to them still read 0 = "Rarely or none of the time" .. 3 = "Most or
# all of the time" -- i.e. the value labels describe the item as worded, not the
# numbers actually stored. The extraction therefore ships REVERSED anchors for
# those four items only (resp 0 = "Most or all of the time", resp 3 = "Rarely or
# none of the time"), overriding the file's own value labels.
#
# Falsifiable prediction: if the four are stored already-reversed, every one of
# them correlates POSITIVELY with the unambiguously negatively-worded core
# depression block (item6 "I felt depressed", item14 "I felt lonely", item18
# "I felt sad"). If they were stored raw, those four correlations would be
# NEGATIVE and the shipped anchors would be wrong.

suppressMessages(library(irw))

TABLE <- "conner_2017_cesd"
REV   <- c("item4", "item8", "item12", "item16")   # positively worded
CORE  <- c("item6", "item14", "item18")            # negatively worded, unambiguous

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "wave", "item", "resp")]),
             idvar = c("id", "wave"), timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
items <- paste0("item", 1:20)
w <- w[complete.cases(w[, items]), ]
core <- rowSums(w[, CORE])

cat(sprintf("n person-waves: %d\n\n", nrow(w)))
cat(sprintf("%-8s %-10s %8s %8s\n", "item", "wording", "mean", "r(core)"))
r <- setNames(numeric(length(items)), items)
for (it in items) {
    r[it] <- cor(w[[it]], core)
    cat(sprintf("%-8s %-10s %8.3f %8.3f\n", it,
                if (it %in% REV) "positive" else "negative",
                mean(w[[it]]), r[it]))
}

cat(sprintf("\nreverse-keyed four r(core): %s\n",
            paste(sprintf("%s=%.3f", REV, r[REV]), collapse = ", ")))
cat(sprintf("min r over all 20 items: %.3f\n", min(r)))

ok <- all(r[REV] > 0) && min(r) > 0

cat("Note: this pins the DIRECTION in which resp is stored for items 4/8/12/16,\n",
    "and hence that their shipped anchors must be reversed relative to the .sav's\n",
    "value labels. It does NOT distinguish item from item -- that tie comes from\n",
    "the .sav variable labels (mapping_basis=data_labels), not from this test.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
