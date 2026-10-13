##European responsibility-sharing in migration policy: paired-model conjoint, six EU countries, from
##Lutz, P., & Bachelet, M. (2026). Europe's immigration divide: multidimensional responsibility-sharing as a
##solution? Journal of European Public Policy, 1-28. https://doi.org/10.1080/13501763.2026.2636284
##Replication data: Taylor & Francis figshare doi:10.6084/m9.figshare.31434858 (version 2), CC BY 4.0. Files read:
##dataset.csv. Read as text only: replication_code.R (authors' R, not run), rjpp_a_2636284_sm7980.docx (supplementary
##material: survey instrument and appendix tables).
##Usage: Rscript lutz_2026.R <dir holding dataset.csv> <output dir>
##
##10,200 adult residents of Denmark, Germany, Greece, Hungary, Italy and Poland (1,700 each; quotas for age, gender and
##education; panel company Bilendi; fielded in the six national languages; commitment and attention checks). Each
##respondent evaluated TWO iterations (task 1 = Models A and B, task 2 = Models C and D; profile 1/2 within a task) of
##alternative designs for a common EU migration policy, full randomization of three attributes (supplement, Part III):
##  attr_protect  refugee protection: Cost sharing (money) / Relocation (people) / Harmonization (norms);
##  attr_control  migration control: joint protection of the European external borders (EU) / European support for
##                non-European countries (international);
##  attr_rules    bindingness: Voluntary / Mandatory (member states).
##Level text = the supplement's option descriptions (the data store the short codes money, people, norms, European,
##international, mandatory, voluntary; the mapping to the bracketed labels [money-sharing], [people-sharing],
##[norm-sharing], [EU control], [Int. control] is the supplement's). The attribute column border in the data is named
##attr_control here (supplement heading "Migration control").
##Outcomes (both tasks): choice = "Which of the two models of European migration policy do you favour? Model A or Model B"
##(forced choice, no opt-out); rating = "How would you rate Model A [B]?" 1 strongly disagree ... 7 strongly agree
##(higher = more favourable). The choice is missing for 424 respondents in task 1 and 451 in task 2 (profile1 / profile2 NA)
##though both ratings exist; those tasks keep their ratings and have choice NA on both profiles (not recoded).
##TABLE: one table, six countries pooled (the authors pool them with country fixed effects, replication_code.R
##"model_conjoint"; the instrument is one text translated into six languages; attribute text is the English supplement's).
##Order within the task: profile 1 = Model A (C), 2 = Model B (D); the data columns profile1A/B, profile2C/D.
##Check: the chosen model has the higher rating in 70% of tasks, the lower in 4.4%.
##Dropped: cluster / East / South (authors' regional grouping of countries), edu (duplicate of education), gender and age
##duplicates, the attitude batteries (ref_*, control_*, immig_preference, european_union: respondent attitudes, not part of the
##profiles). Covariates kept: cov_country; cov_gender (female/male/other: the deposit's text recode of the 1/2/3 item
##Male/Female/Other); cov_age; cov_education_group (authors' low/high split of the education item; the original answer
##categories are not in the file); cov_lrs (left-right self-placement as stored 1-11, although the instrument gives a
##0-10 scale: one point offset suspected, kept as stored, hence not named cov_left_right).
##No survey weight in the file.
##Respondent_ID: dataset.csv has a row-number column V1 (also used by the authors as Respondent_ID); ids are 1..10,200.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "dataset.csv"), encoding = "UTF-8")
stopifnot(nrow(d) == 10200, all(d$V1 == seq_len(nrow(d))))
pro <- c(money = "Cost sharing: states with few refugees support states with many refugees through financial solidarity",
         people = "Relocation: states with few refugees take in refugees from states with many refugees",
         norms = "Harmonization: uniform standards for assessing asylum applications within the EU")
ctl <- c(European = "Joint protection of the European external borders by the member states",
         international = "European support for non-European countries so that they prevent irregular migration to Europe")
rul <- c(voluntary = "Voluntary: each member state freely decides whether to participate in the common policy",
         mandatory = "Mandatory: member states are obliged to participate in the common policy")
mk <- function(prof, r1, r2, ch, p1, p2) {
  data.table(id = d$V1, task = prof, profile = rep(1:2, each = nrow(d)),
             choice = c(fifelse(is.na(ch), NA_integer_, as.integer(ch == "A")), fifelse(is.na(ch), NA_integer_, as.integer(ch == "B"))),
             rating = c(d[[r1]], d[[r2]]),
             attr_protect = unname(pro[c(d[[paste0("protect", p1)]], d[[paste0("protect", p2)]])]),
             attr_control = unname(ctl[c(d[[paste0("border", p1)]], d[[paste0("border", p2)]])]),
             attr_rules = unname(rul[c(d[[paste0("rules", p1)]], d[[paste0("rules", p2)]])]))
}
o <- rbind(mk(1L, "profile1A", "profile1B", d$profile1, "A", "B"), mk(2L, "profile2C", "profile2D", d$profile2, "C", "D"))
o[, rating := as.integer(rating)]
cov <- d[, .(id = V1, cov_country = country, cov_gender = gender, cov_age = as.integer(age), cov_education_group = edu, cov_lrs = as.integer(lrs))]
stopifnot(all(cov$cov_gender %in% c("female", "male", "other")), !anyNA(o[, .(attr_protect, attr_control, attr_rules, rating)]),
          all(d$age == d$`age...20` | is.na(d$age)))
o <- merge(o, cov, by = "id")
stopifnot(o[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], nrow(o) == 40800)
setorder(o, id, task, profile)
fwrite(o, file.path(out, "lutz_2026_responsibility_sharing.csv"))
