##Incumbent re-election conjoint on pandemic performance (16 countries, CANDOUR II) from
##Duch, R., Loewen, P., Robinson, T., & Zakharov, A. (2025). Governing in the face of a global
##crisis: When do voters punish and reward incumbent governments? Proceedings of the National
##Academy of Sciences, 122(4), e2405021122. https://doi.org/10.1073/pnas.2405021122
##Replication data: Harvard Dataverse doi:10.7910/DVN/HF8YDZ, CC0 1.0, no restricted files.
##File read: conjoint_data.tab (the authors' formatted data, tab-separated; 107 MB). Read as
##text: 0_format_data.R, 0_conjoint_functions.R (convert_conjoint / translate_conjoint /
##create_conjoint_data: how the stored short labels were made from the displayed text),
##0_AZ_recoding_functions.R. Design and wording: SI Appendix (PMC11789171 supplementary PDF),
##survey section 3 and Fig. S1 (screenshot of a UK profile).
##Usage: Rscript duch_2025.R <dir holding conjoint_data.tab> <output dir>
##
##22,180 online respondents in 16 countries (Australia, Brazil, Canada, Chile, China, Colombia,
##France, Ghana, India, Italy, Japan, South Africa, Spain, Uganda, UK, US; March-November 2022;
##Respondi panels, Facebook-recruited samples in Chile, Ghana, Uganda), 8 rounds each. Every
##round shows ONE government leader profile (single-profile design: task = round, profile = 1)
##as a two-column table "Government Policy Outcomes / Government Leader Performance" with six
##attributes, randomized afresh each round. The authors pool the countries (country fixed
##effects) and the attribute set is the same everywhere, so one table with cov_country.
##Attribute text. The stored values are the authors' short labels ("+5%", "Quick to procure",
##"20 weeks", "10 per million", "50%"), made by pattern-matching the displayed text after
##translating non-English versions to English (translate_conjoint). They are mapped back to the
##ENGLISH display text, which Fig. S1 shows for the UK ("-5% decrease GDP", "-5% decline jobs",
##"Government was slow in obtaining necessary COVID-19 Vaccine Supplies", "20 weeks lockdown",
##"10 deaths per million people", "50% vaccinated") and the authors' English targets give for
##the other levels ("5% increase GDP", "0% change", "Government quickly obtained all necessary
##COVID-19 Vaccine Supplies", ...). Respondents in BR, CHL, COL, SP, FR, IT, JPN, CHN and part of
##CAN saw translations; Uganda's English wording differed slightly ("5% increase in GDP").
##The leading apostrophe of the authors' "'-10% decrease GDP" (a spreadsheet artifact) is not kept.
##Outcomes (SI 3.2-3.3):
##  choice: "Please indicate whether you think YES this Government Leader should be re-elected
##    or NO this Government Leader should not be re-elected." choice_bin, 1 = YES. Single
##    profile, so opt_out = yes (NO is the outside option).
##  rating: "On a scale from 1 to 7, where 1 indicates that you Very Strongly Oppose the
##    re-election of this Government Leader and 7 indicates that you Very Strongly Support the
##    re-election of this Government Leader. How would you rate this Government Leader?"
##    choice_cont, 1-7, stored as is.
##Dropped: 221 rows (Brazil) whose jobs level is NA in the source: the Portuguese jobs text
##there was "10% de aumento do PIB" (a GDP wording in the jobs slot), which the authors set to
##missing; those rounds are dropped. 177,219 rows remain, 22,180 respondents.
##Level weights and restrictions are not documented (SI: "randomly assigned"); level shares are
##even. Attribute order looks fixed (Fig. S1; not documented).
##Covariates (as stored in the formatted data; the authors' cross-country recodes):
##cov_country (3-letter code as stored: AUS, BR, CAN, CHL, CHN, COL, FR, GHA, IND, IT, JPN, SP,
##UGA, UK, US, ZAF), cov_region (REGION_0), cov_gender (Female -> female, Male -> male,
##Other -> other, "Prefer not to say" -> NA), cov_age (years), cov_education_level
##(EDUCATION_LEVEL, the authors' harmonized text; "Unknown/missing" -> NA), cov_ideology (0-10
##left-right; SI 10.1), cov_married (marital_status), cov_dep_children, cov_gov_reelect
##(gov_relect, "Would you vote to re-elect this government in the next election?", Yes/No; "NA"
##-> NA), cov_gov_rate (gov_rate, 0-100 rating of the current government), cov_vaccinated
##(subj_vaccinated, the authors' 1 = vac_hist_2 starts "Yes,"), cov_attention_pass (attention:
##1 = chose "None of the above" on att_chk_2, the authors' coding), cov_survey_weight (weights).
##Not kept, to stay well below the 100 MB CSV limit and because they are not respondent
##answers: country-level context (OxCGRT C1-E2, deaths/cases/population, V-Dem, system), the
##authors' PCA scores and indices (food_*, who_*, health_*_pca, covidexp_*), income recodes,
##the raw politics_*/health_pol_* batteries, c_id and the source respondent id (re-keyed).
##N: the article reports 22,147 respondents and 178,184 profiles; the deposit has 22,180 and
##177,440 (the article's counts are not reproduced; flagged, not fixed).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
keep <- c("round", "id", "choice_bin", "choice_cont", "gdp", "jobs", "supplies", "lockdown", "deaths", "vaccinated",
          "country", "REGION_0", "gender", "age", "ideology", "EDUCATION_LEVEL", "attention", "marital_status",
          "dep_children", "subj_vaccinated", "gov_relect", "gov_rate", "weights")
