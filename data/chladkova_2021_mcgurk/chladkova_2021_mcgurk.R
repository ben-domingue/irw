## Chladkova, K., Podlipsky, V. J., Nudga, N., & Simackova, S. (2021). The
## McGurk effect in the time of pandemic: Age-dependent adaptation to an
## environmental loss of visual speech cues. Psychonomic Bulletin & Review, 28,
## 992-1002. doi:10.3758/s13423-020-01852-2
## Data: OSF https://osf.io/ud8gf ("The McGurk effect in the time of pandemic"),
## file data_mcgurk2020.txt. Licence: MIT (OSF node licence, copyright
## Katerina Chladkova 2020).
## Psychophysics collection, irw#3686.
##
## Task: online audiovisual syllable identification by Czech speakers, 48
## trials each: 36 McGurk videos (auditory /ba/ dubbed onto visual /ga/; 6
## speakers x 6 tokens, Trial codes 2.<speaker><a-f>) and 12 congruent videos
## (/ba/, /da/, /ga/; Trial codes 3.1-5.7). Six response options: ba, da, ga,
## ka, pa, ta. Two between-subject sessions in 2020 (session 1 at the start of
## the Czech COVID-19 lockdown, session 2 later). One trial per person per
## stimulus.
##
## Layout:
##   item     = stimulus type x Trial code, e.g. mgrk_2.2a, gaga_3.1a
##   resp     = 1 if the response's place of articulation matches the AUDITORY
##              syllable (source percAudio for McGurk items, percCorrect for
##              congruent ones). On McGurk items resp = 0 is the illusion: a
##              fused (coronal, da/ta) or visual (dorsal, ga/ka) response.
##   resp_raw = the syllable chosen (ba, da, ga, ka, pa, ta)
##   rt       = response time in seconds from the source's `reaction` (ms,
##              measured from trial start; the source's `RT` column is offset
##              by the stimulus duration and can be negative). A `reaction`
##              of exactly 0 (about 1% of trials) is a placeholder, so NA
##   trial_number = row order within person in the source file. Rows are not
##              sorted by stimulus, so this is probably presentation order, but
##              the source does not label it as such
##   trial_fused  = 1 if a McGurk response was fused (coronal; source percFused)
##   cov_session (1/2), cov_age (NA when outside 9-100), cov_female,
##   cov_mobile (1 = phone, 0 = computer), cov_headphones, cov_prior_participation,
##   cov_kept_fullscreen, cov_student (the within-subject student group)
##   cov_incl_age  = 1 if aged 16-55 (the paper's age inclusion)
##   cov_reliable  = 1 if all 12 congruent trials were answered correctly (the
##                   paper's reliability filter; derived and checked here)
## id: `pp`, remapped to integers. Students who took part in both sessions
## (source sKaaBoth) appear under a different id in each session; the source
## gives no link, so the same person can hold two ids (cov_student = 1).
## Dropped: timestamps, browser string, the location and language fields (all
## CZ / cs).
##
## Usage: Rscript chladkova_2021_mcgurk.R <data_mcgurk2020.txt> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw <- if (length(args) >= 1) args[1] else "data_mcgurk2020.txt"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

x <- read.table(raw, sep = "\t", header = TRUE, na.strings = "N/A",
                stringsAsFactors = FALSE)
stopifnot(all(table(x$pp) == 48), !any(duplicated(x[, c("pp", "Trial")])))

mg <- x$stimType == "MGRK"
resp <- ifelse(mg, x$percAudio, x$percCorrect)
## check the auditory-match coding against place of articulation
aud_place <- c(MGRK = "lbl", BABA = "lbl", DADA = "crn", GAGA = "drs")[x$stimType]
stopifnot(all(resp == as.integer(x$respPlace == aud_place)))

## the paper's reliability flag = all congruent trials correct
cong_ok <- tapply(x$percCorrect[!mg], x$pp[!mg], sum) == 12
stopifnot(all(cong_ok[as.character(x$pp)] == (x$reliable == 1)))
stopifnot(all((x$inclAge == 1) == (x$true_age >= 16 & x$true_age <= 55)))

pps <- unique(x$pp)
d <- data.frame(
  id = match(x$pp, pps),
  item = paste0(tolower(x$stimType), "_", x$Trial),
  resp = as.integer(resp),
  resp_raw = x$answer,
  rt = ifelse(as.numeric(x$reaction) > 0, as.numeric(x$reaction) / 1000, NA),
  trial_number = ave(seq_len(nrow(x)), x$pp, FUN = seq_along),
  trial_fused = ifelse(mg, as.integer(x$percFused), NA),
  cov_age = ifelse(x$true_age >= 9 & x$true_age <= 100, as.integer(x$true_age), NA),
  cov_mobile = as.integer(x$device == "phone"),
  cov_female = as.integer(x$selected_gender == "female"),
  cov_headphones = as.integer(x$headphones == "yes"),
  cov_incl_age = as.integer(x$inclAge),
  cov_kept_fullscreen = as.integer(x$kept_fullscreen == "true"),
  cov_prior_participation = as.integer(x$priorPartic == "yes"),
  cov_reliable = as.integer(x$reliable),
  cov_session = as.integer(x$session),
  cov_student = as.integer(x$isKaaStud),
  itemcov_speaker = x$stimSpeaker,
  stringsAsFactors = FALSE)
d <- d[order(d$id, d$trial_number), ]
table <- "chladkova_2021_mcgurk"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
pp <- d[!duplicated(d$id), ]
cat(sprintf("%s rows=%d ids=%d items=%d reliable=%d incl_age=%d mcgurk_auditory=%.3f congruent_correct=%.3f\n",
            table, nrow(d), length(unique(d$id)), length(unique(d$item)),
            sum(pp$cov_reliable), sum(pp$cov_incl_age),
            mean(d$resp[grepl("^mgrk", d$item)]), mean(d$resp[!grepl("^mgrk", d$item)])))
