##Antitrust merger conjoint (US public + antitrust lawyers) and a candidate-choice pilot, from
##Short, N., Hill, S., & Brown, J. R. (2025). What is ideological capture and how do we measure it? Using antitrust reform to
##understand expert-public cleavages. Perspectives on Politics. https://doi.org/10.1017/S153759272510323X
##Replication data: Harvard Dataverse doi:10.7910/DVN/3SOLCT, CC0 1.0 (the files are identical to doi:10.7910/DVN/GW7WKI, which is
##not built separately). File read: datasets.RData (six tibbles, loaded into a new environment; used here: combined_survey_conjoint,
##combined_survey_data, candidate_choice_data); README.txt and replication-file.Rmd read as text (the Rmd header carries an author
##email, not copied). Usage: Rscript short_2025.R <dir holding datasets.RData> <output dir>
##
##TABLE 1, short_2025_merger_challenge. US adults (nonprobability quota sample fielded by Bovitz/Forthright, Jan 2024, n = 2,092)
##plus antitrust lawyers (convenience sample, Nov 2023-Mar 2024, n = 103) = 2,195 respondents, matching the article. Each respondent
##rated FIVE hypothetical mergers (profile_number 1-5, recorded; the article text says four). One profile per task (single-profile
##ratings), seven attributes: employees (firm size: 1,000 / 25,000 / 100,000 workers), layoffs (5% increase, no layoffs, 5/10/20%
##decrease), quality (worse / no quality change / better), prices (5% higher, no price change, 5/10/20% lower), bailout risk
##(less likely / no change / more likely), lobbying (less / no change / more), industry (bank, gas and oil, grocery store chain,
##hospital, pharmaceutical, telecom). The article says attribute order and levels were randomized; the deposit records neither
##the order nor any restriction (none documented). Level text is the stored factor label.
##rating = whether the government should allow or challenge the merger, four points: Definitely allow = 1, Maybe allow = 2,
##Maybe challenge = 3, Definitely challenge = 4 (direction: higher = more support for challenging/blocking). The exact question
##wording is in the article's appendix (Table A.11), not in the deposit: paraphrase. No opt-out. The authors' binary
##answer_binary/answer_binary_num and answer_num (0, 1/3, 2/3, 1; checked to be exactly (rating-1)/3) are derived and dropped.
##Covariates: from combined_survey_data joined on ResponseId (all 2,195 present): cov_gender (Male/Female -> male/female,
##Other -> other), cov_age_group (18-39, 40-59, 60+), cov_education (stored category text), cov_race, cov_party_id (3-way
##party: Democrat/Republican/Independent), cov_party_id7 (party_7 text), cov_ideology (text; NA for 101 lawyers' rows as stored),
##cov_antitrust_lawyer (Yes/No: the antitrust lawyer sample), cov_survey_weight (weights, the authors' poststratification
##weight; same value on all of a respondent's rows). Dropped: ResponseId (Qualtrics id, re-keyed), the attitude and values scales.
##
##TABLE 2, short_2025_candidate_pilot. Pilot 3 (June 2023, convenience sample of survey volunteers): 437 respondents, 3 tasks x
##2 hypothetical candidates, seven attributes (party; positions on boosting fossil fuels, breaking up companies, raising the
##minimum wage, requiring photo ID, expanding Medicare, each Support/Oppose; years in office: never held office / 4 / 8 / 12).
##choice = candidate_choice_data$answer (the Rmd labels the dependent variable "Vote for candidate"; question text not in
##the deposit: paraphrase). In 20 of 1,311 tasks neither candidate has answer = 1; the deposit cannot say whether these are
##refusals or a "neither" option, so those 20 tasks are dropped (not coded as an opt-out); five respondents lose all three tasks, leaving 432. Task = profile_number (recorded),
##profile = candidate_number (recorded). cov_party_id = resp_party (Democrat/Independent/Republican), cov_survey_weight = weights
##(a per-respondent poststratification weight, 0.006-5). Derived agree_*/copartisan/resp_* columns dropped. The article text
##describes this pilot only briefly (online appendix); no figure checked against the paper.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "datasets.RData"), envir = e)
ch <- function(x) as.character(x)
## ---- table 1 ----
m <- as.data.table(e$combined_survey_conjoint); w <- as.data.table(e$combined_survey_data)
stopifnot(uniqueN(m$ResponseId) == 2195, nrow(m) == 2195 * 5, !anyDuplicated(w$ResponseId))
code <- c("Definitely allow" = 1L, "Maybe allow" = 2L, "Maybe challenge" = 3L, "Definitely challenge" = 4L)
rating <- code[ch(m$answer)]
stopifnot(!anyNA(rating), all(abs(m$answer_num - (rating - 1) / 3) < 0.005))
x <- merge(m, w[, .(ResponseId, g = ch(gender), ag = ch(age), ed = ch(education), rc = ch(race), p7 = ch(party_7), ideo = ch(ideology))], by = "ResponseId", all.x = TRUE, sort = FALSE)
stopifnot(nrow(x) == nrow(m))
t1 <- x[, .(id = match(ResponseId, unique(ResponseId)), task = as.integer(ch(profile_number)), profile = 1L, rating = rating[match(paste(ResponseId, profile_number), paste(m$ResponseId, m$profile_number))],
            attr_employees = ch(Employees), attr_layoffs = ch(Layoffs), attr_quality = ch(Quality), attr_prices = ch(Prices),
            attr_bailout = ch(Bailout), attr_lobbying = ch(Lobbying), attr_industry = ch(Industry),
            cov_gender = c(Male = "male", Female = "female", Other = "other")[g], cov_age_group = ag, cov_education = ed, cov_race = rc,
            cov_party_id = ch(party), cov_party_id7 = p7, cov_ideology = ideo, cov_antitrust_lawyer = ch(antitrust_lawyer), cov_survey_weight = weights)]
t1[, cov_gender := unname(cov_gender)]
setorder(t1, id, task, profile)
stopifnot(!anyNA(t1[, grep("^attr_", names(t1), value = TRUE), with = FALSE]), !anyNA(t1$rating), t1[, uniqueN(id)] == 2195,
          t1[, .N, .(id, task)][, all(N == 1)])
fwrite(t1, file.path(out, "short_2025_merger_challenge.csv"))
## ---- table 2 ----
c2 <- as.data.table(e$candidate_choice_data)
c2[, tk := paste(id, ch(profile_number))]
ns <- c2[, sum(answer), tk][V1 == 0, tk]
stopifnot(length(ns) == 20, c2[!tk %in% ns, sum(answer), tk][, all(V1 == 1)], uniqueN(c2$id) == 437)
c2 <- c2[!tk %in% ns]
t2 <- c2[, .(id = match(id, unique(id)), task = as.integer(ch(profile_number)), profile = as.integer(ch(candidate_number)), choice = as.integer(answer),
             attr_party = ch(cand_party), attr_fossil_fuels = ch(cand_boost_fossil_fuels), attr_break_up_companies = ch(cand_break_up_companies),
             attr_experience = ch(cand_experience), attr_min_wage = ch(cand_raise_min_wage), attr_photo_id = ch(cand_require_photo_id),
             attr_medicare = ch(cand_expand_medicare), cov_party_id = ch(resp_party), cov_survey_weight = weights)]
setorder(t2, id, task, profile)
stopifnot(!anyNA(t2[, grep("^attr_", names(t2), value = TRUE), with = FALSE]), t2[, .N, .(id, task)][, all(N == 2)])
fwrite(t2, file.path(out, "short_2025_candidate_pilot.csv"))
