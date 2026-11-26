## Makowski, D., Te, A. S., Kirk, S., Liang, N. Z., & Chen, S. H. A. (2025).
## IllusionGameReliability: Relationship between illusion sensitivity and
## inter-individual characteristics [data and code]. GitHub.
## https://github.com/RealityBending/IllusionGameReliability (preregistration
## https://osf.io/k4ntd). Licence: CC BY 4.0 (granted by Dominique Makowski by
## email 2026-11-25; the repository itself sets none; copy in
## irw/licenseinfo/emails/). Psychophysics collection, irw#3686.
##
## Task: the Illusion Game (as makowski_2024_illusion), online. Speeded
## judgements on Ebbinghaus, Mueller-Lyer and Vertical-Horizontal illusions;
## illusion strength (sign = direction of the biasing context; 0 = none)
## crossed with the target difference (signed by Illusion_Side). Each
## illusion: 2 blocks, 128 strength x difference cells, so a fixed, fully
## crossed grid of 384 items seen once per person per session.
##   Session 1: illusion task + a perceptual task (same judgements, no
##     illusion: strength 0, 192 signed-difference items), 500 people.
##   Session 2: the same 384-item illusion grid again, 453 of them.
## One participant whose Prolific status is CONSENT_REVOKED (Student column
## of raw_questionnaires.csv) is dropped from both tables.
##
## Tables:
##   makowski_2025_illusion_retest     data/raw_illusion1.csv + raw_illusion2.csv;
##                                     trial_session = 1/2, ids linked across
##                                     sessions, so each id x item appears twice
##                                     for people who did both sessions.
##   makowski_2025_illusion_perceptual data/raw_perceptual.csv (session 1).
##
## Layout (as makowski_2024_illusion):
##   item  = illusion x strength x signed difference, e.g.
##           ebbinghaus_s0.36_dneg0.159 ("neg" for minus)
##   resp  = 1 - Error; rt = RT (seconds, as in the source)
##   trial_session, trial_block (1/2), trial_number (Trial within block),
##   trial_isi (seconds; source ms)
##   trial_excluded_by_authors = 1 for the participant x task (and, for the
##     *_block2 lists, block 2 only) the authors removed in
##     analysis/1_Cleaning.qmd; everyone is kept here.
##   cov_age, cov_female (NA unless Male/Female), cov_education, cov_ethnicity,
##   cov_student (1 Yes, 0 No; NA for DATA_EXPIRED), cov_retest_interval_days
##   itemcov_strength, itemcov_difference (signed)
## Dropped: screen, browser and device fields, durations, nationality, the
## questionnaire items (not psychophysics), response key.
## Participant codes S001-S500 are remapped to integers (shared by both tables).
##
## Usage: Rscript makowski_2025_illusion_retest.R <repo data/ dir> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "data"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
rd <- function(f) read.csv(file.path(raw_dir, f), stringsAsFactors = FALSE)

i1 <- rd("raw_illusion1.csv"); i2 <- rd("raw_illusion2.csv"); pc <- rd("raw_perceptual.csv")
q <- rd("raw_questionnaires.csv")
stopifnot(length(unique(i1$Participant)) == 500, length(unique(i2$Participant)) == 453,
          length(unique(pc$Participant)) == 500, all(i2$Participant %in% i1$Participant),
          all(c(i1$Error, i2$Error, pc$Error) %in% 0:1), !anyDuplicated(q$Participant))

revoked <- q$Participant[q$Student == "CONSENT_REVOKED"]
stopifnot(length(revoked) == 1)
i1 <- i1[!i1$Participant %in% revoked, ]; i2 <- i2[!i2$Participant %in% revoked, ]
pc <- pc[!pc$Participant %in% revoked, ]

## authors' exclusions (analysis/1_Cleaning.qmd)
out <- list(
  Perceptual = list(all = c("S003", "S008"), b2 = c("S226", "S350")),
  Illusion_Session1 = list(all = c("S008", "S278", "S389"), b2 = c("S153", "S226", "S350")),
  Illusion_Session2 = list(all = c("S003", "S123", "S224", "S226", "S229"), b2 = character(0)))

lab <- c(Ebbinghaus = "ebbinghaus", MullerLyer = "mullerlyer",
         VerticalHorizontal = "verticalhorizontal")
num <- function(v) paste0(ifelse(v < 0, "neg", ""),
                          sub("\\.?0+$", "", formatC(abs(v), format = "f", digits = 3)))
subs <- sort(unique(c(i1$Participant, pc$Participant)))
m_sex <- c(Female = 1L, Male = 0L)

build <- function(x, session) {
  task <- x$Task[1]; stopifnot(all(x$Task == task))
  diff <- as.numeric(x$Illusion_Side) * x$Illusion_Difference
  qm <- match(x$Participant, q$Participant)
  ex <- out[[task]]
  d <- data.frame(
    id = match(x$Participant, subs),
    item = sprintf("%s_s%s_d%s", lab[x$Illusion_Type], num(x$Illusion_Strength), num(diff)),
    resp = 1L - as.integer(x$Error),
    rt = as.numeric(x$RT),
    trial_session = session,
    trial_block = as.integer(x$Block),
    trial_number = as.integer(x$Trial),
    trial_isi = x$ISI / 1000,
    trial_excluded_by_authors = as.integer(x$Participant %in% ex$all |
                                           (x$Participant %in% ex$b2 & x$Block == 2)),
    cov_age = suppressWarnings(as.integer(q$Age[qm])),
    cov_female = unname(m_sex[q$Sex[qm]]),
    cov_education = q$Education[qm],
    cov_ethnicity = q$Ethnicity[qm],
    cov_student = unname(c(Yes = 1L, No = 0L)[q$Student[qm]]),
    cov_retest_interval_days = q$Interval[qm],
    itemcov_strength = x$Illusion_Strength,
    itemcov_difference = diff,
    stringsAsFactors = FALSE)
  stopifnot(!anyDuplicated(d[, c("id", "item")]))
  d
}

tabs <- list(
  makowski_2025_illusion_retest = rbind(build(i1, 1L), build(i2, 2L)),
  makowski_2025_illusion_perceptual = build(pc, 1L))
tabs$makowski_2025_illusion_perceptual$cov_retest_interval_days <- NULL
tabs$makowski_2025_illusion_perceptual$trial_session <- NULL

for (table in names(tabs)) {
  d <- tabs[[table]]
  s <- if (is.null(d$trial_session)) rep(1L, nrow(d)) else d$trial_session
  d <- d[order(d$id, s, d$trial_block, d$trial_number), ]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f excluded_rows=%d\n", table, nrow(d),
              length(unique(d$id)), length(unique(d$item)), mean(d$resp), sum(d$trial_excluded_by_authors)))
}
print(table(q$Sex, useNA = "ifany")); print(table(q$Student, useNA = "ifany")); print(table(q$Education, useNA = "ifany"))
r <- tabs$makowski_2025_illusion_retest
print(round(tapply(r$resp, list(sub("_.*", "", r$item), r$itemcov_strength > 0, r$trial_session), mean), 2))
