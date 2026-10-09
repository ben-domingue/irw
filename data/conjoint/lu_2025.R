##Property-tax policy conjoints (online survey and lab-in-the-field, urban China) from
##Lü, X., Tsai, L. L., Zheng, P., & Trinh, M. (2025). Do government accountability and
##responsiveness enhance support for property taxes? Experimental evidence from China.
##World Development, 194, 107051. https://doi.org/10.1016/j.worlddev.2025.107051
##Replication data: Harvard Dataverse doi:10.7910/DVN/KLVEGA, CC0 1.0, no restricted files.
##Files read: TaxCompliance_Data_Conjoint.dta (saved as survey.dta) and
##TaxCompliance_Data_Lab_Conjoint.dta (saved as lab.dta), Dataverse "original format".
##Read as text: README.txt, TaxCompliance_Conjoint.do, TaxCompliance_Lab.R.
##Usage: Rscript lu_2025.R <raw dir> <output dir>
##
##LEVEL TEXT: the .dta value labels (English, terse: "Yes"/"No", "15%"/"3%", "1 Million", ...);
##the attribute names follow the authors' .do coefplot headings. The displayed (Chinese) wording
##and the outcome wording are not in the deposit (the article was not accessible here), so
##levels such as "Yes" stand for the presence of the policy feature named by the attribute.
##
##Two tables (different attribute sets, samples and fieldings):
##lu_2025_property_tax_online: online conjoint, 893 respondents (SSI 431 + Qualtrics 462; the
##  authors pool the two panels in their "Combine both datasets" model, so one table with
##  trial_panel = SSI / Qualtrics). 4 tasks x 2 policies (5 respondents have fewer tasks).
##  Attributes: citizen input (citizen_input No/Yes), provincial government supervision
##  (prov_supervise No/Yes), tax payment penalty (penalty_3: 15% / 3%), tax exemption
##  (exemption No/Yes).
##lu_2025_property_tax_lab: conjoint given to the 277 lab-in-the-field subjects, 6 tasks x 2,
##  attributes: citizen input (citizen_suggestion), provincial government supervision, exemption
##  threshold (1/2/3 Million), tax rate (0.10% / 0.20% / 0.50%), tax payment penalty (15% / 3%),
##  spending on public goods (Community Infra / Education / Transportation).
##Outcomes (both tables):
##  choice = selected, the policy chosen in the pair (exactly one per task; no opt-out; the .do
##           labels its effect "Change in Pr(Property Tax Policy Selected)").
##  rating = rank, 1-5 per policy, as stored; wording and anchors not deposited (the .do's axis
##           title for it is "Change in Tax Compliance"; chosen policies average higher, 4.1 vs
##           3.8 online, so higher plausibly = more favourable, not confirmed).
##Randomization restrictions and attribute order not documented.
##Covariates (online): cov_age (years), cov_age_group (value-label text), cov_gender (from the
##0/1 variable `male`: 1 = male, 0 = female; the variable name is the only source), cov_education
##(value-label text), cov_ccp / cov_local_hukou / cov_married (0/1 as named), cov_income_cat
##(codes; labels: 1 = 5,000 and below, 2 = 5,000-10,000, 3 = 10,000-20,000, 4 = 20,000-30,000,
##5 = 30,000-50,000, 6 = 50,000-100,000, 7 = 100,000-200,000, 8 = 200,000-500,000,
##9 = 500,000-1,000,000, 10 = 1,000,000+), cov_apartment_owned (count), cov_location (city text).
##Covariates (lab): the same, without age in years and location; cov_age_group and
##cov_education are value-label text; cov_income_cat codes (labels 1 = 20,000 and below,
##2 = 30,000 ... 13 = 140,000, 14 and 15 both labelled "150,000" in the .dta, 16 = 170,000 ...
##19 = 200,000, 20 = 250,000 ... 23 = 400,000+); cov_apartment_owned 0-4 (4 = 4+).
##Respondent IDs re-keyed to integers (online: respondentIndex; lab: session-subject codes).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) as.character(as_factor(x, levels = "labels"))
s <- read_dta(file.path(raw, "survey.dta"))
d <- data.table(id = match(s$respondentindex, unique(s$respondentindex)), task = as.integer(s$task),
                profile = as.integer(s$profile), choice = as.integer(s$selected), rating = as.integer(s$rank),
                trial_panel = lab(s$source),
                attr_citizen_input = lab(s$citizen_input), attr_provincial_supervision = lab(s$prov_supervise),
                attr_payment_penalty = lab(s$penalty_3), attr_tax_exemption = lab(s$exemption),
                cov_age = as.integer(s$age), cov_age_group = lab(s$age_group),
                cov_gender = c("female", "male")[as.integer(s$male) + 1L], cov_education = lab(s$edu),
                cov_ccp = as.integer(s$ccp), cov_local_hukou = as.integer(s$local_hukou),
                cov_married = as.integer(s$married), cov_income_cat = as.integer(s$income_cat),
                cov_apartment_owned = as.integer(s$apartment_owned), cov_location = as.character(s$location))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:5), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          all(d$trial_panel %in% c("SSI", "Qualtrics")), all(s$male %in% 0:1))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lu_2025_property_tax_online.csv"))

l <- read_dta(file.path(raw, "lab.dta"))
e <- data.table(id = match(l$respondent, unique(l$respondent)), task = as.integer(l$task), profile = as.integer(l$profile),
                choice = as.integer(l$selected), rating = as.integer(l$rank),
                attr_citizen_input = lab(l$citizen_suggestion), attr_provincial_supervision = lab(l$prov_supervise),
                attr_exemption_threshold = lab(l$exemption), attr_tax_rate = lab(l$rate),
                attr_payment_penalty = lab(l$penalty_3), attr_public_goods = lab(l$pub_good),
                cov_age_group = lab(l$age_group), cov_gender = c("female", "male")[as.integer(l$male) + 1L],
                cov_education = lab(l$edu), cov_ccp = as.integer(l$ccp), cov_local_hukou = as.integer(l$local_hukou),
                cov_married = as.integer(l$married), cov_income_cat = as.integer(l$income_cat),
                cov_apartment_owned = as.integer(l$apartment_owned))
stopifnot(e[, sum(choice), .(id, task)][, all(V1 == 1)], all(e$rating %in% 1:5), !anyNA(e[, .SD, .SDcols = patterns("^attr_")]),
          all(l$male %in% 0:1))
setorder(e, id, task, profile)
fwrite(e, file.path(out, "lu_2025_property_tax_lab.csv"))
