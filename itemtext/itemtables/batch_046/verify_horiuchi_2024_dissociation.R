# verify_horiuchi_2024_dissociation.R -- Step 5b mapping check.
#
# CLAIM UNDER TEST: the live item code `dissocN` carries the text of Child
# Dissociative Checklist (CDC) v3 item N, as numbered in the paper's own
# questionnaire supplement (10.1371/journal.pone.0298214.s003) and in Putnam's
# published CDC v3 form (identical order, checked item for item).
#
# The item codes ARE the raw file's column names (data/horiuchi_2024_maltreatment_scales.py
# melts the columns whose name starts with "dissoc"; no rename, no positional
# assignment), so the risk is not a shifted range -- it is that the study
# numbered its columns in an administration order different from the CDC's
# published order. Nothing in the raw file (which carries no item text) can
# settle that, so this script tests it against ITEM CONTENT.
#
# Pre-specified content grouping, fixed from the CDC wording BEFORE looking at
# any mean, on one criterion: could a Japanese homeroom teacher / orphanage
# staff member, rating a 6-12 year old over the past 12 months, plausibly
# observe this behaviour at all?
#
#   SEVERE/UNOBSERVABLE (must be at the floor): 10 (speaks of self in the third
#     person / different name), 13 (unexplained injuries, self-injury), 14
#     (hears voices), 15 (vivid imaginary companion), 17 (sleepwalks -- a
#     teacher never sees this), 18 (unusual nighttime experiences -- likewise),
#     19 (talks to self in a different voice), 20 (two or more distinct
#     personalities -- the CDC's most severe item, must be the rarest of all).
#   OBSERVABLE CLASSROOM BEHAVIOUR (must sit at the top): 2 (dazes / "spaced
#     out", the item whose own wording says teachers report it), 8 (does not
#     learn from normal discipline), 9 (goes on lying or denying despite
#     obvious evidence).
#
# Predictions, in order of strength:
#   P1  all 8 severe items have a lower mean than all 3 observable items.
#       Under a random relabelling of the 20 codes: p = 1/C(11,3) = 1/165 = 0.006.
#   P2  dissoc20 is the single lowest mean of all 20 items (p = 1/20 = 0.05).
#   P3  the only two items on which NO respondent ever used resp = 2 are 17 and
#       20 -- the two whose content a teacher can least ever rate "very true"
#       (p = 1/C(20,2) = 1/190 for that exact pair).
#   P4  dissoc1 is the only item with a missing response (n = 213 vs 214), and
#       item 1 is the only CDC item that presupposes trauma "known to have
#       occurred" -- unanswerable for a control child.
#
# DATA. Live per-item n and resp ranges come from irw::irw_table_sets(), which is
# server-side and exports nothing. The per-item MEANS are computed from the
# study's own raw supplement (S7 Table, .s008), which is the file the IRW
# processing script reads; the script first proves that file is the live table's
# source by reconciling per-item n and resp range against irw_table_sets().
# This deliberately avoids irw_fetch(), which would export the whole table.
#
# WHAT THIS DOES NOT ESTABLISH: it does not separate items WITHIN either group,
# and several means are tied outright (dissoc3 and dissoc11 both 0.1308). The
# status recorded for this table is therefore PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "horiuchi_2024_dissociation"
URL   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0298214.s008"

SEVERE     <- c(10, 13, 14, 15, 17, 18, 19, 20)
OBSERVABLE <- c(2, 8, 9)

## ---- raw source file -------------------------------------------------------
f <- file.path(tempdir(), "horiuchi_s008.xlsx")
if (!file.exists(f)) download.file(URL, f, mode = "wb", quiet = TRUE)
raw <- suppressMessages(readxl::read_excel(f, skip = 2))
cols <- grep("^dissoc", names(raw), value = TRUE)
stopifnot(length(cols) == 20)

stat <- do.call(rbind, lapply(cols, function(c) {
    v <- suppressWarnings(as.numeric(raw[[c]])); v <- v[!is.na(v)]
    data.frame(item = c, n = length(v), mean = mean(v), max = max(v))
}))
stat$num <- as.integer(sub("dissoc", "", stat$item))
stat <- stat[order(stat$num), ]

## ---- reconcile the raw file against the live table (no export) -------------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- as.data.frame(s$per_item)
m <- merge(stat, live, by = "item", suffixes = c("_raw", "_live"))
n_ok   <- all(m$n_raw == m$n)
max_ok <- all(m$max == m$resp_max)
cat("-- raw supplement .s008 vs live irw_table_sets() --\n")
cat(sprintf("per-item n identical for all %d items: %s\n", nrow(m), n_ok))
cat(sprintf("per-item resp max identical for all %d items: %s\n", nrow(m), max_ok))
if (!(n_ok && max_ok)) {
    print(m[m$n_raw != m$n | m$max != m$resp_max, ])
    cat("VERDICT: FAIL\n"); quit(save = "no")
}

## ---- the content predictions ----------------------------------------------
cat("\n-- per-item mean, ascending (from the raw supplement) --\n")
o <- stat[order(stat$mean), ]
grp <- ifelse(o$num %in% SEVERE, "severe", ifelse(o$num %in% OBSERVABLE, "observable", "."))
for (i in seq_len(nrow(o)))
    cat(sprintf("%-9s mean %.4f  floor %5.1f%%  max %d  %s\n",
                o$item[i], o$mean[i],
                100 * mean(suppressWarnings(as.numeric(raw[[o$item[i]]])) == 0, na.rm = TRUE),
                o$max[i], grp[i]))

sev <- stat$mean[stat$num %in% SEVERE]
obs <- stat$mean[stat$num %in% OBSERVABLE]
p1 <- max(sev) < min(obs)
cat(sprintf("\nP1  max(severe)=%.4f < min(observable)=%.4f : %s   (p=1/165 under relabelling)\n",
            max(sev), min(obs), p1))

p2 <- stat$item[which.min(stat$mean)] == "dissoc20"
cat(sprintf("P2  lowest-mean item is %s (mean %.4f), expected dissoc20 : %s\n",
            stat$item[which.min(stat$mean)], min(stat$mean), p2))

no2 <- sort(stat$num[stat$max < 2])
p3 <- identical(as.integer(no2), c(17L, 20L))
cat(sprintf("P3  items never scored 2: {%s}, expected {17, 20} : %s\n",
            paste(no2, collapse = ", "), p3))

p4 <- identical(stat$item[stat$n < max(stat$n)], "dissoc1")
cat(sprintf("P4  only item with a missing response: %s, expected dissoc1 : %s\n",
            paste(stat$item[stat$n < max(stat$n)], collapse = ", "), p4))

cat("\nNot established: order WITHIN the severe block and WITHIN the observable\n",
    "block. dissoc3 and dissoc11 tie at 0.1308, so no route here separates them.\n",
    "Recorded status is PARTIAL.\n", sep = "")

cat(if (p1 && p2 && p3 && p4) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
