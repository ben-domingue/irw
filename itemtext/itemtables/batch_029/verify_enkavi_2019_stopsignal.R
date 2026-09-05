# verify_enkavi_2019_stopsignal.R
#
# enkavi_2019_stopsignal is a BLOCKED table: no item text was shipped, so there
# is no item-to-text mapping to re-run. What this script re-runs is the
# substantive claim the block rests on -- that the stop-signal task's four
# stimuli are abstract shape images whose response mapping is counterbalanced
# per participant, so no item wording and no correct_response exist to ship.
#
# Two falsifiable predictions, both checked against the SRO raw deposit:
#   (1) Within a worker, each shape has exactly ONE correct key. Across
#       workers, each shape takes BOTH keys (M=77 / Z=90) at roughly 50/50 --
#       i.e. correct_response is a per-session shuffle, not a property of the
#       item, matching expfactory-experiments/stop_signal/experiment.js's
#       jsPsych.randomization.shuffle(possible_responses...).
#   (2) `condition` (high/low), which data/enkavi_2019_conflict_tasks.py carries
#       through as itemcov_delay, is actually stop-signal FREQUENCY: the high
#       blocks are 40% stop trials and the low blocks 20%, with SS_delay a
#       separate column. This is why the live per-item n splits 30k/20k for
#       high_go/high_stop and 40k/10k for low_go/low_stop.
#
# Neither prediction has anything to do with item counts -- validate_items.R was
# never run for this table, because no CSV was written.

URL <- paste0("https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/",
              "master/Data/Complete_02-16-2019/Individual_Measures/stop_signal.csv.gz")

f <- file.path(tempdir(), "stop_signal.csv.gz")
if (!file.exists(f)) download.file(URL, f, quiet = TRUE, mode = "wb")
d <- read.csv(gzfile(f), stringsAsFactors = FALSE)

t <- d[d$exp_stage == "test", ]
t$shape <- sub(".*/([A-Za-z0-9_]+)\\.png.*", "\\1", t$stimulus)
t <- t[t$shape %in% c("pentagon", "hourglass", "tear", "square"), ]

cat("test-stage rows:", nrow(t), " workers:", length(unique(t$worker_id)), "\n\n")

## (1) response-key counterbalancing --------------------------------------
k <- t[!is.na(t$correct_response), ]
cells <- tapply(k$correct_response, list(k$worker_id, k$shape),
                function(x) length(unique(x)))
cells <- cells[!is.na(cells)]
cat("worker x shape cells:", length(cells),
    "| cells with exactly 1 correct key:", sum(cells == 1), "\n")

ct <- table(k$shape, k$correct_response)
cat("\nshape x correct_response (77 = M key, 90 = Z key), pooled over workers:\n")
print(ct)
pooled_ok <- all(apply(ct, 1, function(r) sum(r > 0) == 2))
share <- ct[, "77"] / rowSums(ct)
cat("\nshare of trials where the M key is correct, by shape:\n")
print(round(share, 3))
cat("(each near 0.5 => the shape->key tie is a per-session shuffle, not item content)\n")

within_ok <- all(cells == 1)

## (2) condition = stop-signal FREQUENCY, not delay ------------------------
cat("\ncondition x SS_trial_type trial counts:\n")
tab <- table(t$condition, t$SS_trial_type)
print(tab)
stop_share <- tab[, "stop"] / rowSums(tab)
cat("\nstop-trial share by condition:\n")
print(round(stop_share, 3))
cat("median SS_delay by condition (ms), for contrast:\n")
print(tapply(as.numeric(t$SS_delay), t$condition, median, na.rm = TRUE))
freq_ok <- abs(stop_share[["high"]] - 0.40) < 0.01 && abs(stop_share[["low"]] - 0.20) < 0.01

cat("\nWhat this does NOT establish: nothing about item-to-wording correspondence,\n",
    "because no wording exists for these four abstract shape images and none was\n",
    "shipped. It establishes only that correct_response is unshippable (randomised\n",
    "per participant) and that the high/low half of the item code names stop-signal\n",
    "frequency rather than delay.\n", sep = "")

cat(sprintf("\nchecks: within-worker-unique-key=%s pooled-both-keys=%s frequency-40/20=%s\n",
            within_ok, pooled_ok, freq_ok))
cat(if (within_ok && pooled_ok && freq_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
