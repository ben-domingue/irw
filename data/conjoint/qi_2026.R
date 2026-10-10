##US welfare-program tax-source conjoint from
##Qi, H., & Dorssom, E. I. (2026). Tax burden, tax types, and public support for social welfare
##programs. American Politics Research, 54(5), 638-651. https://doi.org/10.1177/1532673X261451262
##Replication data: Harvard Dataverse doi:10.7910/DVN/9N6PBH, CC0 1.0, no restricted files.
##Files read: conjoint_all.dta; conjointanalysis.do and conjointanalysis.log read as text.
##Usage: Rscript qi_2026.R <raw dir> <output dir>
##
##1,996 US adults (Qualtrics export, fielded 28 June 2022 onward; sample provider not stated in
##the deposit). Each chose between two hypothetical social welfare programs in 8 tasks
##(task, profile recorded; expand = (task-1)*2 + profile, verified).
##Outcome: choice = program_choice (value labels "Chose this program"/"Chose other program");
##forced choice, no opt-out; the question wording is not deposited (paraphrase).
##Attributes (headings from the .do's figure labels; level text from .dta value labels):
##  description ("Policy description"): SSI description / WIC description / HA description (the
##     value labels; the program descriptions respondents read are not deposited);
##  tax_source ("Taxes are collected from"): the displayed text is the variable label of the
##     authors' dummies: Wages, salaries, and investment income (Visible tax 1) / Properties
##     (Visible tax 2) / Retail sales of goods and services (Invisible tax 1) / Income or capital
##     of companies (Invisible tax 2) (the dummies agree with cat_a_tax1, checked);
##  tax_level ("Taxes are levied by"): Federal / State and local / Federal state and local;
##  tax_distribution ("Distribution of tax burden"): Progressive tax / Proportional tax / Regressive tax;
##  cost ("Total cost per year"): 10 billion / 25 billion / 60 billion / 70 billion (US$).
##Restriction: "Properties" occurs only with "State and local" (the authors' constraint
##cat_a_tax1#cat_a_tax2; 0 other combinations in the data).
##Covariates: cov_gender (gender text Female/Male), cov_age (years), cov_education (educ answer
##text), cov_race, cov_family_income (faminc text), cov_employment, cov_ideology (ideo text),
##cov_party_id (party text: Democrat/Republican/Independent/No preference/Other; "In politics
##... do you consider yourself" wording not deposited), cov_party_id7 (pid_7 value-label text,
##built by the authors from party/strength/lean), cov_attention_freq (attention text),
##cov_attention_pass_1..4 (the authors' pass flags: most-important-problem, newspaper,
##WWI/WWII and 'neither' screeners; the paper's main analyses keep screener_count >= 2),
##cov_duration_sec (durationinseconds, whole survey).
##PII: the .dta holds respondents' IP addresses and Qualtrics ResponseIds; both dropped, as are
##dates, raw screener answers, the authors' dummies and grouped variables. No survey weight.
##Spot check: lm(choice ~ attributes) clustered by id reproduces the log's AMCE table (Table C.1)
##for the tax_distribution and cost attributes (e.g. Regressive tax -0.1588).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "conjoint_all.dta"))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
tw <- function(v) { v <- trimws(v); v[v == ""] <- NA; v }
stopifnot(all(k$expand == (k$task - 1) * 2 + k$profile))
t1 <- c("Wages, salaries, and investment income", "Properties", "Retail sales of goods and services", "Income or capital of companies")
stopifnot(all(k$a_tax1_vis_one == (k$cat_a_tax1 == 1)), all(k$a_tax1_vis_two == (k$cat_a_tax1 == 2)),
          all(k$a_tax1_invis_one == (k$cat_a_tax1 == 3)), all(k$a_tax1_invis_two == (k$cat_a_tax1 == 4)))
d <- data.table(id = as.integer(k$id), task = as.integer(k$task), profile = as.integer(k$profile),
                choice = as.integer(zap_labels(k$program_choice)),
                attr_description = lab(k$cat_a_desc), attr_tax_source = t1[as.integer(zap_labels(k$cat_a_tax1))],
                attr_tax_level = lab(k$cat_a_tax2), attr_tax_distribution = lab(k$cat_a_tax3), attr_cost = lab(k$cat_a_cost))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d))
stopifnot(all(k$gender %in% c("Female", "Male")))
age <- as.integer(k$age); age[!is.na(age) & (age < 18 | age > 100)] <- NA
d[, `:=`(cov_gender = tolower(k$gender), cov_age = age, cov_education = tw(k$educ), cov_race = tw(k$race),
         cov_family_income = tw(k$faminc), cov_employment = tw(k$employ), cov_ideology = tw(k$ideo), cov_party_id = tw(k$party),
         cov_party_id7 = lab(k$pid_7), cov_attention_freq = tw(k$attention),
         cov_attention_pass_1 = as.integer(k$mipscreener_pass), cov_attention_pass_2 = as.integer(k$newspaperscreener_pass),
         cov_attention_pass_3 = as.integer(k$wwiscreener_pass), cov_attention_pass_4 = as.integer(k$neitherscreener_pass),
         cov_duration_sec = as.integer(k$durationinseconds))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "qi_2026_welfare_taxes.csv"))
