##Social-assistance reform conjoint (Denmark) from
##Larsen, M. H. (2025). Politics of welfare exclusion: Open and concealed welfare chauvinism
##and public support for social assistance reform. Acta Sociologica (online 2025-07-04).
##https://doi.org/10.1177/00016993251351544
##Replication data: Harvard Dataverse doi:10.7910/DVN/IQVXTC, CC0 1.0, no restricted files.
##File read: Chauv_policy.tab (Dataverse "original format" download, a Stata 118 .dta). The
##author's Chauv_policy.Rmd was read as text: it is the source of the choice coding and of
##every attribute level label (case_when recodes); the .dta holds only level codes.
##Usage: Rscript larsen_2025.R <raw dir> <output dir>
##
##1,287 Danish online respondents (Sawtooth CBC, design CBC1_1652092410_0, fielded
##2022-05-09 to 2022-05-19), 4 tasks x 2 reform proposals (task, concept = left/right),
##10 attributes, 10,296 rows. One table.
##choice: CBC_Random<t> holds the concept (1 = left, 2 = right) chosen in task t (author's Rmd
##  "Binary outcome: was the social assistance reform proposal chosen?"). Forced choice, no
##  opt-out; exactly one chosen per task (checked). The question wording is not deposited and
##  the article PDF was not reachable from here: design_outcomes carries a paraphrase.
##Levels are the author's ENGLISH recode labels (Rmd); respondents saw Danish text that is
##not deposited. Attributes (Danish .dta variable labels -> author's English):
##  attr_proposer          "Forslagstiller": Party from red bloc / Party from blue bloc
##  attr_work_requirement  "Krav om udført arbejde inden for de sidste 12 måneder":
##                         No work requirements / 225 hours / 225 hours both partners in a
##                         union / 300 hours both partners in a union (the Rmd's table labels
##                         read "Must have worked minimum 225 hours last 12 months. Rule also
##                         applies to spouse"; "in a union" here means married/cohabiting)
##  attr_residence_requirement "Bopælskrav": Residency in DK / Lived in DK 3 out of 4 years /
##                         ... 9 out of 10 years / ... 10 out of 11 years
##  attr_rate_noncitizens  "Kontanthjælpsats for personer uden statsborgerskab"
##  attr_rate_disabled     "Kontanthjælpssats for personer med handicap"
##  attr_rate_parents      "Kontanthjælpsats for forældre med hjemmeboende børn"
##  attr_sanction          "Sanktion ved udeblivelse fra et møde med jobcentret"
##  attr_job_offer         "Krav om accept af jobtilbud der stemmer overens med faglige kvalifikat[ioner]"
##  attr_job_training      "Krav om deltagelse i jobtræning"
##  attr_tax_cost          "Årlig skattestigning som følge af reformen (Til sammenligning betaler...":
##                         Lower / Same / Higher personal costs than previous reform (the
##                         author's Figure 1 labels these "Pay 0.5% less in annual taxes" / "No
##                         change in annual taxes" / "Pay 0.5% more in annual taxes"; the
##                         Rmd case_when labels are stored).
##attrpos_<attr>: attribute row order, randomized once per respondent (qOrder, e.g.
##  /2/6/10/1/3/8/9/4/5/7/ = attribute numbers in display order; one qOrder per respondent;
##  the author's Rmd decodes it the same way, Residence_row/Citizenship_row).
##Covariates (text from the .dta value labels, Danish): cov_gender (bagg2 "Er du?": 1 Mand =
##  male, 2 Kvinde = female, 3 Andet = other); cov_age (bagg1_o1, years as typed; NA for 3
##  respondents who withheld age); cov_age_group (bagg1_a band text, asked only of those who
##  withheld age); cov_region; cov_education (bagg5 "Hvad er din højest gennemførte
##  uddannelse?"); cov_employment (bagg6); cov_income (bagg7, gross annual income band);
##  cov_unemployment_worry (Q1); cov_vote_intention (Q2 "Hvem vil du stemme på, hvis der var
##  folketingsvalg i morgen?", a vote intention, not party id); cov_welfare_news (Q3);
##  cov_duration_sec = ActualSurveyEndTime - ActualSurveyStartTime (whole survey);
##  cov_survey_weight = wgt (used as weights in the author's models).
##Dropped: start/end timestamps, operating system, the row id `id`, the derived alder_kat /
##  udd_kat / køn, Sawtooth design fields. CBC_Id (Sawtooth respondent number) re-keyed to
##  integers. The author's Rmd drops CBC_Id 530, which is not in the deposited file.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "Chauv_policy.tab"))
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y[is.na(zap_labels(x))] <- NA; y }
k <- as.data.table(zap_labels(s))
k[, ord := as.integer(CBC_Id)]
k[, id := match(ord, sort(unique(ord)))]
k[, task := as.integer(task)]; k[, profile := as.integer(concept)]
pick <- k[, cbind(CBC_Random1, CBC_Random2, CBC_Random3, CBC_Random4)][cbind(seq_len(nrow(k)), k$task)]
k[, choice := as.integer(pick == profile)]
rec <- function(x, labs) { stopifnot(all(x %in% seq_along(labs))); labs[x] }
d <- k[, .(id, task, profile, choice)]
d[, attr_proposer := rec(k$attr01forslagstiller, c("Party from red bloc", "Party from blue bloc"))]
d[, attr_work_requirement := rec(k$Attr02Kravomudførtarbejdeindenfo, c("No work requirements", "225 hours",
     "225 hours both partners in a union", "300 hours both partners in a union"))]
