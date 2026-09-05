# verify_enkavi_2019_stopsignal.R
#
# What is shipped for this table, and therefore what has to be verified.
#
# enkavi_2019_stopsignal is a picture-stimulus task: the four stimuli are
# abstract shape images (pentagon/hourglass/tear/square .png) rendered as <img>
# tags by expfactory-experiments/stop_signal/experiment.js, so `item_text` is
# BLANK by design under the 2026-09-05 picture-stimulus ruling
# (references/itemtext_standard.md), following twod_rotation_mather2023.
# `correct_response` is blank too: experiment.js shuffles the shape->key
# assignment per session, so no single key is correct for a shape.
#
# That leaves exactly one mapping with any inference in it, and it is the
# option axis: `option_text` claims resp==1 is "Correct" and resp==0 is
# "Incorrect".  This script verifies THAT, plus the item axis, by Step 5b
# route 9 in its strongest form -- rebuilding `item` and `resp` from the raw
# Self-Regulation Ontology deposit exactly as data/enkavi_2019_conflict_tasks.py
# does, and comparing per-item n AND per-item number-of-correct against the
# live table, cell for cell.
#
# It does NOT re-check item counts as such: matching n alone would prove
# nothing beyond what validate_items.R already did.  The evidence is the
# per-item CORRECT COUNT.  A flipped option mapping (Correct<->Incorrect)
# would leave every n unchanged and break all 16 correct counts (live
# n_correct/n runs 0.44-0.94, nowhere near 0.5, so the flip is not degenerate).
#
# Reproduction of `item` from the source's own `condition`, `SS_trial_type`
# and shape-filename values is a side effect: if the item codes were permuted,
# the per-item n and n_correct would not line up either.

TABLE <- "enkavi_2019_stopsignal"

RAW <- c(
  wave1 = paste0("https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/",
                 "master/Data/Complete_02-16-2019/Individual_Measures/stop_signal.csv.gz"),
  wave2 = paste0("https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/",
                 "master/Data/Retest_02-16-2019/Individual_Measures/stop_signal.csv.gz"))

CACHE <- c(wave1 = file.path(".cache", TABLE, "stop_signal.csv.gz"),
           wave2 = file.path(".cache", TABLE, "stop_signal_retest.csv.gz"))

## ---- rebuild item/resp from the raw deposit --------------------------------
# Mirrors _clean() + _prep_stopsignal() in data/enkavi_2019_conflict_tasks.py:
#   test-stage rows only; resp = the source `correct` column coerced to 0/1
#   with anything else dropped; item = condition_SStrialtype_shapeid, where
#   shape_id is the PNG stem extracted from the `stimulus` <img> tag.
rebuild <- function(path, url) {
  if (!file.exists(path)) {
    dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
    download.file(url, path, quiet = TRUE, mode = "wb")
  }
  d <- read.csv(gzfile(path), stringsAsFactors = FALSE)
  d <- d[d$exp_stage == "test", ]
  co <- d$correct
  if (is.logical(co)) co <- as.integer(co)
  d$resp <- suppressWarnings(as.numeric(co))
  d <- d[!is.na(d$resp) & d$resp %in% c(0, 1) & !is.na(d$worker_id) & d$worker_id != "", ]
  d$shape_id <- sub(".*/([A-Za-z0-9_]+)\\.png.*", "\\1", d$stimulus)
  d$item <- paste(d$condition, d$SS_trial_type, d$shape_id, sep = "_")
  d[, c("item", "resp")]
}

raw <- do.call(rbind, Map(rebuild, CACHE, RAW))
cat("raw rebuilt rows (both waves, test stage, resp in {0,1}):", nrow(raw), "\n\n")

src <- data.frame(item = sort(unique(raw$item)), stringsAsFactors = FALSE)
src$n         <- as.integer(tapply(raw$resp, raw$item, length)[src$item])
src$n_correct <- as.integer(tapply(raw$resp, raw$item, sum)[src$item])

