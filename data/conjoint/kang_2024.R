##Assault-case prioritization conjoints with South Korean police investigators, from
##Kang, I., & Jilke, S. (2024). Mapping out the motivational basis of active representation as
##intergroup behavior. Public Administration, 102(1), 164-187. https://doi.org/10.1111/padm.12908
##(article CC BY-NC-ND; not read: the publisher blocks automated access, so design facts come
##from the deposit and its description).
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZT9R5W, CC0 1.0, no restricted files.
##Files read: "Study 1_replication data.tab" and "Study 2_replication data.tab" (Dataverse
##"original format" .dta, with Stata value labels). The two .do files were read as text (not
##run) for the variable meanings.
##Usage: Rscript kang_2024.R <dir holding s1.dta, s2.dta> <output dir>
##
##Deposit description: "Two large-scale conjoint experiments were performed using a unique
##sample of 1,929 frontline investigators in the National Police in South Korea." Two
##experiments with different attribute sets, so TWO tables (one per experiment):
##  kang_2024_police_priority_exp1: 1,294 investigators who answered (of 1,463 in the file),
##    attributes accuser age, accuser gender, accuser occupation, accused age, accused
##    reachability by phone, assault story.
##  kang_2024_police_priority_exp2: 631 investigators (632 answered, of 844; see below), attributes
##    accuser-and-accused age (one level for both), accuser occupation, accused occupation,
##    assault severity, accuser-accused relationship, accused's position (devaluation of women).
##1,294 + 632 = 1,926, close to the 1,929 reported; whether the two files share respondents
##cannot be told (both number ids from 1) and they are not linked.
##Each investigator saw 6 case profiles. The files have a profile index 1-6 but no task: task
##is INFERRED as consecutive profile pairs (1-2, 3-4, 5-6) and profile = 1/2 within the pair;
##in every answered pair exactly one case has DV = 1 (checked), so this is a paired forced
##choice. Outcome: choice = DV, "case prioritization" (the authors' do-file label): which of the
##two cases the investigator would prioritize; verbatim wording not in the deposit. Pairs with
##no answer (DV missing on both) are omitted; no opt-out is evident.
##Attribute text is the authors' English Stata value labels (e.g. "low-SES", "high-SES",
##"devaluation of women"); respondents saw Korean case descriptions that are not deposited, so
##the stored text is a coded summary of what was shown, not the displayed wording. In exp2 one
##attribute gives one age band for both accuser and accused. Randomization restrictions and
##attribute order are not documented, but occupation levels are unequal: in exp1 accuser
##occupation is unemployed on 14% of profiles (low-SES 44%, high-SES 42%), and in exp2 accuser
##and accused occupation are unemployed on about 8% (level_weights = observed; every pair of levels
##occurs, so no combination rule is visible). Spot check:
##exp1 cases with a female accuser are prioritized 57% of the time vs 43% for a male accuser.
##cov_gender = the investigator's gender as text (Stata value labels on gender: 1 "maleinvestigator"
##-> "male", 2 "femaleinvestigator" -> "female"; missing for 255 exp1 and 4 exp2
##answering respondents; the authors' models drop them). exp2: one answering respondent's 6
##rows have no attribute values and are dropped (631 respondents remain).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) as.character(as_factor(x, levels = "labels"))
build <- function(f, attrs) {
  k <- as.data.table(read_dta(file.path(raw, f)))
  stopifnot(k[, .N, id][, all(N == 6)], k[, all(sort(profile) == 1:6), id]$V1)
  d <- data.table(id = as.integer(k$id), task = as.integer((k$profile + 1) %/% 2), profile = as.integer(2 - k$profile %% 2),
                  choice = as.integer(zap_labels(k$DV)))
  for (nm in names(attrs)) d[, paste0("attr_", nm) := lab(k[[attrs[[nm]]]])]
  d[, cov_gender := c("male", "female")[as.integer(zap_labels(k$gender))]]
  stopifnot(identical(unname(attr(k$gender, "labels")), c(1, 2)), identical(names(attr(k$gender, "labels")), c("maleinvestigator", "femaleinvestigator")))
  stopifnot(d[, uniqueN(cov_gender), id][, all(V1 == 1)])
  d[, keep := !all(is.na(choice)) & !anyNA(.SD), .(id, task), .SDcols = paste0("attr_", names(attrs))]
  d <- d[keep == TRUE][, keep := NULL]
  stopifnot(!anyNA(d$choice), d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  d
}
d1 <- build("s1.dta", list(accuser_age = "accuser_age", accuser_gender = "accuser_gender", accuser_occupation = "accuser_occupation",
                           accused_age = "accused_age", accused_reachability = "accused_reachability", assault_story = "assault_story"))
d2 <- build("s2.dta", list(accuser_accused_age = "accuser_accused_age", accuser_occupation = "accuser_occup",
                           accused_occupation = "accused_occup", assault_severity = "assault_severity",
                           accuser_accused_relationship = "accuser_accused_relationship", accused_position = "accused_position"))
stopifnot(uniqueN(d1$id) == 1294, uniqueN(d2$id) == 631)
fwrite(d1, file.path(out, "kang_2024_police_priority_exp1.csv"))
fwrite(d2, file.path(out, "kang_2024_police_priority_exp2.csv"))
