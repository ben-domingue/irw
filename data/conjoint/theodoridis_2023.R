##Discrimination conjoint (US, YouGov) from
##Theodoridis, A. G., Goggin, S. N., & Deichert, M. (2023). Separated by politics?
##Disentangling the dimensions of discrimination. Political Behavior, 45(4), 2025-2051.
##https://doi.org/10.1007/s11109-022-09809-y (online July 2022). Author order from the
##publisher's Crossref record; the authors' replication.R header lists "Deichert, Goggin,
##Theodoridis".
##Replication data: Harvard Dataverse doi:10.7910/DVN/IFDM4B, CC0 1.0, no restricted files,
##no terms. Files read: replication.tab (Dataverse "original format" download, CSV, one row
##per respondent, wide conj_<task><A|B>_<attr> codes). Read as text: replication.R (the
##authors' stacking code and factor() labels, the only source of level text) and
##Online_Appendix.pdf (Table I sample, Figures I-VIII level lists). The article (paywalled)
##was NOT read: question wording is not documented here.
##Usage: Rscript theodoridis_2023.R <raw dir> <output dir>
##
##2,654 YouGov respondents (appendix Table I: N = 2654) each made 5 choices (conj_1..conj_5,
##1 = "Person A", 2 = "Person B", per replication.R) between two target people, A = profile 1,
##B = profile 2. Each respondent was assigned one of five contexts (conj_treat, between
##subjects; labels from replication.R: 1 Relative, 2 Neighbor, 3 Loan, 4 Charity, 5 Jury),
##stored as trial_context; the context-specific question wording is not deposited
##(design_outcomes carries a paraphrase). choice: forced, exactly one per task (checked).
##10 attributes, levels from the authors' factor() labels in replication.R:
##  race Black/White/Hispanic/Latino/Asian; sex Male/Female; age (the number shown, 25-75; the
##  authors bin it); party Democrat/Republican/Independent; ideology Fiscally Conservative/
##  Socially Conservative/Fiscally Liberal/Socially Liberal; grew up Big City/Small Town/Suburbs/
##  Medium Size City; religion Atheist/Jewish/Muslim/Catholic/Mainline Protestant/Evangelical
##  Protestant/Spiritual; career 15 occupations ("Factor Foreman" as spelled by the authors,
##  presumably factory foreman); marital status Married/Single/Divorced/Widowed; sexual
##  orientation "Homosexual, Gay, or LGBT"/"Heterosexual or Straight".
##Every attribute also has a "<Attribute> - Not Asked" level (code 5/3/4/.../16; age 76),
##drawn independently for each profile (about 15% of profiles per attribute; both profiles of
##a pair about 2%): coded here as "(not shown)". ASSUMPTION for Ben: the deposit does not say
##whether those profiles showed a blank or a placeholder; the authors treat "Not Asked" as the
##baseline (appendix Fig. note "'Not Asked' is the omitted category").
##Sexual orientation: Heterosexual about 2x as frequent as Homosexual (level_weights observed).
##Covariates: cov_survey_weight (weight; NA for 154 respondents), cov_birth_year (birthyr).
##No codebook maps the YouGov codes, so these keep their codes with a _code suffix:
##cov_gender_code, cov_race_code, cov_educ_code, cov_pid7_code (replication.R: 1-3 Democrat
##side, 4 independent, 5-7 Republican side, 8 not coded), cov_ideo5_code, cov_newsint_code
##(appendix Fig. II note: 1 = "most of the time"), cov_marstat_code, cov_religpew_code,
##cov_employ_code, cov_votereg_code, cov_inputstate_code, cov_sexual_orientation_code.
##Dropped: caserow, YouGov caseid (re-keyed to integers in file order), occupation, child18,
##faminc_new, pew_* items, pid3/pid3_t/pid7zero/pid3lean, most_import_factor (a post-task
##"most important factor" item, codes 1-12 with no labels), starttime/endtime.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "replication.csv"))
stopifnot(nrow(k) == 2654L, !anyDuplicated(k$caseid))
k[, id := seq_len(.N)]
labs <- list(race = c("Black", "White", "Hispanic/Latino", "Asian", NA),
             sex = c("Male", "Female", NA), party = c("Democrat", "Republican", "Independent", NA),
             ideo = c("Fiscally Conservative", "Socially Conservative", "Fiscally Liberal", "Socially Liberal", NA),
             grew = c("Big City", "Small Town", "Suburbs", "Medium Size City", NA),
             relig = c("Atheist", "Jewish", "Muslim", "Catholic", "Mainline Protestant", "Evangelical Protestant", "Spiritual", NA),
             career = c("Carpenter", "Professor", "Teacher", "Lawyer", "Doctor", "CEO", "Retail Manager", "Receptionist",
                        "Small-Business Owner", "Farmer", "Factor Foreman", "Construction Worker", "Engineer", "Lobbyist",
                        "Political Staffer", NA),
             marstat = c("Married", "Single", "Divorced", "Widowed", NA),
             sexorient = c("Homosexual, Gay, or LGBT", "Heterosexual or Straight", NA, NA))
nm <- c(race = "race", sex = "sex", party = "party", ideo = "ideology", grew = "grew_up", relig = "religion",
        career = "career", marstat = "marital_status", sexorient = "sexual_orientation")
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  s <- data.table(id = k$id, task = t, profile = p, choice = as.integer(k[[paste0("conj_", t)]] == p))
  ag <- k[[sprintf("conj_%d%s_age", t, c("A", "B")[p])]]
  stopifnot(all(ag %in% c(25:75, 76)))
  s[, attr_age := fifelse(ag == 76L, "(not shown)", as.character(ag))]
  for (x in names(labs)) {
    v <- k[[sprintf("conj_%d%s_%s", t, c("A", "B")[p], x)]]
    stopifnot(all(v %in% seq_along(labs[[x]])), all(v == length(labs[[x]]) | !is.na(labs[[x]][v])))
    s[, paste0("attr_", nm[x]) := fifelse(v == length(labs[[x]]), "(not shown)", labs[[x]][v])]
  }
  s
}))))
d[, trial_context := c("Relative", "Neighbor", "Loan", "Charity", "Jury")[k$conj_treat[id]]]
cv <- data.table(id = k$id, cov_survey_weight = k$weight, cov_birth_year = k$birthyr,
                 cov_gender_code = k$gender, cov_race_code = k$race, cov_educ_code = k$educ, cov_pid7_code = k$pid7,
                 cov_ideo5_code = k$ideo5, cov_newsint_code = k$newsint, cov_marstat_code = k$marstat,
                 cov_religpew_code = k$religpew, cov_employ_code = k$employ, cov_votereg_code = k$votereg,
                 cov_inputstate_code = k$inputstate, cov_sexual_orientation_code = k$sexual_orientation)
d <- merge(d, cv, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), !anyNA(d$trial_context))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "theodoridis_2023_discrimination.csv"))
