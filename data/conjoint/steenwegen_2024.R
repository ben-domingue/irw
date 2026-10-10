##Community-education flyer experiment (Flanders, Belgium) from
##Steenwegen, J., & Meijers, M. J. (2024). How prejudice shapes public perceptions of
##minority-organized spaces: the case of community education. Journal of Ethnic and Migration
##Studies. https://doi.org/10.1080/1369183X.2024.2333874 (open access; read via the OSF preprint
##osf.io/kcsvy, design and outcome sections)
##Replication data: Harvard Dataverse doi:10.7910/DVN/8F4UFO, CC0 1.0. File read: data.sav (original
##SPSS file, value and variable labels). Read as text only: readme.txt, exp_study.do.
##Usage: Rscript steenwegen_2024.R <dir holding data.sav> <output dir>
##
##Kieskompas opt-in panel (VAA users), Flanders, fielded to 23 January 2023. Respondents were routed
##to an observational study or to this experiment (groep 2 with dv1 present: 2,653; the preprint
##reports 2,650, the number with all three outcomes). Each saw ONE hypothetical flyer (an image, in
##Dutch plus the community's language, with the country-of-origin flag) "die in uw lokale
##bibliotheek zou kunnen hangen" (task = 1, profile = 1). id = row number of the source file (the
##Qualtrics ResponseId is dropped).
##Factors, full 3 x 2 (437-449 per cell). The flyer text itself is not deposited; level text is the
##article's English description (Table 2), mapped from com_ed_treatment1-6 by the authors' do-file
##(1-2 Italian, 3-4 Chinese, 5-6 Moroccan; odd = heritage language, even = math tutoring), and
##agrees with the Dutch manipulation-check options ("De Italiaanse gemeenschap", "Om de taal van
##herkomst te onderwijzen", "Om wiskunde-bijles te geven"):
##  attr_community  Italian community / Chinese community / Moroccan community
##  attr_purpose    Heritage language lessons / Math tutoring
##Outcomes (three ratings of the same flyer; Dutch wording from the SPSS labels, [Field-community]
##piped; 1 = "Heel slecht", 4 = "Noch slecht, noch goed", 7 = "Heel goed", stored raw, higher =
##more favourable):
##  rating_overall  (dv1) "Vindt u het in het algemeen juist goed of juist slecht dat de
##                  [Field-community] gemeenschap zulke lessen organiseert?"
##  rating_children (dv2) "... goed of juist slecht voor [Field-community] kinderen ..."
##  rating_society  (dv3) "... goed of juist slecht voor de Vlaamse samenleving ..."
##  dv2/dv3 are missing for 3 respondents (kept with NA there).
##Covariates (answer text from the value labels): cov_gender (Man/Vrouw/Anders ->
##male/female/other), cov_birth_year, cov_education, cov_province, cov_vote_2019 (2019 Flemish
##Parliament vote; "Zeg ik liever niet" -> NA), cov_left_right (0 = links, 10 = rechts; the code -99
##"Weet niet / zeg ik liever niet" mixes don't-know and refusal and is set NA), cov_attention_pass
##(1 = picked both red and green in screener 2, the authors' "attention" coding; 0 otherwise),
##cov_survey_weight (weight_dv, the post-stratification weight for the experiment; 3 NA),
##cov_duration_sec (whole-survey duration).
##Dropped: ResponseId, dates, observational-study items, the unrelated candidate experiment (repos_*,
##DV1_eval, DV2_trust, DV3_vote), multiculturalism/sexism scales, manipulation checks, derived variables.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "data.sav")))
stopifnot(nrow(s) == 6957L)
s[, id := .I]
s <- s[!is.na(dv1)]
tr <- as.matrix(s[, paste0("com_ed_treatment", 1:6), with = FALSE]); tr[is.na(tr)] <- 0
stopifnot(nrow(s) == 2653L, all(rowSums(tr) == 1))
k <- max.col(tr)
lab <- function(x, na = character()) { v <- trimws(as.character(as_factor(x, levels = "labels"))); v[v %in% na] <- NA; v }
lr <- as.integer(s$left_right); lr[lr < 0] <- NA
d <- data.table(id = s$id, task = 1L, profile = 1L,
  rating_overall = as.integer(s$dv1), rating_children = as.integer(s$dv2), rating_society = as.integer(s$dv3),
  attr_community = c("Italian community", "Chinese community", "Moroccan community")[(k + 1) %/% 2],
  attr_purpose = fifelse(k %% 2 == 1, "Heritage language lessons", "Math tutoring"),
  cov_gender = c(Man = "male", Vrouw = "female", Anders = "other")[lab(s$gender)],
  cov_birth_year = as.integer(s$birthyear), cov_education = lab(s$education), cov_province = lab(s$provincie),
  cov_vote_2019 = lab(s$vote, "Zeg ik liever niet"), cov_left_right = lr,
  cov_attention_pass = as.integer(!is.na(s$screener2_3) & s$screener2_3 == 1 & !is.na(s$screener2_5) & s$screener2_5 == 1),
  cov_survey_weight = as.numeric(s$weight_dv), cov_duration_sec = as.numeric(s$Duration__in_seconds_))
stopifnot(d[, .N, .(attr_community, attr_purpose)][, .N] == 6L, !anyNA(d$cov_gender),
          d[, all(c(rating_overall, rating_children, rating_society) %in% c(1:7, NA))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "steenwegen_2024_community_education.csv"))
