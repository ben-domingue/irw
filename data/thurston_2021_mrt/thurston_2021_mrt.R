## Thurston, L. T., Coome, L. A., Skorska, M. N., Peragine, D. E., Saokhieo, P.,
## Kaewthip, O., Chariyalertsak, S., & VanderLaan, D. P. (2021). Mental rotation
## task performance in relation to sexual and gender diversity in Thailand.
## Psychoneuroendocrinology, 133, 105428. doi:10.1016/j.psyneuen.2021.105428
## Data: Borealis doi:10.5683/SP2/PWBUGH, ThurstonMRTDataVerse_20201220.sav
## (original format). Licence: CC0 1.0 (dataset record).
## Mental rotation collection (irw#3686 follow-up).
##
## Task: a paper-style Mental Rotation Test (Vandenberg & Kuse type), two sets
## of 10 items. On each item the participant ticks the two of four figures
## that are rotations of the target. 1,423 Thai adults.
##
## Layout:
##   item = set x item, mrt_a01 ... mrt_a10, mrt_b01 ... mrt_b10
##   resp = the depositors' standard (conservative) score: 1 if both correct
##          figures and no incorrect figure were ticked (TrialScore_MRT_v*.*)
##   Rows where the participant ticked nothing on that item
##   (ResponseCount_MRT_v*.* missing or 0) are dropped: the source scores
##   them 0, but on a timed test they are mostly not reached (set A item 10
##   was left blank by 1,030 people), so 0 would be an imputed value.
##   cov_age, cov_female (birth sex; intersex and "prefer not to answer" are
##   NA), cov_education (1-9, source codes), cov_mrt_excluded (1 = dropped
##   from the paper's MRT analysis, MRTExlusion_ALL)
##
## Dropped deliberately: every variable on sexual orientation, gender
## identity, sexual attraction, hormone use and menstrual cycle (including
## exact period dates), income, ethnicity, verbal fluency scores, the
## per-item "liberal" scores and tick counts, and the paper's group variables.
## The study's own question (rotation performance by sexual and gender
## identity) therefore cannot be reproduced from this table; those data stay
## at the source under the depositors' terms. ParticipantID is remapped.
##
## Usage: Rscript thurston_2021_mrt.R <ThurstonMRTDataVerse_20201220.sav> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
sav <- if (length(args) >= 1) args[1] else "ThurstonMRTDataVerse_20201220.sav"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

x <- haven::zap_labels(haven::read_sav(sav))
stopifnot(nrow(x) == 1423, !any(duplicated(x$ParticipantID)))

rows <- list()
for (s in 1:2) for (i in 1:10) {
  sc <- x[[sprintf("TrialScore_MRT_v%d.%d", s, i)]]
  rc <- x[[sprintf("ResponseCount_MRT_v%d.%d", s, i)]]
  answered <- !is.na(rc) & rc > 0
  stopifnot(all(sc[!answered] == 0), all(sc %in% 0:1))
  rows[[length(rows) + 1]] <- data.frame(
    pid = x$ParticipantID[answered],
    item = sprintf("mrt_%s%02d", c("a", "b")[s], i),
    resp = as.integer(sc[answered]))
}
d <- do.call(rbind, rows)
ids <- sort(unique(x$ParticipantID))
m <- match(d$pid, x$ParticipantID)
d <- data.frame(
  id = match(d$pid, ids),
  item = d$item,
  resp = d$resp,
  cov_age = as.integer(x$Age[m]),
  cov_education = as.integer(x$Education[m]),
  cov_female = c(`1` = 0L, `2` = 1L)[as.character(x$BirthSex[m])],
  cov_mrt_excluded = as.integer(x$MRTExlusion_ALL[m]),
  stringsAsFactors = FALSE)
d <- d[order(d$id, d$item), ]
table <- "thurston_2021_mrt"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d mean_resp=%.3f\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
print(round(tapply(d$resp, d$item, mean), 2))
print(table(tapply(d$item, d$id, length)))