d[, attr_residence_requirement := rec(k$Attr03Bopælskrav, c("Residency in DK", "Lived in DK 3 out of 4 years",
     "Lived in DK 9 out of 10 years", "Lived in DK 10 out of 11 years"))]
d[, attr_rate_noncitizens := rec(k$Attr04Kontanthjælpsatsforpersone, c("Non-citizens receive 50% less",
     "Non-citizens receive 25% less", "Non-citizens receive the same"))]
d[, attr_rate_disabled := rec(k$Attr05Kontanthjælpssatsforperson, c("Disabled receive 50% more",
     "Disabled receive 25% more", "Disabled receive the same"))]
d[, attr_rate_parents := rec(k$Attr06Kontanthjælpsatsforforældr, c("Parents receive 50% more",
     "Parents receive 25% more", "Parents receive the same"))]
d[, attr_sanction := rec(k$Attr07Sanktionvedudeblivelsefrae, c("No sanctions",
     "Receive 10% less the following month", "Receive 20% less the following month"))]
d[, attr_job_offer := rec(k$attr08kravomacceptafjobtilbudder, c("Required to accept joboffer that matches skills",
     "Not required to accept joboffer that matches skills"))]
d[, attr_job_training := rec(k$Attr09Kravomdeltagelseijobtrænin, c("Required to participate in job training",
     "Not required to participate in job training"))]
d[, attr_tax_cost := rec(k$Attr10Årligskattestigningsomfølg, c("Lower personal costs than previous reform",
     "Same personal costs as previous reform", "Higher personal costs than previous reform"))]
an <- c("proposer", "work_requirement", "residence_requirement", "rate_noncitizens", "rate_disabled",
        "rate_parents", "sanction", "job_offer", "job_training", "tax_cost")
po <- lapply(strsplit(gsub("^/|/$", "", k$qOrder), "/"), as.integer)
stopifnot(all(vapply(po, function(p) identical(sort(p), 1:10), TRUE)))
for (j in 1:10) d[, paste0("attrpos_", an[j]) := vapply(po, function(p) match(j, p), 1L)]
g <- zap_labels(s$bagg2); stopifnot(all(g %in% 1:3))
d[, cov_gender := c("male", "female", "other")[g]]
age <- zap_labels(s$bagg1_o1); age[!(age %in% 18:110)] <- NA
d[, cov_age := as.integer(age)]
d[, cov_age_group := lab(s$bagg1_a)]
d[, cov_region := lab(s$Region)]
d[, cov_education := lab(s$bagg5)]
d[, cov_employment := lab(s$bagg6)]
d[, cov_income := lab(s$bagg7)]
d[, cov_unemployment_worry := lab(s$Q1)]
d[, cov_vote_intention := lab(s$Q2)]
d[, cov_welfare_news := lab(s$Q3)]
d[, cov_duration_sec := as.integer(round(as.numeric(difftime(s$ActualSurveyEndTime, s$ActualSurveyStartTime, units = "secs"))))]
d[, cov_survey_weight := as.numeric(s$wgt)]
stopifnot(d[, .(n = .N, ch = sum(choice)), by = .(id, task)][, all(n == 2 & ch == 1)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "larsen_2025_welfare_chauvinism.csv"))