s <- fread(file.path(raw, "conjoint_data.tab"), select = keep, colClasses = list(character = "id"), na.strings = "")
stopifnot(nrow(s) == 177440L, s[, .N, .(id, round)][, all(N == 1)])
pct <- function(x, noun, up, down) fifelse(x == "0%", "0% change",
         fifelse(substr(x, 1, 1) == "+", paste0(substring(x, 2), " ", up, " ", noun), paste0(x, " ", down, " ", noun)))
s <- s[jobs != "NA" & !is.na(jobs)]
d <- s[, .(id = match(id, unique(id)), task = as.integer(round), profile = 1L,
           choice = as.integer(choice_bin), rating = as.integer(choice_cont),
           attr_gdp = pct(gdp, "GDP", "increase", "decrease"),
           attr_jobs = pct(jobs, "jobs", "increase", "decline"),
           attr_vaccine_supplies = c("Quick to procure" = "Government quickly obtained all necessary COVID-19 Vaccine Supplies",
                                     "Slow to procure" = "Government was slow in obtaining necessary COVID-19 Vaccine Supplies")[supplies],
           attr_lockdown = paste(lockdown, "lockdown"),
           attr_deaths = sub(" per million", " deaths per million people", deaths),
           attr_vaccinated = paste(vaccinated, "vaccinated"),
           cov_country = country, cov_region = REGION_0,
           cov_gender = c(Female = "female", Male = "male", Other = "other")[gender],
           cov_age = as.integer(age), cov_education_level = fifelse(EDUCATION_LEVEL == "Unknown/missing", NA_character_, EDUCATION_LEVEL),
           cov_ideology = as.integer(ideology), cov_married = marital_status, cov_dep_children = dep_children,
           cov_gov_reelect = fifelse(gov_relect == "NA", NA_character_, gov_relect), cov_gov_rate = as.integer(gov_rate),
           cov_vaccinated = as.integer(subj_vaccinated), cov_attention_pass = as.integer(attention),
           cov_survey_weight = weights)]
stopifnot(all(s$gdp %in% c("-10%", "-5%", "0%", "+5%", "+10%")), all(s$jobs %in% c("-10%", "-5%", "0%", "+5%", "+10%")),
          !anyNA(d$attr_vaccine_supplies), all(s$lockdown %in% paste(c(10, 20, 30, 40), "weeks")),
          all(s$deaths %in% paste(c(10, 30, 50, 70, 90), "per million")), all(s$vaccinated %in% c("5%", "15%", "25%", "50%", "75%")),
          all(d$choice %in% 0:1), all(d$rating %in% 1:7), all(s$gender %in% c("Female", "Male", "Other", "Prefer not to say")))
stopifnot(d[, uniqueN(cov_country), id][, all(V1 == 1)], nrow(d) == 177219L, uniqueN(d$id) == 22180L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "duch_2025_covid_incumbents.csv"))
