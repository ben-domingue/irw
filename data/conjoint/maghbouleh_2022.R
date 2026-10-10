##Racial-classification conjoint (MENA / White) from
##Maghbouleh, N., Schachter, A., & Flores, R. D. (2022). Middle Eastern and North African
##Americans may not be perceived, nor perceive themselves, to be White. Proceedings of the
##National Academy of Sciences, 119(7), e2117940119. https://doi.org/10.1073/pnas.2117940119
##Replication data: Harvard Dataverse doi:10.7910/DVN/BTFTQE, CC0 1.0, no restricted files.
##File read: Maghbouleh_Schachter_Flores_2022_Public.tab (Dataverse original format, Stata 14,
##saved as public.dta). Level text from the Stata value labels, checked against SI Appendix
##Table D2 and the screenshots in the SI ("Text and Questions for the External Classification
##Experiment", pp. 8-11); the deposit's .do file was read as text for the authors' recodes.
##Usage: Rscript maghbouleh_2022.R <raw dir> <output dir>
##
##1,083 US respondents in three samples, pooled in one table with cov_sample because the
##experiment and attribute text are identical and the authors also estimate pooled models
##with sample interactions (SI Figs. S9-S10): MENA (Prolific) 333, MENA (Lucid) 329,
##non-Hispanic White (Prolific) 421, July-September 2021. The paper drops 4 White-sample
##respondents who wrote in a MENA grandparent (417); the deposit does not flag them
##(mena_grandparent is 0 for all 421), so all 421 are kept. cov_mena_grandparent is the authors'
##coding for the two MENA samples (0 for 51 Prolific and 3 Lucid respondents).
##Design: 5 tasks, each a pair of fictitious people shown side by side in a grid ("Immigrant 1" /
##"Immigrant 2", or "U.S.-born Citizen 1" / "U.S.-born Citizen 2"), 10 profiles in all. Each
##profile was classified separately; the pair is not a choice. task = source `pair` (1-5);
##the source numbers profiles 1-10 within respondent with profiles 2t-1 and 2t in pair t;
##profile = 1 for the odd number and 2 for the even one (INFERRED: the deposit does not say which
##column was on the left).
##Attributes (row order randomized once per respondent; source order_* -> attrpos_*):
##  attr_language  "Primary language spoken at home": English / Amharic / Arabic / Persian / German
##                 (SI Table D2 also lists Spanish; it never occurs in the data)
##  attr_occupation "Occupation": Fast Food Cook / Cashier / Home Health Aide / Real Estate Agent /
##                 Food Service Manager / Paralegal / Doctor / Sales Manager / Lawyer
##  attr_ancestry  "Ancestors are from": 33 country pairs, e.g. "England and Germany", "Lebanon and
##                 Syria", "Ethiopia and Iran" (value-label text = displayed text)
##  attr_name      "Name": Claire / Jake / DeShawn / Lakisha / Mohammed / Nawal / Ziad / Randa /
##                 Alireza / Samira
##  attr_religion  "Religion": Christian (Protestant) / Christian (Catholic) / Hindu / Jewish /
##                 Muslim / Buddhist / Atheist/Agnostic. Value labels say "Protestant"/"Catholic";
##                 the displayed text "Christian (...)" is from SI Table D2 and the screenshot.
##  attr_skin_color "Skin Color": a picture of a hand, one of the 10 hand images of the Massey &
##                 Martin (2003) skin-colour scale (SI Table D2 note a). No text was shown; stored
##                 as "Hand image 1" .. "Hand image 10" from source t_skin (1 = lightest; the authors
##                 group 1-3 light, 4-6 medium, 7-10 dark).
##trial_nativity_arm: Immigrant / U.S.-born Citizen (source im_cit, value labels), randomized per
##respondent: the column headers and intro text called the profiles immigrants or citizens.
##Restrictions: none on combinations ("all treatments were fully randomized for each profile",
##paper); NONUNIFORM ancestry weights: "Ancestor treatments were weighted so that the broader
##categories (European, Sub-Saharan African, European-MENA, etc.) had even chances" (SI D2 note b).
##Outcome: "How would you classify these immigrants [these U.S.-born citizens]? (please choose the
##single best category for each individual)", one of White / Black / Native American / Hispanic /
##Middle Eastern/North African (MENA) / Asian (SI p. 11). Stored as six 0/1 ratings, one per
##category, 1 = this category was chosen (rating_white, rating_black, rating_native_american,
##rating_hispanic, rating_mena, rating_asian; source `race` value labels White, Black, Hispanic,
##Asian, Native Am., MENA). Exactly one is 1 on every row. 64 profiles with no answer are dropped.
##PERSONAL DATA in the deposit, dropped: IPAddress, zipcode, prolificID, free-text answers
##(gender, language, religion, grandparents' origins, follow-ups). respid is a sequential number
##(1-1083), re-keyed to integers in sorted order.
##Covariates: cov_sample (value labels of `sample`); cov_age (typed age, whole numbers 18-100
##kept); cov_gender (Female -> female, Male -> male, "Other:" / Transgender -> other, blank NA);
##cov_education, cov_party_id (pid3: Democrat / Republican / Independent / Other),
##cov_party_closer (pid_closer), cov_born_us (bornus), cov_parents_born (parborn), cov_citizen,
##cov_religion (relig), cov_income (hhinc), cov_discrim_mena (perceived discrimination against
##MENA people): answer text as exported, blank -> NA; cov_duration_sec (Qualtrics survey
##duration); cov_attention_score (authors' count of attention checks passed, 1-3);
##cov_mena_grandparent (authors' 0/1 coding of the written-in grandparent origins).
##Dropped: the self-identification experiment (control_resp, treat_resp, nct_*), page timers,
##derived dummies and the authors' collapsed attribute codes.
##Spot check (printed): MENA sample 1 (Prolific), share classified MENA for ancestors "Lebanon and
##Syria" minus "England and Germany" (paper: +51 points for fully Arab vs fully European
##ancestry, from an AMCE model).
suppressMessages({library(data.table); library(haven)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- as.data.table(read_dta(file.path(raw, "public.dta")))
stopifnot(nrow(r) == 10830, uniqueN(r$respid) == 1083)
lab <- function(x) { l <- attr(x, "labels"); v <- names(l)[match(as.numeric(x), l)]; stopifnot(all(is.na(x) | !is.na(v))); v }
txt <- function(x) { x <- trimws(as.character(x)); fifelse(x == "", NA_character_, x) }
rel <- lab(r$t_relig); rel[rel == "Protestant"] <- "Christian (Protestant)"; rel[rel == "Catholic"] <- "Christian (Catholic)"
race <- lab(r$race)
cats <- c(white = "White", black = "Black", native_american = "Native Am.", hispanic = "Hispanic", mena = "MENA", asian = "Asian")
stopifnot(all(is.na(race) | race %in% cats))
age <- suppressWarnings(as.numeric(r$age))
g <- txt(r$gender)
stopifnot(all(is.na(g) | g %in% c("Female", "Male", "Other:", "Transgender")))
ids <- sort(unique(r$respid))
d <- data.table(id = match(r$respid, ids), task = as.integer(r$pair), profile = as.integer(2 - r$profile %% 2), src_profile = r$profile,
  attr_language = lab(r$t_lang), attr_occupation = lab(r$t_occ), attr_ancestry = lab(r$t_gat), attr_name = lab(r$t_name),
  attr_religion = rel, attr_skin_color = paste("Hand image", as.integer(r$t_skin)),
  attrpos_language = as.integer(r$order_lang), attrpos_occupation = as.integer(r$order_occ), attrpos_ancestry = as.integer(r$order_gat),
  attrpos_name = as.integer(r$order_name), attrpos_religion = as.integer(r$order_relig), attrpos_skin_color = as.integer(r$order_skin),
  trial_nativity_arm = lab(r$im_cit), race = race,
  cov_sample = lab(r$sample), cov_age = fifelse(!is.na(age) & age == round(age) & age >= 18 & age <= 100, as.integer(age), NA_integer_),
  cov_gender = c(Female = "female", Male = "male", "Other:" = "other", Transgender = "other")[g],
  cov_education = txt(r$educ), cov_party_id = txt(r$pid3), cov_party_closer = txt(r$pid_closer), cov_born_us = txt(r$bornus),
  cov_parents_born = txt(r$parborn), cov_citizen = txt(r$citizen), cov_religion = txt(r$relig), cov_income = txt(r$hhinc),
  cov_discrim_mena = txt(r$discrim_mena), cov_duration_sec = as.numeric(r$Durationinseconds),
  cov_attention_score = as.integer(r$attention_score), cov_mena_grandparent = as.integer(r$mena_grandparent))
stopifnot(d[, all(task == ceiling(src_profile / 2))], all(d$attr_skin_color %in% paste("Hand image", 1:10)),
          d[, uniqueN(trial_nativity_arm), id][, all(V1 == 1)], d[, uniqueN(attrpos_name), id][, all(V1 == 1)])
for (k in names(cats)) d[, paste0("rating_", k) := as.integer(race == cats[[k]])]
n0 <- nrow(d); d <- d[!is.na(race)]; cat("profiles with no classification dropped:", n0 - nrow(d), "\n")
d[, c("src_profile", "race") := NULL]
d[, cov_mena_grandparent := as.integer(cov_mena_grandparent)]
cat("respondents by sample:\n"); print(d[, .(n = uniqueN(id)), cov_sample])
s <- d[cov_sample == "MENA (Prolific)" & attr_ancestry %in% c("Lebanon and Syria", "England and Germany"), .(mena = mean(rating_mena), .N), attr_ancestry]
print(s)
setcolorder(d, c("id", "task", "profile", paste0("rating_", names(cats))))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "maghbouleh_2022_mena_classification.csv"))