## ---- live per-item aggregate, server-side ----------------------------------
# 403,800 rows; a full irw_fetch() export counts against the 200GB/30-day cap,
# so the aggregate is computed by query and only 16 rows come back.
live <- tryCatch({
  suppressMessages(library(redivis))
  q <- redivis::query(paste(
    "select item, count(*) as n, sum(resp) as n_correct",
    "from `datapages.item_response_warehouse_3:5xaj.enkavi_2019_stopsignal`",
    "group by item order by item"))
  as.data.frame(q$to_data_frame())
}, error = function(e) { message("redivis query failed: ", conditionMessage(e)); NULL })

if (is.null(live)) {
  suppressMessages(library(irw))
  d <- as.data.frame(irw::irw_fetch(TABLE))
  r <- as.numeric(d$resp); it <- as.character(d$item)
  live <- data.frame(item = sort(unique(it)), stringsAsFactors = FALSE)
  live$n         <- as.integer(tapply(r, it, length)[live$item])
  live$n_correct <- as.integer(tapply(r, it, sum)[live$item])
}
live <- live[order(live$item), ]
live$n <- as.integer(live$n); live$n_correct <- as.integer(live$n_correct)

## ---- compare ---------------------------------------------------------------
m <- merge(src, live, by = "item", suffixes = c("_raw", "_live"))
m$d_n  <- m$n_raw - m$n_live
m$d_nc <- m$n_correct_raw - m$n_correct_live
m$p_correct_live <- round(m$n_correct_live / m$n_live, 4)

cat("per-item comparison, raw SRO deposit vs live IRW table:\n")
print(m[, c("item", "n_raw", "n_live", "d_n",
            "n_correct_raw", "n_correct_live", "d_nc", "p_correct_live")],
      row.names = FALSE)

items_ok   <- setequal(src$item, live$item) && nrow(m) == 16
n_ok       <- all(m$d_n == 0)
correct_ok <- all(m$d_nc == 0)

cat("\nitems matched:", nrow(m), "of 16 | max |diff n|:", max(abs(m$d_n)),
    "| max |diff n_correct|:", max(abs(m$d_nc)), "\n")

## ---- the flip that this rules out ------------------------------------------
# If option_text were reversed (resp 1 = "Incorrect"), the raw count of
# correct trials would have to equal the live count of resp==0 trials.
flip_gap <- abs(m$n_correct_raw - (m$n_live - m$n_correct_live))
cat("\nunder the FLIPPED reading (resp 1 = Incorrect), per-item discrepancy:\n")
print(setNames(flip_gap, m$item))
cat("min discrepancy under the flip:", min(flip_gap),
    "(0 would mean the flip is indistinguishable)\n")
flip_ruled_out <- min(flip_gap) > 0

## ---- corroboration: go vs stop accuracy ------------------------------------
# Independent of the counts: on a stop trial the required response is to
# withhold, so accuracy must be far lower than on go trials.  If resp==1 meant
# "Incorrect" this ordering would invert.
go   <- m[grepl("_go_",   m$item), ]
stp  <- m[grepl("_stop_", m$item), ]
cat("\nmean p(resp==1) over the 8 go items  :", round(mean(go$p_correct_live), 4), "\n")
cat("mean p(resp==1) over the 8 stop items:", round(mean(stp$p_correct_live), 4), "\n")
cat("(go > stop is what accuracy looks like; the reverse would indicate resp==1 = Incorrect)\n")
ordering_ok <- min(go$p_correct_live) > max(stp$p_correct_live)
cat("min go p =", round(min(go$p_correct_live), 4),
    "> max stop p =", round(max(stp$p_correct_live), 4), ":", ordering_ok, "\n")

cat("\n")
cat("items_ok:", items_ok, "| n_ok:", n_ok, "| correct_ok:", correct_ok,
    "| flip_ruled_out:", flip_ruled_out, "| ordering_ok:", ordering_ok, "\n")

if (items_ok && n_ok && correct_ok && flip_ruled_out && ordering_ok) {
  cat("VERDICT: PASS\n")
} else {
  cat("VERDICT: FAIL\n")
}
