# verify_enkavi_2019_simon.R
#
# This table is BLOCKED: it ships NO item text, so there is no item_text<->item
# mapping in the corpus to verify, and verification_enkavi_2019_simon.csv records
# status=NO_ROUTE. The reason is determinate rather than an access failure: the
# 8 `item` codes are Simon-task STIMULUS CONDITIONS built by
# data/enkavi_2019_conflict_tasks.py as stim_color_stim_side_condition, and the
# administered stimulus -- per the study's own task code, expfactory `simon`
# (github.com/expfactory/expfactory-experiments/blob/master/simon/experiment.js)
# -- is an untexted coloured <div> box. There is no item prompt to transcribe.
#
# What this script re-runs is the evidence that the block's PREMISE is true, so a
# later ruling that reconstructed cognitive-task text is shippable needs no
# re-investigation. It is the "re-run the processing script" route (SKILL.md core
# model 3, the strongest available) plus route 8 (semantic coherence), and it
# checks THREE falsifiable claims:
#
#   1. Each item code names exactly the stimulus condition it spells: rebuilding
#      the item key from the two raw SRO files reproduces every live per-item n.
#      Live n come from irw::irw_table_sets() -- a server-side aggregate, so no
#      Redivis export quota is spent (the raw GitHub files are the bulk fetch).
#   2. The `condition` half of each code is real, not a label: congruent items
#      must be MORE accurate than incongruent ones (the Simon effect).
#   3. The per-item correct key is fully determined by the code: congruent ->
#      arrow on the same side as the box, incongruent -> opposite arrow. This is
#      the only per-item content that would be shippable if the block were lifted,
#      so it is checked here rather than asserted.
#
# WHAT THIS DOES NOT VERIFY: any item_text<->item mapping. There is none, and
# none can exist for this task. A PASS here means "the block is correctly
# reasoned", not "the shipped text is right" -- nothing is shipped.

suppressMessages(library(irw))

TABLE <- "enkavi_2019_simon"
BASE  <- "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data"
DIRS  <- c("Complete_02-16-2019", "Retest_02-16-2019")

# ---- live per-item n, via server-side aggregates (no export) -----------------
ts <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(ts$per_item)
if (is.null(ts$per_item) || !"item" %in% names(pi))
    stop("irw_table_sets() returned no per-item aggregate; inspect str(ts)")
cn <- intersect(c("n", "n_obs", "count"), names(pi))[1]
live <- setNames(as.numeric(pi[[cn]]), as.character(pi$item))

# ---- rebuild the item key from the raw source -------------------------------
raw <- do.call(rbind, lapply(DIRS, function(d) {
    u  <- file.path(BASE, d, "Individual_Measures", "simon.csv.gz")
    tf <- tempfile(fileext = ".csv.gz")
    utils::download.file(u, tf, quiet = TRUE, mode = "wb")
    x <- utils::read.csv(gzfile(tf), stringsAsFactors = FALSE)
    unlink(tf)
    x[, c("exp_stage", "stim_color", "stim_side", "condition",
          "correct", "correct_response", "worker_id")]
}))

d <- raw[raw$exp_stage == "test", ]
d$resp <- suppressWarnings(as.numeric(d$correct))
d <- d[!is.na(d$resp) & d$resp %in% c(0, 1) & !is.na(d$worker_id) & d$worker_id != "", ]
d$item <- paste(d$stim_color, d$stim_side, d$condition, sep = "_")

rec <- table(d$item)
items <- sort(union(names(rec), names(live)))

cat("CLAIM 1 -- item codes reproduce the live per-item n exactly\n")
cat(sprintf("%-24s %10s %10s %8s\n", "item", "raw", "live", "diff"))
diffs <- numeric(0)
for (it in items) {
    r <- if (it %in% names(rec)) as.numeric(rec[[it]]) else NA_real_
    l <- if (it %in% names(live)) live[[it]] else NA_real_
    diffs <- c(diffs, abs(r - l))
    cat(sprintf("%-24s %10s %10s %8s\n", it, r, l, r - l))
}
ok1 <- length(items) == 8 && all(!is.na(diffs)) && all(diffs == 0)
cat(sprintf("=> %d items, max |diff| = %s\n\n", length(items),
            if (all(!is.na(diffs))) max(diffs) else "NA"))

cat("CLAIM 2 -- the Simon effect: congruent items are more accurate\n")
acc <- tapply(d$resp, d$item, mean)
cong   <- acc[grepl("_congruent$",   names(acc))]
incong <- acc[grepl("_incongruent$", names(acc))]
for (it in names(acc)) cat(sprintf("%-24s acc = %.4f\n", it, acc[[it]]))
cat(sprintf("=> congruent range %.4f-%.4f ; incongruent range %.4f-%.4f ; gap %.4f\n\n",
            min(cong), max(cong), min(incong), max(incong), min(cong) - max(incong)))
ok2 <- length(cong) == 4 && length(incong) == 4 && min(cong) > max(incong)

cat("CLAIM 3 -- the correct key is determined by the code (37 = left arrow, 39 = right)\n")
pred <- function(it) {
    p <- strsplit(it, "_")[[1]]
    side <- p[2]; cond <- p[3]
    same <- if (side == "left") 37 else 39
    if (cond == "congruent") same else if (same == 37) 39 else 37
}
ok3 <- TRUE
for (it in names(acc)) {
    obs <- sort(unique(d$correct_response[d$item == it]))
    p <- pred(it)
    good <- length(obs) == 1 && obs[1] == p
    ok3 <- ok3 && good
    cat(sprintf("%-24s predicted %d ; observed %s ; %s\n",
                it, p, paste(obs, collapse = ","), if (good) "ok" else "MISMATCH"))
}
cat("\n")

cat("Note: this establishes that each item code names exactly the stimulus condition\n",
    "it spells. It establishes NOTHING about item_text<->item, because this task has\n",
    "no item text -- the stimulus is an untexted coloured box. That is why the table\n",
    "is blocked and the verification status is NO_ROUTE rather than VERIFIED.\n", sep = "")

cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
