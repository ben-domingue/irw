##Immigrant-admission rating conjoint (US) from
##Zhirkov, K. (2022). Estimating and using individual marginal component effects from
##conjoint experiments. Political Analysis, 30(2), 236-249. https://doi.org/10.1017/pan.2021.4
##Replication data: Harvard Dataverse doi:10.7910/DVN/K2JI6I, CC0 1.0, no restricted files.
##Files read (from replication_materials.zip): data/data_02_conjoint_unprocessed.dta (the
##Qualtrics/Conjoint Survey Design Tool export) and data/data_01_survey.dta (respondent
##covariates). The authors' code/code_02_conjoint_processing.do was read as text (not run)
##for the layout; design facts and the outcome wording are from the (CC BY) article.
##Usage: Rscript zhirkov_2022.R <dir holding data_02_... and data_01_...> <output dir>
##
##929 Lucid respondents (December 2019). The article: 1,003 completed; 74 who gave the same
##score to every profile were excluded, leaving 929; the deposit holds only these 929. Each
##rated 15 pairs (task 1-15) of hypothetical immigrants, profile 1 = left, 2 = right
##(source F_<task>_<profile>_<k>), on 6 attributes: age (a number of years, 26-55), gender,
##race/ethnicity, education, English proficiency, prior trips to the U.S.
##Outcome: rating = "preference for being admitted to the United States", 11-point scale,
##0 = Definitely not admit .. 10 = Definitely admit (higher = more favourable). Each profile
##was rated separately; there is no choice question. 7 missing ratings are omitted (rows
##with no outcome), so 27,863 rows rather than 27,870.
##Attribute levels are the text shown (age as the number). Values were fully and independently
##randomized with uniform probabilities (article). Attribute ROW ORDER was randomized per
##respondent and fixed across that respondent's 15 tasks (source F_<task>_<k> headers, checked
##identical across tasks); kept as attrpos_<name> = 1..6, top to bottom.
##The authors' processing script additionally drops respondents who never saw both values of a
##dichotomized attribute (for their individual-level estimates); that is an analysis choice and
##is NOT applied here, so all 929 respondents are kept. Their dichotomized/collapsed attribute
##codes (*_bin, *_cat) are not reproduced.
##Covariates (data_01_survey.dta, Lucid-supplied): cov_age (years); cov_gender (value labels
##1 = Male, 2 = Female -> male/female); cov_education = the value-label text of education
##("Education category"): Less than high school, Complete high school, Post high school
##vocational training, Some college, no degree, Associate's degree, Bachelor's degree,
##Master's or professional degree, Dcotorate degree [sic, verbatim]; cov_party_id7 = the
##value-label text of pid ("Party identification"): Strong Democrat, Not very strong
##Democrat, Independent, lean Democrat, Independent, Independent, lean Republican, Not very
##strong Republican, Strong Republican. Source codes kept: cov_income (household income,
##1 = less than $14,999 .. 24 = $250,000 and above, $5,000 bands to $100,000, then
##$25,000/$50,000 bands), cov_race (1 = White, 2 = Black or African American, 3 = American
##Indian or Alaska Native, 4 = Asian, 5 = Pacific Islander, 6 = Other), cov_hispanic (0 = No,
##1 = Yes). Dropped: the authors' derived ethnocentrism scale score (the item responses are
##not deposited). No survey weight, attention check or duration in the deposit (readme).
##Profiles were shown as the usual two-column conjoint table (article Figure 1). No task is
##repeated (checked). The 7 omitted missing ratings leave 7 tasks with one profile.
##Count check: 929 respondents matches the article. Spot check: OLS of rating on the
##dichotomized attributes (as in the authors' Figure 2), clustered by id, gives no prior
##violation +1.473 (SE .071), college +0.665, good English +0.626, female +0.085; the deposited
##data_04_Figure2_output.txt has +1.474, +0.665, +0.626, +0.087 (the authors' sample is a little
##smaller because of the drop described above).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "data_02_conjoint_unprocessed.dta")))
## attribute order is fixed within respondent
for (i in 2:15) for (j in 1:6) stopifnot(all(k[[sprintf("F_%d_%d", i, j)]] == k[[sprintf("F_1_%d", j)]]))
nm <- c("Age" = "age", "Gender" = "gender", "Race/ethnicity" = "race_ethnicity", "Education" = "education",
        "English proficiency" = "english", "Prior trips to U.S." = "prior_trips")
d <- rbindlist(lapply(1:15, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = as.integer(k$respid), task = t, profile = p,
                  rating = as.integer(k[[sprintf("rate_%d_%d", p, t)]]))
  for (j in 1:6) {
    an <- nm[k[[sprintf("F_1_%d", j)]]]; stopifnot(!anyNA(an))
    for (v in unique(an)) {
      w <- an == v
      x[w, paste0("attr_", v) := k[[sprintf("F_%d_%d_%d", t, p, j)]][w]]
      x[w, paste0("attrpos_", v) := j]
    }
  }
  x
}))))
setcolorder(d, c("id", "task", "profile", "rating", paste0("attr_", nm), paste0("attrpos_", nm)))
stopifnot(d[, all(rating %in% c(0:10, NA))], !anyNA(d[, paste0("attr_", nm), with = FALSE]))
d <- d[!is.na(rating)]
s <- as.data.table(read_dta(file.path(raw, "data_01_survey.dta")))
vl <- function(v) { l <- attr(v, "labels"); x <- names(l)[match(as.numeric(v), l)]; stopifnot(all(is.na(v) | !is.na(x))); x }
stopifnot(all(s$gender %in% 1:2), identical(vl(haven::labelled(1:2, attr(s$gender, "labels"))), c("Male", "Female")))
cv <- s[, .(id = as.integer(respid), cov_age = as.integer(age), cov_gender = tolower(vl(gender)),
            cov_income = as.integer(zap_labels(income)), cov_race = as.integer(zap_labels(race)),
            cov_hispanic = as.integer(zap_labels(hispanic)), cov_education = vl(education),
            cov_party_id7 = vl(pid))]
stopifnot(uniqueN(cv$id) == nrow(cv), setequal(cv$id, d$id))
d <- merge(d, cv, by = "id")
stopifnot(uniqueN(d$id) == 929)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhirkov_2022_immigrant_admission.csv"))
