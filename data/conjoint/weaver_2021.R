##Municipal candidate conjoint in Peru from
##Weaver, J. A. (2021). Electoral dis-connection: The limits of re-election in contexts of weak
##accountability. The Journal of Politics, 83(4), 1462-1477. https://doi.org/10.1086/711901
##Replication data: Harvard Dataverse doi:10.7910/DVN/V8U06V, CC0 1.0, no restricted files.
##File read: conjoint.data, downloaded in its original format (an .RData holding one data frame
##of the same name, one row per profile seen; loaded into its own environment). Read as text:
##README.txt and the author's ReplicationScript_..._MainText.R (its attribute_list and baselines,
##lines 147-163, name the levels; it supplies no covariate codebook).
##Usage: Rscript weaver_2021.R <dir holding conjoint.data> <output dir>
##
##1,037 Peruvian respondents, 1 to 4 tasks each (814 saw four), two municipal mayoral candidates
##per task: 3,788 tasks, 7,576 rows, every task with exactly one chosen profile. The deposit's
##levels are English, while the survey was fielded in Peru and one attribute is the candidate's
##language, so the stored level text is the author's English rendering (label_language en,
##display_language unknown: the deposit ships no instrument).
##
##Design. Eight attributes, all as displayed text: incumbency with performance information
##(attr_incumbent: Challenger, or Incumbent with no / good / bad performance information about
##public works or financial aid), membership of social organizations (attr_soc_orgs, Yes / No),
##home village (attr_village), occupation (attr_work), language (attr_language, Spanish /
##Quechua), political family (attr_dynasty), campaign gifts (attr_gifts) and gender
##(attr_gender). Every task pairs exactly one Challenger with exactly one Incumbent, so
##attr_incumbent is blocked: Challenger is 0.50 of profiles and each of the five incumbent
##variants about 0.10. attr_gender is also unequal (male 0.64, female 0.36). The other six
##attributes are 50/50. Attribute order is not recorded.
##
##Outcome. choice: which of the two candidates the respondent would vote for
##(outcome_votechoice_binary; forced, exactly one per task). No wording survives in the deposit.
##
##Covariates. The conjoint file carries the respondent variables the author used, all as bare
##codes with no codebook, so they keep the codes under _code names: cov_gender_code (0/1),
##cov_education_code (1-9), cov_age_group_code (1-3), cov_income_quantile (1-4). Two further
##respondent-level items are kept as given: cov_quechua_mother_tongue (1 = Quechua) and the two
##beliefs the author interacts with the attributes, cov_repeat_likely (the mayor is likely to
##run again) and cov_learn_to_be_corrupt (politicians learn to be corrupt in office); both are
##0/1 and constant within respondent.
##NOT carried: survey.data, the separate respondent-level survey file (1,061 rows of attitude
##items with no codebook); it keys on unique.ID and holds nothing the conjoint analysis uses.
##No survey weight ships with the deposit. respondentID is already an integer with no platform
##identifier; it is re-keyed 1..n in first-appearance order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "conjoint.data"), envir = e)
s <- as.data.table(as.data.frame(e$conjoint.data))
stopifnot(nrow(s) == 7576L, uniqueN(s$respondentID) == 1037L)

d <- data.table(
  id = as.integer(frank(s$respondentID, ties.method = "dense")),
  task = as.integer(s$`Task Number`),
  profile = 2L - as.integer(s$`First Profile`),
  choice = as.integer(s$outcome_votechoice_binary),
  attr_incumbent = as.character(s$feat.incumbent),
  attr_soc_orgs = as.character(s$feat.soc.orgs),
  attr_village = as.character(s$feat.village),
  attr_work = as.character(s$feat.work),
  attr_language = as.character(s$feat.lang),
  attr_dynasty = as.character(s$feat.dynasty),
  attr_gifts = as.character(s$feat.gifts),
  attr_gender = as.character(s$feat.gender),
  cov_gender_code = as.integer(s$gender.binary),
  cov_education_code = as.integer(s$educ_noNA),
  cov_age_group_code = as.integer(s$age.category.numeric),
  cov_income_quantile = as.integer(s$income.quantile),
  cov_quechua_mother_tongue = as.integer(s$idioma.materno.quechua),
  cov_repeat_likely = as.integer(s$`Repeat Likely`),
  cov_learn_to_be_corrupt = as.integer(s$`Learn to be Corrupt`))

stopifnot(d[, .N, .(id, task)][, all(N == 2L)],
          d[, sum(choice), .(id, task)][, all(V1 == 1L)],
          d[, uniqueN(profile), .(id, task)][, all(V1 == 2L)],
          !anyNA(d[, grep("^attr_", names(d)), with = FALSE]),
          d[, sum(attr_incumbent == "Challenger"), .(id, task)][, all(V1 == 1L)],
          d[, uniqueN(id)] == 1037L, nrow(d) == 7576L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "weaver_2021_peru_mayors.csv"))
