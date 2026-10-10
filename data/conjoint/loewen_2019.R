##Candidate-depression vignette conjoints (USA and Canada, 2017) from
##Loewen, P. J., & Rheault, L. (2021). Voters punish politicians with depression. British Journal
##of Political Science, 51(1), 427-437 (FirstView 2019). https://doi.org/10.1017/S0007123419000127
##Replication data: Harvard Dataverse doi:10.7910/DVN/DHWZYE, CC0 1.0, no restricted files.
##Files read: depression_usa.tab and depression_can.tab (original-format CSV downloads, saved as
##usa.csv / can.csv), codebook_usa.tab / codebook_can.tab (variable descriptions only). The
##authors' R scripts (depression_main_models.R, depression_appendix.R) were read as text. The
##article is paywalled; the vignette template is not deposited.
##Usage: Rscript loewen_2019.R <raw dir holding usa.csv and can.csv> <output dir>
##
##Each respondent read two pairs of short candidate descriptions, one task each:
##  "open seat" session: Candidates A and B (profile 1 = A, 2 = B);
##  "incumbent" session: Candidates C (the incumbent) and D (profile 1 = C, 2 = D).
##The two sessions have different attribute sets and the two countries different texts and
##analyses (Canada in the appendix), so FOUR tables, one task each:
##  loewen_2019_depression_open_us (966 respondents), loewen_2019_depression_incumbent_us (967),
##  loewen_2019_depression_open_ca (779), loewen_2019_depression_incumbent_ca (779).
##The same respondents (re-keyed ids, shared within a country) appear in both tables of a country.
##Outcomes (forced choice between the two candidates, no opt-out; codebook descriptions, wording
##not deposited): choice = vote ("Vote, Open Seat/Incumbent Session"); choice_prepared
##("Candidate Most Prepared"), choice_trust ("Candidate Most Trustworthy"), choice_character
##("Candidate with Best Character"). A few US respondents have no answers in a session (5 open,
##4 incumbent); their rows are omitted.
##Attributes = the text fragments stored per candidate (piped into the vignette; e.g. race "a
##Caucasian", experience "five years of experience as a local councillor", tax "small business",
##guns "limited"/"no"); the sentences around them are not deposited, so a fragment such as "no"
##(guns) reads only in its sentence. attr_gender = female/male (Canadian file: pronoun He/She
##piped into the text; pronoun columns are dropped as duplicates of gender).
##Health treatment (the paper's manipulation):
##  open seat: Candidate A's condition = illnessA (the authors' factor labels "Blood Pressure",
##  "Cancer", "Depression" for randomization codes A/B/C; the displayed sentence is not
##  deposited); Candidate B has no health information -> "(not shown)". attr_leave = A's leave of
##  absence: Canadian text "one week"/"two weeks"/"six weeks"; the US file has only `leave` in
##  weeks (1/2/6), mapped to the same Canadian wording (inferred); Blood Pressure has no leave
##  (leave 0, blank in the Canadian text) -> "(not shown)" (inferred), as on B.
##  incumbent: Candidate C's illness = candidate_C_illness text ("a severe case of the flu",
##  "depression", "skin cancer"), attr_attendance = C's voting attendance ("70%".."100%"); D has
##  neither -> "(not shown)". Canada adds D's military sentence ("He/She supports military
##  engagements abroad.") which is EMPTY on 375 of 779 D profiles: stored as "(not shown)",
##  inferred to be a sentence the design omitted (no "opposes" text exists). C has no military
##  attribute -> "(not shown)".
##Restrictions: the two candidates of a pair always have opposite parties (observed in every
##task; not documented). Health/leave/attendance only on A and C (by design). Level weights not
##documented (shares near-equal).
##Covariates: cov_age (years); cov_gender_code (0/1, no codebook mapping); cov_education_code
##(US 1-6, Canada 1-5; no labels deposited); cov_party_id (US pid_factor text: A Democrat / A
##Republican / An independent / None of these); cov_english_first (US, 0/1); cov_born_canada
##(Canada, 0/1); cov_depression_prevalence ("1 in 10 people" ...), cov_depression_chance,
##cov_depression_experience (prior experience with depression), cov_depression_help (did you or
##someone close seek help) as stored text.
##Dropped: hashed respondent ids (id, Canadian ResponseId; re-keyed to integers), RecordedDate,
##the authors' recodes (*_numeric, pid, leave/missed numeric, illnessC factor, ab_/cd_depression
##dummies, health_randomization letter), pronoun columns, and the duplicate candidate_C_illness.1.
##N: US file 971 respondents, Canada 779 (article and appendix N not checked: paywalled).
##No survey weight in the deposit. No repeated task.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ns <- "(not shown)"
leave_txt <- c("1" = "one week", "2" = "two weeks", "6" = "six weeks")
nz <- function(x) !is.na(x) & nzchar(x)
pick <- function(v, l1, l2) { stopifnot(all(v %in% c(l1, l2, NA, ""))); ifelse(v == l1, 1L, ifelse(v == l2, 0L, NA_integer_)) }
build <- function(s, ctry) {
  s[, rid := .I]
  covs <- s[, .(rid, cov_age = as.integer(age), cov_gender_code = as.integer(gender), cov_education_code = as.integer(education),
                cov_depression_prevalence = depression_prop, cov_depression_chance = depression_chance,
                cov_depression_experience = if (ctry == "us") depression_exp else depression_expericne,
                cov_depression_help = depression_help)]
  if (ctry == "us") covs[, `:=`(cov_party_id = s$pid_factor, cov_english_first = as.integer(s$english))]
  else covs[, cov_born_canada := as.integer(s$bicanada)]
  pre <- if (ctry == "us") "" else "conj_"
  sess <- function(P, Q, oc, extra) {
    rows <- lapply(1:2, function(k) {
      c0 <- c(P, Q)[k]; lab <- paste("Candidate", c0)
      g <- function(v) s[[sprintf("candidate_%s_%s", c0, v)]]
      d <- s[, .(rid, task = 1L, profile = k,
                 choice = pick(get(paste0(oc, "_vote")), lab, paste("Candidate", c(P, Q)[3 - k])),
                 choice_prepared = pick(get(paste0(pre, oc, "_prepared")), lab, paste("Candidate", c(P, Q)[3 - k])),
                 choice_trust = pick(get(paste0(pre, oc, "_trust")), lab, paste("Candidate", c(P, Q)[3 - k])),
                 choice_character = pick(get(paste0(pre, oc, "_character")), lab, paste("Candidate", c(P, Q)[3 - k])))]
      d[, `:=`(attr_age = as.character(g("age")), attr_gender = g("gender"), attr_race = g("race"), attr_party = g("party"))]
      if (ctry == "ca") d[, attr_occupation := g("occupation")]
      extra(d, c0, g)
      d
    })
    d <- rbindlist(rows, use.names = TRUE)
    d <- d[!is.na(choice) | !is.na(choice_prepared) | !is.na(choice_trust) | !is.na(choice_character)]
    for (v in c("choice", "choice_prepared", "choice_trust", "choice_character"))
      stopifnot(d[, sum(get(v)), .(rid, task)][, all(V1 == 1)])
    stopifnot(d[, uniqueN(attr_party), rid][, all(V1 == 2)])
    for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(all(nz(d[[v]])))
    d
  }
  open <- sess("A", "B", "ab", function(d, c0, g) {
    d[, `:=`(attr_experience = g("experience"), attr_abortion = g("abortion"))]
    if (ctry == "us") d[, attr_guns := g("guns")] else d[, attr_military := g("military")]
    d[, attr_tax := g("tax")]
    if (c0 == "A") {
      stopifnot(all(s$illnessA %in% c("Blood Pressure", "Cancer", "Depression")),
                all((s$illnessA == "Blood Pressure") == (s$leave == 0)))
      lv <- if (ctry == "us") unname(leave_txt[as.character(s$leave)]) else s$candidate_A_leave
      if (ctry == "ca") stopifnot(all(unname(leave_txt[as.character(s$leave[s$leave > 0])]) == lv[s$leave > 0]))
      d[, `:=`(attr_health = s$illnessA, attr_leave = fifelse(s$leave == 0, ns, lv))]
    } else d[, `:=`(attr_health = ns, attr_leave = ns)]
  })
  inc <- sess("C", "D", "cd", function(d, c0, g) {
    if (ctry == "us") d[, attr_healthcare := g("healthcare")] else d[, attr_daycare := g("daycare")]
    if (c0 == "C") {
      stopifnot(all(s$candidate_C_attendance %in% c("70%", "80%", "90%", "100%")))
      d[, `:=`(attr_illness = s$candidate_C_illness, attr_attendance = s$candidate_C_attendance)]
      if (ctry == "ca") d[, attr_military := ns]
    } else {
      d[, `:=`(attr_illness = ns, attr_attendance = ns)]
      if (ctry == "ca") d[, attr_military := fifelse(nz(g("military")), g("military"), ns)]
    }
  })
  for (nm in c("open", "incumbent")) {
    d <- merge(if (nm == "open") open else inc, covs, by = "rid")
    d[, id := rid][, rid := NULL]
    setcolorder(d, c("id", "task", "profile"))
    setorder(d, id, task, profile)
    fwrite(d, file.path(out, sprintf("loewen_2019_depression_%s_%s.csv", nm, ctry)))
  }
}
build(fread(file.path(raw, "usa.csv"), na.strings = c("", "NA")), "us")
build(fread(file.path(raw, "can.csv"), na.strings = c("", "NA")), "ca")
