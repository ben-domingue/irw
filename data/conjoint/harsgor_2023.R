##COVID-19 assistance-policy conjoint (Israel) from
##Harsgor, L., & Yakter, A. (2024). Public preferences for intergroup assistance in conflicts facing
##joint external threats: Lessons from COVID-19 in Israel. Journal of Conflict Resolution, 68(7-8),
##1522-1551. https://doi.org/10.1177/00220027231198519 (online first 2023-08-25)
##Replication data: Harvard Dataverse doi:10.7910/DVN/AMMJOM, CC0 1.0, no restricted files, no terms.
##Files read: "Conjoint experiment july.csv" (Dataverse original of "Conjoint experiment july.tab")
##and "Panel survey July+October.dta" (value labels of the respondent covariates only). Also read as
##text: "Harsgor & Yakter JCR - README.pdf" and "Harsgor & Yakter JCR - conjoint code.r". The
##article and its online appendix (questionnaire) could not be retrieved (publisher 403).
##Usage: Rscript harsgor_2023.R <raw dir> <output dir>
##
##July 2020 wave of the authors' two-wave online panel of Jewish-Israeli adults (README; deposit abstract). 1,589
##respondents in the file, each shown 5 tasks (task) of 2 policy profiles (profile 1-2), 5
##attributes. Outcome: choice = `selected` (the authors' cregg models `selected ~ ...`), one of the
##two profiles chosen in every answered task; no opt-out. Question wording not in the deposit
##(design record: unknown). No rating.
##Attributes, as stored (the authors' English labels; the respondents most likely saw Hebrew:
##the panel .dta carries Hebrew value labels for some items; the displayed wording is not in the
##deposit). Attribute names are the authors' (var_label in their code):
##  action "POLICY TYPE": Lockdown / Worker Ban / Monitor / Protective Equipment / Medical Aid
##  effect_pal "PALESTINIAN ILLNESS": Deterioration / No Effect / Improvement
##  effect_isr "CROSS-INFECTIONS": Fewer Infections / No Change
##  funding "FUNDING SOURCE": Palestinian Taxes / Half-and-Half / Israeli Budget
##  collaboration "COORDINATION": No Coordination / Only With PA / With PA and Hamas
##Restrictions (OBSERVED, not documented in the deposit): Medical Aid never appears with
##Deterioration and Monitor never with Improvement (the authors model action * effect_pal). So
##Medical Aid and Monitor appear less often (2,490 / 2,472 vs ~3,640 profiles) and No Effect more
##often. Attribute row order is fixed (the *.rowpos columns are constant: action 1, effect_pal 2,
##effect_isr 3, funding 4, collaboration 5), so no attrpos_ columns.
##Dropped: 334 tasks (668 rows) with no answer (selected NA; the authors drop them too), leaving 1,586
##respondents; the Qualtrics ResponseId (re-keyed to integers); the *.rowpos columns; respondentIndex
##(an unexplained 1-6 index that tracks health_concern; not documented).
##Covariates. Mapped from the value labels of the panel .dta (same variable names and codes in the
##conjoint file; the README says the conjoint file comes from the July wave of that survey):
##cov_gender (sex 1 Male, 2 Female), cov_education (education: Elementary school or lower / High
##School without matriculation / High school with matriculation / Post-secondary non-academic
##(teachers seminar, nursing certificate, Practical Engineer, religious studies) / Academic BA /
##Academic MA or higher), cov_religiosity (Ultra-Orthodox (Haredi) / Religious / Traditional /
##Secular), cov_income ("Income compared to average": Far below average .. Far above average).
##cov_age in years as stored. Kept as codes (no labels in the deposit): cov_region (-90 = a missing
##code, 20 rows), cov_left_right (1-7; the authors' code labels 1-3 "Left", 4 "Center", 5-7
##"Right"), cov_health_concern and cov_econ_concern (1-5, "Health-related / Economic concern of
##COVID-19"). No survey weight in the deposit.
##N: 1,586 answering respondents; the article's N was not checked.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "conjoint_july.orig"))
p <- read_dta(file.path(raw, "panel.dta"))
x <- x[!is.na(selected)]
stopifnot(x[, .(s = sum(selected), n = .N), .(Response.ID, task)][, all(s == 1 & n == 2)],
          all(x$action.rowpos == 1), all(x$effect_pal.rowpos == 2), all(x$effect_isr.rowpos == 3),
          all(x$funding.rowpos == 4), all(x$collaboration.rowpos == 5))
ids <- unique(x$Response.ID)
d <- data.table(id = match(x$Response.ID, ids), task = as.integer(x$task), profile = as.integer(x$profile),
                choice = as.integer(x$selected),
                attr_action = x$action, attr_effect_pal = x$effect_pal, attr_effect_isr = x$effect_isr,
                attr_funding = x$funding, attr_collaboration = x$collaboration)
stopifnot(!anyNA(d), d[, all(sort(profile) == 1:2), .(id, task)]$V1)
lab <- function(v, codes) { l <- attr(p[[v]], "labels"); stopifnot(all(codes %in% c(l, NA))); unname(names(l)[match(codes, l)]) }
stopifnot(identical(unname(attr(p$sex, "labels")), c(1, 2)), names(attr(p$sex, "labels")) == c("Male", "Female"))
d[, cov_gender := c("male", "female")[x$sex]]
d[, cov_age := as.integer(x$age)]
d[, cov_education := lab("education", x$education)]
d[, cov_religiosity := lab("religiosity", x$religiosity)]
d[, cov_income := lab("income", x$income)]
d[, `:=`(cov_region = as.integer(x$region), cov_left_right = as.integer(x$left_right),
         cov_health_concern = as.integer(x$health_concern), cov_econ_concern = as.integer(x$econ_concern))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "harsgor_2023_covid_aid_palestinians.csv"))
cat(nrow(d), uniqueN(d$id), "\n")
