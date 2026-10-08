##Candidate task-priority conjoint (UK and US samples) from
##Pedersen, H. H. (2025). Legislator or representative? Politicians' tasks according to
##voters. British Journal of Political Science. https://doi.org/10.1017/S0007123425101245
##Replication data: Harvard Dataverse doi:10.7910/DVN/50RWSI, CC0 1.0, no restricted files.
##File read: "Legislator or Representative Wide.dta" (Dataverse "original format" download of
##the .tab; one row per respondent, value labels carry the level text). Design facts from the
##article's Research Design section; readme-1.docx and Replication-1.do read as text only.
##Usage: Rscript pedersen_2025.R <raw dir> <output dir>
##
##YouGov samples, 6-23 January 2025: Denmark 2,454, Germany 2,095, UK 2,849, US 2,554
##respondents (9,952 rows; 1,427 did not consent and have no conjoint data). Four forced-choice
##tasks (q4a_taskeen1-4): "Which of the two candidates would you be most inclined to vote for
##if there were ..." (label truncated in the file), Candidate 1 / Candidate 2, no opt-out. The
##article: respondents consider a candidate "running for a party whom they would consider
##voting for". choice = 1 for the chosen candidate.
##Six displayed attributes, levels = the value labels in the file: first name (60 names: 1-20
##majority female, 21-30 Turkish female, 31-50 majority male, 51-60 Turkish male, per the
##authors' recodes), surname (1-20 majority, 21-40 Turkish), age (25-34, 40-54, 60-65 in
##years), years in profession before parliament (1-3, 7-9, 13-15 years), occupation (25,
##grouped by the authors into short/medium/long education) and task priority (8 statements,
##odd = functional, even = relational). RESTRICTION (article): young candidates (25-34) always
##have short (1-3 years) work experience. In the data the surname's origin always matches the
##first name's (majority first names only with the 20 majority surnames, Turkish with the 20
##Turkish ones); not stated in the sources read. Attribute order not recorded.
##TABLES: the deposit's value labels are ONE English master set (UK-oriented: "Parliament",
##UK surnames). The article analyses each country separately, and the other surveys showed
##localised text (the US task list says "House of Representatives"; the Danish and German
##surveys were in Danish and German, and German male candidates carry German-language codes
##101-125 in the file). Two tables are built here, one per English-language sample:
##pedersen_2025_mp_tasks_uk (labels very likely as displayed) and pedersen_2025_mp_tasks_us
##(English master labels; the US screens probably said House/Congress instead of Parliament,
##not verifiable). DENMARK AND GERMANY ARE HELD: the majority names shown there were
##presumably Danish/German names, which the deposit does not hold, so the level text as
##displayed is not recoverable.
##Covariates: cov_gender ("Gender", .dta value labels 1 Female, 2 Male -> female/male); cov_age (years); cov_trust_mps (q9) 1=no trust ..
##7=a great deal, 8=don't know; cov_interest_politics (q16) 1=not at all .. 4=very
##interested; cov_left_right (q17) 1=left .. 7=right, 8=don't know; cov_task_importance_1..10
##(q2_1-q2_10, importance of the ten tasks listed in the appendix, 0=not important at all ..
##10=very important, 11=don't know); cov_task_time_1..10 (q3_*_1, share of time 0-100).
##Dropped: survey duration (duration, unit not documented; no survey weight in the file), the
##authors' age bands and derived indices; respondents with no
##conjoint answers (did not consent).
##N: UK 2,231 and US 2,185 respondents answered the conjoint (2,849 and 2,554 in the article
##are all who entered). Spot check (lm of choice on majority-name and female-name dummies
##only, SEs clustered by id): UK 0.044 / 0.032, US 0.030 / 0.017, within 0.001 of Figure 3
##(UK 0.045 / 0.033, US 0.031 / 0.016; the authors' model has all attributes).
##The first-name label "Mathhew" is kept as stored.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Legislator or Representative Wide.dta"))
stopifnot(nrow(k) == 9952)
lab <- function(x) as.character(as_factor(x))
atts <- c(attr1 = "first_name", attr2 = "surname", attr3 = "age", attr4 = "years_in_profession", attr5 = "occupation", attr6 = "task_priority")
num <- function(v) as.integer(zap_labels(k[[v]]))
stopifnot(all(num("gender") %in% 1:2))
cv <- data.table(cov_gender = c("female", "male")[num("gender")], cov_age = num("age"), cov_trust_mps = num("q9"), cov_interest_politics = num("q16"),
                 cov_left_right = num("q17"))
for (i in 1:10) cv[, paste0("cov_task_importance_", i) := num(paste0("q2_", i))]
for (i in 1:10) cv[, paste0("cov_task_time_", i) := as.numeric(k[[paste0("q3_", i, "_1")]])]
rows <- list()
for (t in 1:4) for (p in 1:2) {
  ch <- num(paste0("q4a_taskeen", t))
  d <- data.table(row = seq_len(nrow(k)), country = num("monadic"), task = t, profile = p, choice = as.integer(ch == p))
  for (v in names(atts)) {
    x <- k[[paste0("q_", v, "_concept", p, "_task", t)]]
    if (v %in% c("attr5", "attr6")) stopifnot(all(zap_labels(x)[num("monadic") != 4] < 100, na.rm = TRUE))
    d[, paste0("attr_", atts[[v]]) := lab(x)]
  }
  rows[[length(rows) + 1]] <- cbind(d, cv)
}
d <- rbindlist(rows)
d <- d[!is.na(choice)]
stopifnot(d[, .N, row][, all(N == 8)], !anyNA(d$attr_first_name), !anyNA(d$attr_task_priority))
stopifnot(d[, sum(choice), .(row, task)][, all(V1 == 1)])
# young candidates always have short experience
stopifnot(d[as.integer(attr_age) < 35, all(attr_years_in_profession %in% c("1 year", "2 years", "3 years"))])
for (cc in list(c(2, "uk"), c(3, "us"))) {
  s <- d[country == as.integer(cc[1])]
  s[, id := match(row, sort(unique(row)))]
  s[, c("row", "country") := NULL]
  setcolorder(s, c("id", "task", "profile", "choice"))
  setorder(s, id, task, profile)
  fwrite(s, file.path(out, paste0("pedersen_2025_mp_tasks_", cc[2], ".csv")))
}
