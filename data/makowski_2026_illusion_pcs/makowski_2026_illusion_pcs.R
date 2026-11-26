## Makowski, D., & Neves, A. (2026). Testing the Relationship between
## Phenomenological Control related to Illusion Sensitivity: data, analysis code
## and materials (Stage 2 Registered Report). Zenodo.
## doi:10.5281/zenodo.23943901 (record 23946919, v1.1). Licence: CC BY 4.0.
## Repo: github.com/RealityBending/IllusionGamePhenomenologicalControl;
## preprint psyarxiv 873th. Psychophysics collection, irw#3686.
##
## Task: the Illusion Game (Makowski et al., 2023), online (Prolific). Speeded
## judgements on Ebbinghaus, Mueller-Lyer and Vertical-Horizontal illusions;
## illusion strength (positive = incongruent, biasing towards the wrong answer;
## negative = congruent; README) crossed with the objective difference between
## the targets. Each illusion: blocks A and B of 80 trials, 160 cells, each seen
## once by every participant -- a fixed, fully crossed grid of 480 items.
## Same task as makowski_2024_illusion (OpenNeuro ds004587), but a different
## stimulus grid and sample, so a separate table.
##
## Source: data/rawdata_illusion.csv (500 people x 480 trials) and
## data/rawdata_participants.csv. Everyone recruited is kept; the authors'
## samples are flagged from data_participants.csv (registered analysis, N = 295)
## and data_participants_unregistered.csv (sensitivity analysis, N = 468).
##
## Layout (as makowski_2024_illusion):
##   item  = illusion x strength x difference, e.g. mullerlyer_s21_d0.45;
##           negative values spelled "neg"
##   resp  = 1 if correct (`Response_Correct`)
##   rt    = seconds (source already in seconds)
##   trial_block = 1 (A) or 2 (B); trial_in_block = 1-80 within illusion x block
##   trial_isi   = inter-stimulus interval in seconds
##   cov_age, cov_female (NA for "Other"), cov_education, cov_ethnicity,
##   cov_student, cov_incl_registered, cov_incl_sensitivity
##   itemcov_strength, itemcov_difference
## Dropped: browser, platform, screen size, start date and duration; the PCS,
## PID-5 and IPIP-6 questionnaire items (not psychophysics); response key.
## Participant codes S001-S500 are remapped to integers.
##
## Usage: Rscript makowski_2026_illusion_pcs.R <archive data/ dir> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "data"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

x <- read.csv(file.path(raw_dir, "rawdata_illusion.csv"), stringsAsFactors = FALSE)
p <- read.csv(file.path(raw_dir, "rawdata_participants.csv"), stringsAsFactors = FALSE)
reg <- read.csv(file.path(raw_dir, "data_participants.csv"), stringsAsFactors = FALSE)$Participant
sens <- read.csv(file.path(raw_dir, "data_participants_unregistered.csv"), stringsAsFactors = FALSE)$Participant
stopifnot(length(unique(x$Participant)) == 500, all(table(x$Participant) == 480),
          length(reg) == 295, length(sens) == 468,
          all(x$Response_Correct %in% c("true", "false")))

lab <- c(Ebbinghaus = "ebbinghaus", MullerLyer = "mullerlyer",
         VerticalHorizontal = "verticalhorizontal")
num <- function(v) paste0(ifelse(v < 0, "neg", ""),
                          sub("\\.?0+$", "", formatC(abs(v), format = "f", digits = 3)))
x$item <- sprintf("%s_s%s_d%s", lab[x$Illusion_Type], num(x$Illusion_Strength),
                  num(x$Illusion_Difference))
stopifnot(length(unique(x$item)) == 480, !any(duplicated(x[, c("Participant", "item")])))

subs <- sort(unique(x$Participant))
m <- match(x$Participant, p$Participant)
stopifnot(!any(is.na(m)))
d <- data.frame(
  id = match(x$Participant, subs),
  item = x$item,
  resp = as.integer(x$Response_Correct == "true"),
  rt = as.numeric(x$RT),
  trial_block = c(A = 1L, B = 2L)[x$Block],
  trial_in_block = as.integer(x$Trial),
  trial_isi = as.numeric(x$ISI),
  cov_age = as.integer(p$Age[m]),
  cov_education = p$Education[m],
  cov_ethnicity = p$Ethnicity[m],
  cov_female = c(Female = 1L, Male = 0L, Other = NA)[p$Gender[m]],
  cov_incl_registered = as.integer(x$Participant %in% reg),
  cov_incl_sensitivity = as.integer(x$Participant %in% sens),
  cov_student = as.integer(as.logical(p$Student[m])),
  itemcov_difference = as.numeric(x$Illusion_Difference),
  itemcov_strength = as.numeric(x$Illusion_Strength),
  stringsAsFactors = FALSE)
d <- d[order(d$id, x$Illusion_Type, d$trial_block, d$trial_in_block), ]
table <- "makowski_2026_illusion_pcs"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
pp <- d[!duplicated(d$id), ]
cat(sprintf("%s rows=%d ids=%d items=%d registered=%d sensitivity=%d mean_resp=%.3f congruent=%.3f incongruent=%.3f\n",
            table, nrow(d), length(unique(d$id)), length(unique(d$item)),
            sum(pp$cov_incl_registered), sum(pp$cov_incl_sensitivity), mean(d$resp),
            mean(d$resp[d$itemcov_strength < 0]), mean(d$resp[d$itemcov_strength > 0])))
