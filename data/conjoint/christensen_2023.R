##Political-leader conjoint on media freedom vs policy positions (Finland) from
##Christensen, H. S., & Saikkonen, I. (2023). Replication data: Does democratic backsliding
##depend on the policy issue [Data set]. OSF. https://doi.org/10.17605/OSF.IO/JN5KZ
##(no article is linked from the deposit; the do-file calls the paper "Transgressions across
##issues". The same authors' "Guardians of democracy" conjoint, Political Research Quarterly
##2023, doi:10.1177/10659129211073592, is a different experiment: 1,030 respondents, other
##attributes.)
##Licence: OSF node licence CC BY 4.0, no other terms in the files.
##Files read: Replication data.dta (OSF y3h4b), saved as data.dta. Labels from the .dta value
##labels and the authors' "Replication file Does backsliding depend.do" (read as text, section
##2.1 "Labelling conjoint attributes"); codebook ...Policy Issue.html (frequencies only).
##Usage: Rscript christensen_2023.R <dir holding data.dta> <output dir>
##
##2,406 Finnish respondents, 6 tasks ("comp") of 2 leader profiles ("profile", left/right
##placement in the do-file section 4.2), 7 attributes, each with two levels. Level text is the
##authors' ENGLISH labels (the Finnish text shown to respondents is not in the deposit):
##gender (Male/Female), age (28 years old/74 years old, .dta labels), education (Basic
##education/University degree), media freedom (Condemns restricting media freedom/Wants to
##restrict media freedom), welfare state spending (Favours increased spending/Favours lower
##taxes), adoption rights (Favours adoption rights/Opposed to adoption rights), climate
##efforts (Favours stronger measures/Opposed to stronger efforts); do-file label text, which
##spells out the media levels that the .dta labels truncate.
##Outcomes:
##  choice: `choice` (= conjointchoice == profile), which of the two leaders the respondent
##    chose; exactly one per task. The question wording is not in the deposit.
##  choice_vote: the follow-up `votes` ("Would vote for selected profile", No/Yes), asked once
##    per task about the chosen profile: 1 on the chosen profile when the answer is Yes, else 0
##    (opt-out: a respondent can decline to vote for either).
##trial_design_version = vers_cbconjoint (the design version, 180 versions, one per
##respondent): the profiles come from a fixed set of design versions (likely a Sawtooth CBC
##design; not documented). Attribute order and randomization restrictions are not documented.
##Covariates (Finnish answer text as stored): cov_age_group (age band), cov_age (v5, the typed
##age: whole numbers only; "21-vuotias", "40v", "E" and a superscript "65" are set NA),
##cov_gender (Nainen -> female, Mies -> male, "Muu/en halua sanoa" (other/prefer not to say)
##-> NA, since it mixes other and refusal), cov_region (4 areas), cov_province (v7),
##cov_education, cov_has_party (partyid: Kyllä/En), cov_party_id (partyid_party, NA when blank),
##cov_polint, cov_ideology, cov_demsat, cov_eff_1-5, cov_demideal_*, cov_poltrst_*,
##cov_authpar1-3, cov_auth1-12, cov_polpos_* (as stored). Dropped: municipality (229 values,
##58 of them with a single respondent; re-identification risk), the authors' recodes (pos_*,
##*_congr*, *_3cat, educ codes) and the row id. No survey weight (none in the deposit).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "data.dta"))))
stopifnot(nrow(s) == 28872L, uniqueN(s$respid) == 2406L, s[, .N, respid][, all(N == 12)])
lab <- list(att_gendr = c("Male", "Female"), att_age = c("28 years old", "74 years old"),
            att_educ = c("Basic education", "University degree"),
            att_media = c("Condemns restricting media freedom", "Wants to restrict media freedom"),
            att_welf = c("Favours increased spending", "Favours lower taxes"),
            att_mino = c("Favours adoption rights", "Opposed to adoption rights"),
            att_clima = c("Favours stronger measures", "Opposed to stronger efforts"))
nm <- c(att_gendr = "gender", att_age = "age", att_educ = "education", att_media = "media_freedom",
        att_welf = "welfare", att_mino = "adoption_rights", att_clima = "climate")
for (v in names(lab)) stopifnot(all(s[[v]] %in% 1:2))
d <- s[, .(id = as.integer(respid), task = as.integer(comp), profile = as.integer(profile), choice = as.integer(choice))]
stopifnot(all(d$choice == as.integer(s$conjointchoice == s$profile)))
d[, choice_vote := as.integer(choice == 1L & s$votes == 1)]
for (v in names(lab)) d[, paste0("attr_", nm[[v]]) := lab[[v]][s[[v]]]]
d[, trial_design_version := as.integer(s$vers_cbconjoint)]
age <- trimws(s$v5)
d[, `:=`(cov_age_group = s$age, cov_age = fifelse(grepl("^[0-9]+$", age), suppressWarnings(as.integer(age)), NA_integer_),
         cov_gender = c(Nainen = "female", Mies = "male")[s$gender], cov_region = s$region, cov_province = s$v7,
         cov_education = s$education, cov_has_party = s$partyid,
         cov_party_id = fifelse(trimws(s$partyid_party) == "", NA_character_, s$partyid_party))]
keep <- c("polint", "ideology", "demsat", paste0("eff_", 1:5), grep("^demideal_|^poltrst_|^polpos_", names(s), value = TRUE),
          paste0("authpar", 1:3), paste0("auth", 1:12))
for (v in keep) d[, paste0("cov_", v) := s[[v]]]
stopifnot(d[, .(sum(choice), sum(choice_vote), .N), .(id, task)][, all(V1 == 1 & V2 <= 1 & N == 2)])
stopifnot(s[, uniqueN(votes), .(respid, comp)][, all(V1 == 1)], all(d$cov_age %between% c(18, 99) | is.na(d$cov_age)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "christensen_2023_backsliding_issues.csv"))
