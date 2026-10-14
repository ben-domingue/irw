##Factorial vignette (one Facebook-style news post per respondent) from
##Calvo, E., Aruguete, N., & Alvarado, J. D. (2026). Framing and news sharing behavior: the use of
##confirmation and refutation statements in the election of a right-wing populist leader.
##Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-026-08888-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/AJOL9E, CC0 1.0. File read:
##"AAC-NatureHSSC-Survey Eleccion Presidencial Argentina 2023-Noviembre 20 2023-iLCSS.tab" (tab version of the
##authors' .dta; 2,075 x 467). Codebook AAC_MileiExperiment_Codebook.pdf, SIF AAC_MileiExperiment_SIF.pdf (Table 2),
##analysis code AAC_Replication_Models_Final.R (all read as text).
##Usage: Rscript calvo_2026.R <dir holding the .tab renamed or not> <output dir>   (the single *.tab in the dir is read)
##
##Netquest panel, adults in Argentina, fielded 20 Nov 2023, the day after the Massa-Milei runoff. 2,075 rows, of
##which 2,044 were assigned to one of eight posts (tratamientoMilei_encode non-missing); the 31 unassigned are dropped
##(they have no attributes). Each respondent saw ONE post, so 1 task x 1 profile; id = row order of the kept rows.
##2x2x2 randomization (codebook sec. 4): candidate (posteoMilei: 1 = Milei, 0 = Massa), the claim (negation: 0 = "can
##control inflation", 1 = "cannot control"), and the label (falso: 0 = "It is TRUE that", 1 = "It is FALSE that").
##The coding was verified against SIF Table 3 arm counts. Level text is the English translation of the posts given in SIF Table 2
##("It is TRUE that Javier Milei can control Argentina's inflation" ...); the Spanish post wording is only in the
##fielded-instrument PDF, which is not deposited with the data in this form. Level text is therefore translated.
##Outcomes (all 0/1, stored as `rating_*`, since they are judgements of the one post and not a pick among profiles):
##  behaviour, "would you 'like', 'share', 'reply' or 'ignore' the Facebook post?" (like, share and reply can be
##  combined; ignore is exclusive): rating_like (E1_like), rating_share (E1_rt), rating_comment (E1_reply),
##  rating_ignore (E1_ignore);
##  affect, how the post made them feel, one of Ekman's categories or "indifferent" (single choice): rating_optimism
##  (E1_optimist), rating_joy (E1_happy), rating_anger (E1_angry), rating_sadness (E1_sad), rating_stress
##  (E1_stressed), rating_fear (E1_fearful), rating_disgust (E1_disgust), rating_indifferent (E1_NoSentiment).
##The exact Spanish question text is not in the deposit; design_outcomes carries the English wording of the SIF.
##Drops: derived engage / positive / negative / true / congruenteballotage, reading and reaction times except the log
##reading time, ideological placement of candidates, province, ethnic/religion/discrimination batteries.
##Dropped for privacy: IPAddress, LocationLatitude/Longitude, ResponseId, RecipientEmail/Name (empty), start/end dates.
##Covariates: cov_gender (Genero via the authors' `woman`: 1 woman, 0 man; Genero codes 4 and 6 (5 respondents) are
##NA, not documented), cov_age_group (Edad_bis band text), cov_education_code (Education, codes 1-9, no mapping in
##the deposit), cov_vote_first_round (general, text; blank = none), cov_vote_runoff (segunda_encode, codebook sec. 5:
##1 blank or null, 2 Massa, 3 Milei), cov_ideology (1-7 left to right, 512 missing), cov_log_read_time (lnTimeE1, log
##seconds on the post; recorded after assignment), trial_prior_umbrella_experiment (exposedtoUmbrella; an earlier,
##unrelated stressor experiment).
##Survey weight: `weight_var` is in the file but undocumented, unused by the authors, 180 missing and up to 449: not kept.
##Count check: 2,044 assigned = SIF Table 3 total; arm sizes equal SIF Table 3. The authors' regressions use 1,901
##(complete cases on runoff vote); this table keeps all 2,044. Reproduced: like/share/reply means on the 1,901 sample
##0.147/0.099/0.084 (codebook sec. 3).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.tab$", full.names = TRUE); stopifnot(length(f) == 1)
d <- fread(f)
d <- d[!is.na(tratamientoMilei_encode)]
stopifnot(nrow(d) == 2044, all(d$falso %in% 0:1), all(d$negation %in% 0:1), all(d$posteoMilei %in% 0:1))
cand <- c("Sergio Massa", "Javier Milei")[d$posteoMilei + 1L]
claim <- c("can control Argentina's inflation", "cannot control Argentina's inflation")[d$negation + 1L]
lab <- c("It is TRUE that", "It is FALSE that")[d$falso + 1L]
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
                rating_like = d$E1_like, rating_share = d$E1_rt, rating_comment = d$E1_reply, rating_ignore = d$E1_ignore,
                rating_optimism = d$E1_optimist, rating_joy = d$E1_happy, rating_anger = d$E1_angry, rating_sadness = d$E1_sad,
                rating_stress = d$E1_stressed, rating_fear = d$E1_fearful, rating_disgust = d$E1_disgust,
                rating_indifferent = d$E1_NoSentiment,
                attr_candidate = cand, attr_claim = claim, attr_label = lab)
r[, cov_gender := c("male", "female")[d$woman + 1L]]
r[, cov_age_group := d$Edad_bis][cov_age_group == "More than 65", cov_age_group := "65+"][cov_age_group == "", cov_age_group := NA]
r[, cov_education_code := as.integer(d$Education)]
r[, cov_vote_first_round := d$general][cov_vote_first_round == "", cov_vote_first_round := NA]
r[, cov_vote_runoff := c("Blank or null", "Massa", "Milei")[d$segunda_encode]]
r[, cov_ideology := as.integer(d$ideology)]
r[, cov_log_read_time := d$lnTimeE1]
r[, trial_prior_umbrella_experiment := as.integer(d$exposedtoUmbrella)]
stopifnot(all(unlist(r[, grep("^rating", names(r)), with = FALSE]) %in% 0:1))
print(r[, .N, .(attr_candidate, attr_claim, attr_label)])
print(colMeans(r[!is.na(cov_vote_runoff), grep("^rating", names(r)), with = FALSE]))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "calvo_2026_milei_framing.csv"))
