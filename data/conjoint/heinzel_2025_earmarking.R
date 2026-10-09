##Earmarked-contribution paired conjoint (UN staff elite survey) from
##Heinzel, M., Reinsberg, B., & Siauwijaya, C. (2025). Understanding resourcing trade-offs in
##international organizations: Evidence from an elite survey experiment. The Journal of Politics,
##88(3), 1231-1244. https://doi.org/10.1086/736339
##Replication data: Harvard Dataverse doi:10.7910/DVN/0NQPXZ, CC0 1.0, no restricted files, no terms.
##File read: Heinzel_Reinsberg_Siauwijaya_24_ACCEPT.dta (original-format download); the .do files
##read as text, not run. Design and wording: accepted manuscript (eprints.gla.ac.uk/354525),
##research-design section and Table 1.
##Usage: Rscript heinzel_2025_earmarking.R <raw dir> <output dir>
##
##280 staff of six UN organizations (email + LinkedIn recruitment; paper: "our final sample
##included 280 UN staff members"), 7 tasks of two "hypothetical contributions" ("Contribution 1",
##"Contribution 2"); six features, two levels each, "independently randomized" (paper). The deposit
##keeps only respondents who rated all seven pairs (paper). Long file already one row per
##respondent x task x profile: id = group(responseid) (authors' integer key), task = choice_number,
##profile = profile_number. Level text = the deposit's choice<feature> string columns: Yes/No for
##earmarked to your area of work / country / sector / project; length "1 year"/"3 years" (Table 1:
##"Spend within one year/three years"); donor "Member state"/"Private foundation".
##Outcomes:
##  choice          = choicevar_clean (choicevar "Contribution 1"/"Contribution 2"), a forced choice
##                    the paper uses as a robustness check (wording not reported); exactly one per task.
##  rating_amount   = amount_clean: answer to "The typical contribution to a UN organization is
##                    approximately 1.84 million USD. For each of the two contributions, please indicate
##                    in million USD how large the minimum grant amount would need be to be worth it for
##                    the international organization (please write "No" if you do not think that the
##                    international organization should accept the contribution)". Open text (<= 4
##                    characters); the stored value is the AUTHORS' numeric cleaning (million USD) in the
##                    deposit; the raw text (c<k>_amount<p>) is not kept.
##  rating_overhead = overhead_clean: "... please indicate how much overheads an international
##                    organization should charge in percent (please write "No" ...)", authors' cleaning
##                    of the open text (percent).
##  rating_refuse   = refuse (1 = the respondent rejected the contribution by writing "No"; authors'
##                    coding; NA for 143 profiles).
##Covariates (source text): cov_organization (q26), cov_gender (q8 Male/Female; "Prefer not to say" ->
##NA), cov_region (q10 duty-station region), cov_staff_focus (q11), cov_staff_category (q35),
##cov_grade (q25); "Prefer not to say" kept as NA in these. cov_recruitment = data (email / linkedin).
##cov_survey_weight = mean_weight, the authors' post-stratification weight to UN staff composition
##(gender, duty station, grade; used in appendix Fig. A2). Dropped: q29_1-q32_1 (unlabelled),
##IO-level shares, derived dummies/logs, estimation-sample flags, raw open-text answers.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(zap_labels(read_dta(file.path(raw, "Heinzel_Reinsberg_Siauwijaya_24_ACCEPT.dta"))))
na_pref <- function(v) { v <- trimws(as.character(v)); v[v %in% c("", "Prefer not to say")] <- NA; v }
d <- x[, .(id = as.integer(id), task = as.integer(choice_number), profile = as.integer(profile_number),
           choice = as.integer(choicevar_clean),
           rating_amount = as.numeric(amount_clean), rating_overhead = as.numeric(overhead_clean),
           rating_refuse = as.integer(refuse),
           attr_own_area = choiceown_area, attr_country = choicecountry, attr_sector = choicesector,
           attr_project = choiceproject, attr_length = choicelength, attr_donor = choicesource,
           cov_organization = na_pref(q26), cov_gender = tolower(na_pref(q8)), cov_region = na_pref(q10),
           cov_staff_focus = na_pref(q11), cov_staff_category = na_pref(q35), cov_grade = na_pref(q25),
           cov_recruitment = data, cov_survey_weight = as.numeric(mean_weight))]
stopifnot(uniqueN(d$id) == 280, nrow(d) == 280 * 14, !anyDuplicated(d[, .(id, task, profile)]),
          d[, sum(choice), .(id, task)][, all(V1 == 1)],
          all(d$cov_gender %in% c("male", "female", NA)),
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
# choicevar text agrees with the 0/1 coding
stopifnot(all((x$choicevar == paste("Contribution", x$profile_number)) == (x$choicevar_clean == 1)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "heinzel_2025_io_earmarking.csv"))
