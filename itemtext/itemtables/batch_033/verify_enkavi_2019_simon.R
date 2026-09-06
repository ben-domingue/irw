# verify_enkavi_2019_simon.R  (batch_033)
#
# This table SHIPS under the picture-stimulus ruling (itemtext_standard.md,
# "Picture-stimulus tasks: ship the table, leave item_text blank", 2026-09-05):
# the Simon stimulus is an untexted coloured <div> box, so `item_text` is blank
# by design and the table carries what the source does publish -- the task's own
# instructions, the per-item correct key, and the accuracy labels behind resp.
#
# What must therefore be verified is NOT an item_text<->item mapping (there is no
# item text, and none can exist for this task) but the two mappings the file does
# assert:
#
#   A. item <-> stimulus condition + correct key. `item` is built by
#      data/enkavi_2019_conflict_tasks.py as stim_color_stim_side_condition from
#      the raw Self-Regulation Ontology simon.csv.gz; the shipped
#      `correct_response` claims congruent -> the arrow on the same side as the
#      box, incongruent -> the opposite arrow.
#   B. resp <-> option_text. resp is trial accuracy; the file labels 1 "Correct"
#      and 0 "Incorrect".
#
# Route: re-run the processing script's item construction over the raw deposit
# (SKILL.md core model 3, the strongest available) + route 8 (semantic coherence,
# the Simon effect) + route 9 (response-frequency/label matching, for B).
# Live counts come from irw::irw_table_sets() -- a server-side aggregate, so no
# Redivis export quota is spent; the raw GitHub files are the only bulk fetch.
#
# WHAT THIS DOES NOT ESTABLISH: any wording, because the task publishes none. It
# also cannot pin which arrow key an individual participant used for red vs blue
# (the [KEY FOR RED]/[KEY FOR BLUE] tokens in `instructions`): experiment.js
# shuffles that pair per participant, which is exactly why the shipped key is
# stated per item code rather than per colour.

suppressMessages(library(irw))

TABLE <- "enkavi_2019_simon"
BASE  <- "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data"
DIRS  <- c("Complete_02-16-2019", "Retest_02-16-2019")
SHIPPED <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                     "enkavi_2019_simon__items.csv")

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
          "correct", "correct_response", "key_press", "worker_id")]
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

cat("CLAIM 3 -- the shipped correct_response equals the raw file's own key, per item\n")
ship <- utils::read.csv(SHIPPED, stringsAsFactors = FALSE)
KEYNAME <- c("37" = "left arrow", "39" = "right arrow")
ok3 <- TRUE
cat(sprintf("%-24s %14s %14s %10s %s\n", "item", "raw keycode", "raw label", "purity", "shipped"))
for (it in names(acc)) {
    obs <- unique(d$correct_response[d$item == it])
    purity <- mean(d$correct_response[d$item == it] == obs[1])
    lab <- KEYNAME[[as.character(obs[1])]]
    shp <- unique(ship$correct_response[ship$item == it])
    good <- length(obs) == 1 && length(shp) == 1 && identical(lab, shp)
    ok3 <- ok3 && good
    cat(sprintf("%-24s %14s %14s %10.4f %s  %s\n", it, paste(obs, collapse = ","), lab,
                purity, shp, if (good) "ok" else "MISMATCH"))
}
cat("\n")

cat("CLAIM 4 -- resp 1 = 'Correct', resp 0 = 'Incorrect' (route 9, label<->integer)\n")
d$match <- suppressWarnings(as.numeric(d$key_press)) == suppressWarnings(as.numeric(d$correct_response))
tb <- table(resp = d$resp, key_matches_correct_key = d$match)
print(tb)
p1 <- mean(d$match[d$resp == 1], na.rm = TRUE)
p0 <- mean(d$match[d$resp == 0], na.rm = TRUE)
cat(sprintf("=> P(key = correct key | resp=1) = %.4f ; P(key = correct key | resp=0) = %.4f\n", p1, p0))
lab1 <- unique(ship$option_text[ship$resp == 1]); lab0 <- unique(ship$option_text[ship$resp == 0])
cat(sprintf("   shipped labels: resp=1 -> '%s' ; resp=0 -> '%s'\n\n",
            paste(lab1, collapse = ","), paste(lab0, collapse = ",")))
ok4 <- isTRUE(all.equal(p1, 1)) && isTRUE(all.equal(p0, 0)) &&
       identical(lab1, "Correct") && identical(lab0, "Incorrect")

cat("Note: claims 1-3 establish that each item code names exactly the stimulus\n",
    "condition it spells and carries the key the task required for it; claim 4\n",
    "establishes the accuracy labels. They establish NOTHING about item wording,\n",
    "because this task publishes none -- the stimulus is an untexted coloured box\n",
    "and item_text ships blank by design.\n", sep = "")

cat(if (ok1 && ok2 && ok3 && ok4) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
