##Expected-contribution conjoint (Denmark) from
##Kruse, M. (2025). The correlates of ethnicity: Why the ethnic majority expects that ethnic
##minorities contribute less to the collective. British Journal of Political Science, 55, e70.
##https://doi.org/10.1017/S0007123425000092 (CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/XKY5PI, CC0 1.0, no restricted files.
##Files read: ethnic_bias_bjps_dataset.tab (Dataverse "original format" .dta, Stata value
##labels) and ethnic_bias_bjps_codebook.pdf. The do-file was read as text (not run).
##Usage: Rscript kruse_2025.R <dir holding data.dta> <output dir>
##
##4,368 ethnic-Danish YouGov panel respondents (17 Feb - 16 Mar 2022; 4,530 recruited, those
##without an ethnic Danish background excluded by the author; the deposit holds the 4,368).
##Framing: a public goods game with 100 hypothetical participants, of whom each respondent
##saw 15, three at a time: task = source `round` (1-5), profile = position within the round
##(source `player` 1-15 minus 3 x (round - 1)). All profiles are men.
##Outcomes, same profiles, one table:
##  choice = which of the three participants the respondent thought would give the most money
##    to the common pool (article's description; forced choice, exactly one of three, checked).
##  rating = expected contribution, 0-10, units of DKK 100 (0 = DKK 0 .. 10 = DKK 1,000; the
##    article: "on a scale from 0 Danish kroner to DKK 1,000, with DKK 100 as the interval").
##  Verbatim wordings are in the article's Appendix A (not read).
##Between-respondent information treatment (trial_information, equal probability): Control
##shows name, born in Denmark, religiosity, age; Socio-economy adds education and residence;
##Cultural values adds gender-role and same-sex-marriage attitudes; Norm compliance adds
##undeclared work and welfare/work status; Full information adds all six; Placebo adds pet,
##nature, colour, exercise, drink and TV preferences. Attributes not shown in a condition are
##"(not shown)". The author pools conditions in some models (Figures 4, 6, 7), so one table.
##attr_name is the first name shown (36 male names, 18 Danish and 18 Middle Eastern, from the
##Stata labels of names_all; that label set stores "Søren" as a Latin-1 byte, re-encoded
##to UTF-8; only strings that are not valid UTF-8 are touched).
##attr_name_origin keeps the author's coding (Danish name / Middle Eastern name), which is
##fully determined by the name: it is a grouping of attr_name, not a separate attribute, kept
##because the author's design and analyses use it. Other level text is the English codebook /
##value-label text (the survey language is not stated; the Danish YouGov panel presumably saw
##Danish text, which is not deposited); attr_age is the
##number of years (30-65).
##Restrictions (article): levels uniform and independent, except that 90% of Danish-named
##profiles were born in Denmark (table: 90%; Middle Eastern-named: 50%). The name always
##appeared at the top; the article says
##profile order was randomized within respondents; attribute order is not recorded.
##Covariates: cov_survey_weight (YouGov weight); respondent items with codebook codes:
##cov_party_vote, cov_res, cov_welfare, cov_undeclared, cov_homo, cov_gender_role, cov_age
##(14 bands), cov_region, cov_edu, cov_personal_income, cov_household_income, cov_occupation,
##cov_pol_interest, cov_rel, cov_gender (1 = Woman, 2 = Man), cov_att_naiv and cov_att_coop
##(validity checks, 1-7), cov_att_ind and cov_att_group (attention checks, 1 = pass),
##cov_device. Dropped: derived variables (age_cat, treat_np, id_* shared-identity flags,
##r_age_cat, pass), constant r_eth, timing variables (endtime, tot_time, duration).
##id = row order of the sorted YouGov caseid, re-keyed 1-4,368.
##Spot check (Figure 2A model, control condition, lm with SEs clustered by id): Middle Eastern
##name -0.092 (SE 0.011) on the forced choice; born outside Denmark -0.070, religious +0.076.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "data.dta"))
lab <- function(x) {
  y <- as.character(as_factor(x, levels = "labels")); y[is.na(x)] <- NA
  bad <- !is.na(y) & !validUTF8(y)
  y[bad] <- iconv(y[bad], "latin1", "UTF-8")
  y
}
z <- function(x) as.integer(zap_labels(x))
ids <- sort(unique(k$caseid))
d <- data.table(id = match(k$caseid, ids), task = z(k$round), profile = z(k$player) - 3L * (z(k$round) - 1L),
                choice = z(k$coop_fc), rating = z(k$coop), trial_information = lab(k$treat),
                attr_name = lab(k$names_all), attr_name_origin = lab(k$name), attr_born = lab(k$born),
                attr_religiosity = lab(k$rel), attr_age = as.character(z(k$age)), attr_education = lab(k$edu),
                attr_residence = lab(k$res), attr_gender_roles = lab(k$gender_role), attr_homosexual_marriage = lab(k$homo),
                attr_undeclared_work = lab(k$undeclared), attr_work_status = lab(k$welfare), attr_pets = lab(k$pets),
                attr_nature = lab(k$nature), attr_color = lab(k$color), attr_exercise = lab(k$exercise),
                attr_drinks = lab(k$drinks), attr_tv = lab(k$tv),
                cov_survey_weight = as.numeric(k$weight))
## the encoding fix must only touch the one non-ASCII name
stopifnot(d[, all(profile %in% 1:3)], d[, .N, .(id, task)][, all(N == 3)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[, all(rating %in% 0:10)], uniqueN(d$id) == 4368, uniqueN(d$attr_name) == 36, "Søren" %in% d$attr_name)
stopifnot(d[, uniqueN(attr_name_origin), attr_name][, all(V1 == 1)])
shown <- list(attr_education = c("Socio-economy", "Full information"), attr_residence = c("Socio-economy", "Full information"),
              attr_gender_roles = c("Cultural values", "Full information"), attr_homosexual_marriage = c("Cultural values", "Full information"),
              attr_undeclared_work = c("Norm compliance", "Full information"), attr_work_status = c("Norm compliance", "Full information"))
for (v in c("attr_pets", "attr_nature", "attr_color", "attr_exercise", "attr_drinks", "attr_tv")) shown[[v]] <- "Placebo"
stopifnot(all(unlist(shown) %in% d$trial_information))
for (v in names(shown)) {
  stopifnot(d[trial_information %in% shown[[v]], !anyNA(get(v))], d[!trial_information %in% shown[[v]], all(is.na(get(v)))])
  d[!trial_information %in% shown[[v]], (v) := "(not shown)"]
}
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
for (v in c("party_vote", "res", "welfare", "undeclared", "homo", "gender_role", "age", "region", "edu", "personal_income",
            "household_income", "occupation", "Pol_interest", "rel", "gender"))
  d[, paste0("cov_", tolower(v)) := z(k[[paste0("r_", v)]])]
for (v in c("att_naiv", "att_coop", "att_ind", "att_group")) d[, paste0("cov_", v) := z(k[[v]])]
d[, cov_device := z(k$device_category)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kruse_2025_expected_contribution.csv"))
