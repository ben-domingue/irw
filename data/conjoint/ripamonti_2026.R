##Government-transparency factorial survey from
##Ripamonti (2026), replication data for "Does being informed about government transparency boost trust?
##Exploring an overlooked mechanism" (Government Information Quarterly; the codebook gives 2024 and the data
##page the Dataverse title "Does being informed about government transparency boost trust? ..."; the paper DOI
##is not stated in the deposit, so doi is left blank).
##Replication data: Harvard Dataverse doi:10.7910/DVN/8T0XOD, CC BY 4.0. termsOfAccess is non-empty only
##because one file (long_data_restricted_demographics.tab, respondent demographics) is available on request;
##it was NOT requested or read. All files used are open.
##Files read: long_data_public.tab, codebook.md, appendix.pdf (questionnaire example, Section A; text only).
##Usage: Rscript ripamonti_2026.R <raw dir> <output dir>   (raw dir holds long_data_public.tab)
##
##200 US adults (online survey, 7-8 April 2024; 206 completed, 6 set aside by the block quota). Each read 8
##descriptions of a public organization in a hypothetical US city (one profile per task; task = round 1-8,
##recorded) from one of 20 blocks of 8 vignettes (trial_deck = block_number, 10 respondents per block).
##Five randomized factors:
##  attr_organization  "Police Department" / "Department of Sanitation and Environmental Services"
##  attr_disclosure_motive  "only discloses information that is strictly required by the State Freedom of Information
##                     Act" / "discloses more information than it is strictly required by the State Freedom of
##                     Information Act"  (the deposit stores the truncated tags "only discloses information that is" /
##                     "discloses more information than it is"; full text from the questionnaire example in the appendix)
##  attr_finance_transparency, attr_meetings_transparency, attr_performance_transparency:
##                     "very limited" / "abundant" (displayed as "In detail, they publish: very limited / abundant
##                     information about funding and expenditures / public meetings / their performance")
##Attribute level text for the motive taken from the article appendix; the deposit stores short tags.
##Outcomes (slider 0-100; "What percent of the time do you think citizens can trust the [organization]..."):
##  rating_principled  perc_int  "...to do their work in a principled or ethical way"
##  rating_city_interest  perc_ben  "...to do what is best for the city"
##  rating_efficient   perc_eff  "...to work in an efficient way (with minimal waste of time and resources)"
##perc_trust (their mean) is derived and dropped. No opt-out. The codebook reports the three transparency
##factors and the motive as having a stated reference level; that is analysis coding, not used here.
##Covariates (asked once before the vignettes, text of the codebook's labels): cov_importance_finance,
##cov_importance_meetings, cov_importance_performance (importance of government sharing that information: not at
##all important ... extremely important), cov_confidence_executive / _supreme_court / _congress / _military (confidence in
##the people running the institution: none at all ... a great deal). Derived averages avg_imp_tran and
##conf_median_index dropped. Demographics are not in the open file. respondent_id (R001-R200, arbitrary) re-keyed to integers.
##Count check: codebook: 200 respondents x 8 = 1,600 rows.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "long_data_public.tab"), sep = "\t")
stopifnot(nrow(d) == 1600, uniqueN(d$respondent_id) == 200, !anyDuplicated(d[, .(respondent_id, round)]))
mot <- c("only discloses information that is" = "only discloses information that is strictly required by the State Freedom of Information Act",
         "discloses more information than it is" = "discloses more information than it is strictly required by the State Freedom of Information Act")
stopifnot(all(d$motiv %in% names(mot)), all(d$org %in% c("Police Department", "Department of Sanitation and Environmental Services")))
imp <- c("not at all important", "slightly important", "moderately important", "very important", "extremely important")
cf <- c("none at all", "a little", "a moderate amount", "a lot", "a great deal")
x <- d[, .(id = match(respondent_id, sort(unique(respondent_id))), task = as.integer(round), profile = 1L,
  rating_principled = perc_int, rating_city_interest = perc_ben, rating_efficient = perc_eff,
  attr_organization = org, attr_disclosure_motive = unname(mot[motiv]), attr_finance_transparency = tran_fin,
  attr_meetings_transparency = tran_pm, attr_performance_transparency = tran_perf, trial_deck = as.integer(block_number),
  cov_importance_finance = imp[imp_tran_fin], cov_importance_meetings = imp[imp_tran_pm],
  cov_importance_performance = imp[imp_tran_perf], cov_confidence_executive = cf[conf_exe],
  cov_confidence_supreme_court = cf[conf_sup], cov_confidence_congress = cf[conf_con], cov_confidence_military = cf[conf_mil])]
stopifnot(!anyNA(x$attr_disclosure_motive), x[, all(c(rating_principled, rating_city_interest, rating_efficient) >= 0 & c(rating_principled, rating_city_interest, rating_efficient) <= 100)])
setorder(x, id, task, profile); fwrite(x, file.path(out, "ripamonti_2026_transparency_trust.csv"))
cat(nrow(x), uniqueN(x$id), "\n")
