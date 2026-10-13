##Fictional news-article vignette (hunger-relief program) from
##Prather, L. (2020). Transnational ties and support for foreign aid. International Studies
##Quarterly, 64(1), 133-147. https://doi.org/10.1093/isq/sqz096
##Replication data: Harvard Dataverse doi:10.7910/DVN/S0VCUQ, CC0 1.0. File read: Latino_sample_data.tab
##(plain tab-delimited; no value labels). The U.S. and UK files (treat_cash / treat_black) are NOT built:
##the paper documents only a white/black recipient photo there, the deposit gives 0/1 codes, and the
##meaning of the cash treatment is not stated anywhere in the deposit or the article text (held).
##Usage: Rscript prather_2020.R <dir holding Latino_sample_data.tab> <output dir>
##
##1,000 Latino Americans (YouGov online omnibus, English, Aug 2013), one vignette each (no respondent id: id = row
##number, task = 1, profile = 1). Each read "U.S. Officials May Cut Hunger Relief Program" (150,000 people below the
##poverty line, food packages, $100 million a year, held constant) with two independently randomized features
##(Figure 2 of the article, 2x2):
##  attr_program_scope : "the United States" (treat_foreign = 0, domestic program) or "other countries" (= 1)
##  attr_photo_location: caption of the recipients' photo: domestic program Pennsylvania (treat_lat = 0) or New Mexico
##    (= 1); foreign program Africa (0) or Latin America (1). The article note says the Latino treatment is
##    "the program helps Latinos or people in Latin America (1) or African-Americans or people in Africa (0)".
##    The caption levels are therefore nested within the scope (restrictions: yes).
##Outcomes (all after the vignette):
##  choice            = aid: 1 if the respondent said officials should NOT cut the program, 0 if they should cut it
##                      (accept/reject of the single profile, so opt_out yes, coded as in the article's tables)
##  rating_obligation = oblig, "Do you agree or disagree that the US government has a moral obligation to assist the
##                      recipients of this program?" 1-4, higher = stronger agreement (article, Table 3 note)
##  rating_closeness  = close, "How close do you feel, in terms of your ideas and interests, to [the recipients]?"
##                      1-4, higher = closer (article describes it as Not close - Very close; wording paraphrased)
##The authors' transnational-ties measure (ties3, 0 = none, 1 = weak, 2 = strong, observed not randomized) is kept as cov_ties.
##Covariates: cov_gender (woman: 1 = female, 0 = male; article controls "gender (woman)"), cov_age, cov_education_code
##(1-6, no labels in deposit), cov_republican (binary republican affiliation), and the other control codes (white,
##low income, full employment, religiosity importance relimp, trust in government govtrust: codes, no labels).
##Survey weight: none in the file. Count check: N = 1,000 matches the article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "Latino_sample_data.tab"))
stopifnot(nrow(k) == 1000, all(k$treat_foreign %in% 0:1), all(k$treat_lat %in% 0:1))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, choice = as.integer(k$aid),
                rating_obligation = as.integer(k$oblig), rating_closeness = as.integer(k$close),
                attr_program_scope = ifelse(k$treat_foreign == 1, "other countries", "the United States"),
                attr_photo_location = fcase(k$treat_foreign == 0 & k$treat_lat == 0, "Pennsylvania",
                                            k$treat_foreign == 0 & k$treat_lat == 1, "New Mexico",
                                            k$treat_foreign == 1 & k$treat_lat == 0, "Africa",
                                            k$treat_foreign == 1 & k$treat_lat == 1, "Latin America"),
                cov_gender = ifelse(k$woman == 1, "female", "male"), cov_age = as.integer(k$age),
                cov_education_code = as.integer(k$educ), cov_ties = as.integer(k$ties3),
                cov_republican = as.integer(k$rep), cov_white = as.integer(k$white), cov_low_income = as.integer(k$loinc),
                cov_full_employment = as.integer(k$fullemploy), cov_religiosity_code = as.integer(k$relimp),
                cov_govtrust_code = as.integer(k$govtrust))
stopifnot(!anyNA(d[, .(choice, attr_photo_location)]), d[, all(rating_obligation %in% 1:4 | is.na(rating_obligation))],
          d[, all(rating_closeness %in% 1:4 | is.na(rating_closeness))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "prather_2020_foreign_aid_latino.csv"))
