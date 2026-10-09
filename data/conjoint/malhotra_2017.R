##Immigrant skill x prevalence factorial vignette (US) from
##Malhotra, N., & Newman, B. (2017). Explaining immigration preferences: Disentangling skill and
##prevalence. Research & Politics, 4(4). https://doi.org/10.1177/2053168017734076
##Replication data: Harvard Dataverse doi:10.7910/DVN/DEKS5Z, CC0 1.0. File read:
##data_jan182017.tab (saved as data.tab). Read as text only: prevalence_code_2017may7.do, README.txt.
##The deposit also re-hosts Hainmueller & Hopkins (2015) conjoint data (repdata.dta) and Wright et
##al. study files for an appendix re-analysis; those are not this experiment and are not built here.
##Usage: Rscript malhotra_2017.R <dir holding data.tab> <output dir>
##
##12,052 US adults (Morning Consult online survey), one vignette each (task 1, profile 1): a
##hypothetical immigrant applying to come to the US. 12 cells (`treat`) = country (Mexico, India,
##Canada) x skill (education and profession move together: "No Formal Education"/"Farm Laborer" vs
##"Equiv. to Completing Graduate Degree in the U.S."/"Doctor") x prevalence information (a sentence
##shown or not). The sentence text is fixed by country x skill and states the real prevalence, e.g.
##"Of the 42.3 million foreign born individuals currently residing in the U.S., there are very many
##low-skill persons from Mexico."; when the cell shows no sentence, attr_prevalence_sentence is
##"(not shown)". Restrictions: education and profession are bundled; the sentence depends on
##country and skill. Cell sizes 949-1,061 (do-file "Experimental Cell Counts"). Level text is as stored
##in the data (country, educationtreat, profession, sentence); the rest of the vignette wording is not
##deposited and the article could not be retrieved (publisher blocks automated access).
##Outcomes (the do-file names them; wording not deposited, paraphrase), stored raw:
##  choice (nm2): binary admission question (Q1), 1 = admit -> choice 1, 2 = not admit -> choice 0
##     (do-file: admit_bin = (nm2-2)/-1). Single-profile accept/reject, so opt_out = yes.
##  rating_admit_scale (nm3): continuous admission measure (Q2), 1-7; do-file admit_scale = (nm3-1)/6,
##     so 7 = most in favour of admitting.
##  rating_how_many_more (nm4): "How many more?" (Q3), 1-5; do-file reverses it ((nm4-5)/-4), so
##     1 = most in favour of more immigrants like this. Stored raw (low = favourable).
##  rating_admit_ten_thousand (nm5): "Admit ten thousand?" (Q4), 1-5; do-file reverses it, so
##     1 = most in favour. Stored raw (low = favourable).
##Covariates: cov_survey_weight (wts). Morning Consult demographics ship only as codes with no labels
##in the deposit: cov_age_code (demAgeFull; the do-file bands codes 2-13, 14-23, ... so it is not
##years), cov_gender_code, cov_education_code (demEduFull), cov_hispanic_code, cov_race_code,
##cov_party_id_code (demPidNoLn), cov_party_lean_code, cov_ideology_code (demPolIdeo), cov_state_code.
##All other survey items are dropped. PII: demZIP (ZIP code) and free-text answers are in the deposit
##and are dropped. id = row number (the file has no respondent id).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.tab"), na.strings = "")
s[sentence == "", sentence := NA]
stopifnot(nrow(s) == 12052, all(s$treat %in% 1:12), all(s$nm2 %in% 1:2), all(s$nm3 %in% 1:7), all(s$nm4 %in% 1:5), all(s$nm5 %in% 1:5))
##cell design check: sentence present exactly in cells 4-6 and 10-12
stopifnot(s[, all(is.na(sentence) == (treat %in% c(1:3, 7:9)))])
d <- s[, .(id = .I, task = 1L, profile = 1L, choice = as.integer(nm2 == 1), rating_admit_scale = as.integer(nm3),
           rating_how_many_more = as.integer(nm4), rating_admit_ten_thousand = as.integer(nm5),
           attr_country = country, attr_education = educationtreat, attr_profession = profession,
           attr_prevalence_sentence = fifelse(is.na(sentence), "(not shown)", trimws(sentence)),
           cov_survey_weight = wts, cov_age_code = demAgeFull, cov_gender_code = demGender, cov_education_code = demEduFull,
           cov_hispanic_code = demHisp, cov_race_code = demRace, cov_party_id_code = demPidNoLn, cov_party_lean_code = demPidLean,
           cov_ideology_code = demPolIdeo, cov_state_code = demState)]
stopifnot(!anyNA(d[, .(attr_country, attr_education, attr_profession)]), uniqueN(d[, .(attr_country, attr_education, attr_prevalence_sentence)]) == 12)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "malhotra_2017_immigrant_skill.csv"))
