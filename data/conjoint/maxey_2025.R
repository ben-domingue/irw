##Military-intervention success conjoint (US) from
##Maxey, S. (2025). Good enough? Public perceptions of success in military interventions.
##International Studies Quarterly, 69(3), sqaf051. https://doi.org/10.1093/isq/sqaf051
##Replication data: Harvard Dataverse doi:10.7910/DVN/RB08VT, CC0 1.0, no restricted files.
##File read: replication/surveyone.dta inside replication.zip (Stata value labels give the level
##text). replicationcode.do and output.smcl were read as text. Question wording is from the
##article's supplementary file (Appendix A2, survey one instrument).
##Usage: Rscript maxey_2025.R <dir holding replication/surveyone.dta> <output dir>
##
##Survey one: 1,214 US online respondents (Qualtrics; platform not stated in the deposit), each
##saw five pairs of hypothetical US military interventions ("Intervention A/B") described by 7
##attributes. The file has NO task or profile column: each respondent has 10 rows, rows 1-5 have
##first_option = 1 and rows 6-10 first_option = 0; row k and row k+5 form a pair (verified: exactly
##one chosen in every answered pair, while pairing consecutive rows fails). So profile 1 = the
##first_option row (taken to be Intervention A) and task = k are INFERRED from row order.
##Surveys two and three in the deposit are single-scenario vignette experiments (not conjoint)
##and are not built.
##Outcomes (supplement A2):
##  choice: "Which intervention was the MOST successful?" Intervention A / Intervention B, forced,
##     no opt-out. 43 pairs unanswered (blank).
##  rating: "How successful were each of the interventions?" 1 = Very Unsuccessful,
##     2 = Somewhat Unsuccessful, 3 = Somewhat Successful, 4 = Very Successful.
##Attributes: level text = the deposit's value labels, which may abbreviate the displayed wording
##(the article, not read, "exhaustively outlines" it): security outcome (cannot attack / can
##attack), humanitarian outcome (people safe / people not safe), soldiers killed (0/10/100/1,000/
##10,000), civilians killed (none / a small number / many), financial costs ($100/$300/$500
##mil/day), peace lasts (<1 year / ~3 years / foreseeable future), target regime (strong
##democracy / weak democracy / dictatorship). Randomization restrictions and attribute order are
##not documented in the deposit.
##Covariates (codes in the instrument's option order, A2; gender, party and attention coding
##confirmed by the authors' .do file, education by their `college` dummy): cov_gender 1=Female
##2=Male 3=Other 4=Prefer not to say; cov_education 1=Did not finish high school .. 6=Graduate
##or professional degree; cov_partyid 1=Strong Democrat .. 7=Strong Republican; cov_race
##(multiple answers, comma-joined: 1=Caucasian (white) 2=African-American 3=American Indian or
##Native American 4=Asian-American 5=Other); cov_hispanic 1=Yes 2=No; cov_age_group 1=18-19
##2=20-29 .. 6=60-69 7=Older than 69; cov_attention_pass (attention1 == 3, "I have a question").
##Dropped: Qualtrics ResponseId (re-keyed to integers in file order), IP_country, recaptcha score,
##consent, news/vote/armedforces/combat/income (codings not documented), the authors' derived
##variables (successbi, college, reversed duplicates SecurityOutcome .. TargetRegime).
##N: 1,214 respondents in the file, one with no answers; 1,213 kept = the authors' AMCE run
##(12,054 profiles; the article itself was not read). Spot check: the authors' rating regression
##(output.smcl, 12,118 obs) gives can attack -0.1375, weak democracy -0.1839; this table gives
##the same N and coefficients.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "replication", "surveyone.dta")))
lab <- function(x) { stopifnot(!is.null(attr(x, "labels"))); as.character(as_factor(x, levels = "labels")) }
s[, r := seq_len(.N), responseid]
stopifnot(s[, .N, responseid][, all(N == 10)], s[, all(first_option == as.integer(r <= 5))])
s[, `:=`(id = match(responseid, unique(responseid)), task = (r - 1L) %% 5L + 1L, profile = 2L - first_option)]
d <- s[, .(id = as.integer(id), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(profilechosen), rating = as.integer(zap_labels(interventionx_success)),
           attr_security_outcome = lab(interventionx_security), attr_humanitarian_outcome = lab(interventionx_humanitarian),
           attr_soldiers_killed = lab(interventionx_milcasualty), attr_civilians_killed = lab(interventionx_civcasualty),
           attr_financial_costs = lab(interventionx_costs), attr_peace_lasts = lab(interventionx_peace),
           attr_target_regime = lab(interventionx_regime),
           cov_gender = as.integer(gender), cov_education = as.integer(education), cov_partyid = as.integer(partyid),
           cov_race = as.character(race), cov_hispanic = as.integer(hispanic), cov_age_group = as.integer(age),
           cov_attention_pass = as.integer(attention1 == 3))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d$rating %in% c(1:4, NA)),
          d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)])
d <- d[!(is.na(choice) & is.na(rating))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "maxey_2025_intervention_success.csv"))
