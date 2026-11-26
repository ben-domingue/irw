## Gu, H., Lee, J., Kim, S., Lim, J., Lee, H.-J., Lee, H., Choe, M. J., Yoo, D.,
## Ryu, J. H., Lim, S., & Lee, S.-H. (2025). Attractor dynamics of working
## memory explain a concurrent evolution of stimulus-specific and
## decision-consistent biases in visual estimation. Neuron, 113(20), 3476-3490.
## doi:10.1016/j.neuron.2025.07.003
## Data: OpenNeuro ds005381 v1.1.0 ("Discrimination-Estimation Task"),
## doi:10.18112/openneuro.ds005381.v1.1.0. Licence: CC0 (dataset_description).
## Psychophysics collection, irw#3686 (floor of 50 people; this table has 50).
##
## Task (task-DET_events.json): an oriented grating (24 orientations, 0-172.5
## deg in 7.5-deg steps) is shown for 1.5 s; 6 s (early) or 12 s (late) after
## trial onset a reference appears at -21, -4, 0, +4 or +21 deg relative to
## the stimulus (positive = clockwise), and the participant reports whether the
## remembered stimulus was clockwise or counterclockwise of it; later they
## reproduce the stimulus orientation (estimation). Recorded during fMRI,
## several runs over sessions 2-5. Events files: sub-*/ses-*/func/
## sub-*_ses-*_task-DET_run-*_events.tsv.
##
## Layout:
##   item  = timing x reference offset, e.g. early_refneg4, late_ref21 (10 items).
##           Stimulus orientation is drawn from a fixed set but crossed with
##           the item per trial, so it is a trial column, not part of the item.
##   resp  = 1 if the participant chose "clockwise" (response_decision 1),
##           0 if "counterclockwise" (-1). The choice, not accuracy, is the
##           response, because on reference-0 trials there is no correct answer.
##   rt    = discrimination response time in seconds
##   trial_correct    = 1/0 accuracy of the choice (NA on reference-0 trials)
##   trial_stimulus   = stimulus orientation in degrees
##   trial_estimation = reproduced orientation in degrees (continuous)
##   trial_session, trial_run, trial_in_run, trial_number (order within person:
##                      session, run, trial)
##   cov_age, cov_female, cov_eye_dominance (right/left/mixed; participants.tsv)
##   itemcov_reference = reference offset in degrees; itemcov_late = 1 if late
## Dropped: rows with no discrimination response (175 of 12,084 trials); event
## timing columns. BIDS subject labels are remapped to integers.
##
## Usage: Rscript gu_2025_det.R <dir with ev/*.tsv and participants.tsv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "raw"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

fs <- sort(Sys.glob(file.path(raw_dir, "ev", "sub-*_task-DET_run-*_events.tsv")))
x <- do.call(rbind, lapply(fs, function(f) {
  d <- read.delim(f, na.strings = "n/a", stringsAsFactors = FALSE)
  b <- basename(f)
  d$sub <- sub("_ses.*", "", b)
  d$ses <- as.integer(sub(".*_ses-([0-9]+)_.*", "\\1", b))
  d$run <- as.integer(sub(".*_run-([0-9]+)_.*", "\\1", b))
  d
}))
key <- c("sub", "ses", "run", "trial")
s  <- x[x$event_type == "stimulus", c(key, "trial_type", "value_stimulus")]
dm <- x[x$event_type == "dm_task", c(key, "value_reference", "response_decision", "response_time")]
em <- x[x$event_type == "em_task", c(key, "response_estimation")]
stopifnot(!any(duplicated(s[, key])), !any(duplicated(dm[, key])), !any(duplicated(em[, key])))
t <- merge(merge(s, dm, by = key, all.x = TRUE), em, by = key, all.x = TRUE)
stopifnot(nrow(t) == nrow(s), all(t$value_reference %in% c(-21, -4, 0, 4, 21)),
          all(t$trial_type %in% c("early", "late")))
t <- t[!is.na(t$response_decision), ]
stopifnot(all(t$response_decision %in% c(-1, 1)))

p <- read.delim(file.path(raw_dir, "participants.tsv"), stringsAsFactors = FALSE)
subs <- sort(unique(t$sub))
stopifnot(length(subs) == 50, all(subs %in% p$participant_id))
m <- match(t$sub, p$participant_id)
ref <- function(v) paste0("ref", ifelse(v < 0, "neg", ""), abs(v))

t <- t[order(t$sub, t$ses, t$run, t$trial), ]
m <- match(t$sub, p$participant_id)
d <- data.frame(
  id = match(t$sub, subs),
  item = paste0(t$trial_type, "_", ref(t$value_reference)),
  resp = as.integer(t$response_decision == 1),
  rt = as.numeric(t$response_time),
  trial_correct = ifelse(t$value_reference == 0, NA,
                         as.integer(sign(-t$value_reference) == t$response_decision)),
  trial_estimation = as.numeric(t$response_estimation),
  trial_in_run = as.integer(t$trial),
  trial_number = ave(seq_len(nrow(t)), t$sub, FUN = seq_along),
  trial_run = t$run,
  trial_session = t$ses,
  trial_stimulus = as.numeric(t$value_stimulus),
  cov_age = as.integer(p$age[m]),
  cov_female = c(F = 1L, M = 0L)[p$sex[m]],
  cov_eye_dominance = c(R = "right", L = "left", M = "mixed")[p$eye_dominance[m]],
  itemcov_late = as.integer(t$trial_type == "late"),
  itemcov_reference = as.numeric(t$value_reference),
  stringsAsFactors = FALSE)
table <- "gu_2025_det"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d accuracy(ref!=0)=%.3f\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$trial_correct, na.rm = TRUE)))
print(round(tapply(d$resp, d$itemcov_reference, mean), 3))
