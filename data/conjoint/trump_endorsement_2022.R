##2x3 factorial vignette on a Trump endorsement of a congressional candidate (US, 2022) from the replication data of
##"The Causal Effects of a Trump Endorsement on Voter Perceptions in a General Election Scenario" (authors and article DOI
##not stated in the deposit files read; the code header names the paper and "Danielle" as last editor). Harvard Dataverse
##doi:10.7910/DVN/QJAUTB, CC0 1.0, no restricted files. Files read: poll_2022_weighted_final_topost.tab (downloaded with
##format=original; the code calls it .csv), Final Code.R (as text; arm recodes, DV rescaling, Table 1).
##Usage: Rscript trump_endorsement_2022.R <dir holding poll_2022_weighted_final_topost.tab> <output dir>
##
##1,346 online respondents, 2022 (an omnibus poll with several unrelated modules). This table is the Terry Mitchell experiment only:
##one vignette per respondent (each row is a respondent, id = row number), 2 policy stances x 3 endorsement arms:
##  attr_policy_stance (column `conventional`, text as stored): "Terry supports lowering taxes on wealthy individuals and large
##    corporations, wants to limit the role of the federal government in the health insurance marketplace, and opposes a path to
##    citizenship for undocumented immigrants." / "Terry supports raising taxes ... believes in a path to citizenship ..."
##    (the authors call these 'convenR' and 'unconvenR', i.e. conventional vs unconventional stances for a Republican);
##  attr_trump_endorsement (column `endorsement`): 'Former President Trump has given Terry Mitchell his "complete and total
##    endorsement!"' / 'Former President Trump has said, "I will NOT be endorsing Terry Mitchell for Congress!"' / blank in the
##    control arm = the endorsement sentence omitted by design -> "(not shown)". The stored text has a doubled closing quote in the
##    endorsement string (CSV artefact); normalised to a single closing quotation mark.
##Outcomes (wording NOT in the deposit; no questionnaire; taken from the authors' code): rating = mitchell_vote 1-5, the authors'
##"likelihood to vote" for Mitchell (their rescale 1=0 ... 5=1, so higher = more likely); rating_favorability = mitchell_fave_1, a 0-100
##slider the authors regress as favorability (anchors unknown). Other modules and items (abortion, baker, inflation, urban, partyprime,
##the paired-candidate rural/urban module with Name1..CampaignFocus2, thermometer items, mitchell_ideology/donation/biglie/tariffs) are
##not built: no wording, and the paired module has no documented outcome.
##Covariates (codes with no codebook keep codes): cov_party_id_code (pid3), cov_gender_code (gender), cov_education_code (education),
##cov_age (`age`, years), cov_survey_weight (nationalweight, national weight).
##PII/identifiers dropped: ResponseId, rid (panel id), zip, dates, state, free text. No lat/long or IP columns in this file.
##Count check: 1,346 respondents; the article N was not read.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "poll_2022_weighted_final_topost.tab"), na.strings = c("NA", ""))
stopifnot(nrow(d) == 1346, !anyNA(d$conventional), !anyNA(d$mitchell_vote))
e <- d$endorsement
yes <- grepl("complete and total endorsement", e); no <- grepl("NOT be endorsing", e)
stopifnot(all(yes + no + is.na(e) == 1))
d[, id := .I]
r <- data.table(id = d$id, task = 1L, profile = 1L, rating = as.integer(d$mitchell_vote), rating_favorability = as.numeric(d$mitchell_fave_1),
  attr_policy_stance = d$conventional,
  attr_trump_endorsement = ifelse(yes, "Former President Trump has given Terry Mitchell his “complete and total endorsement!”",
                           ifelse(no, "Former President Trump has said, “I will NOT be endorsing Terry Mitchell for Congress!”", "(not shown)")),
  cov_party_id_code = d$pid3, cov_gender_code = d$gender, cov_education_code = d$education, cov_age = as.integer(d$age),
  cov_survey_weight = as.numeric(d$nationalweight))
print(r[, .N, .(substr(attr_policy_stance, 15, 30), attr_trump_endorsement)])
print(summary(r$rating_favorability)); print(summary(r$cov_age))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "trump_endorsement_2022_mitchell.csv")); cat("rows", nrow(r), "\n")
