##Ideology-label candidate conjoint (Study 2) from
##Trexler, A., & Johnston, C. D. (2025). An ideology by any other name. Political Behavior,
##47(1), 385-409. https://doi.org/10.1007/s11109-024-09955-5
##Replication data: Harvard Dataverse doi:10.7910/DVN/XOWWHF, CC BY 4.0, no restricted files,
##no terms. Files read: data_study2.csv (Dataverse "original format" download of
##data_study2.tab). Attribute text is stored in the data; coding facts from _README.txt
##(deposit codebook) and the authors' Analysis_Study2.R (read as text). Study 1 of the
##deposit (data_study1) is a plain survey, not a conjoint, and is not used.
##Usage: Rscript trexler_2025.R <raw dir> <output dir>
##
##US online sample (2023; the authors' code computes age as 2023 - birth year), 2,941 rows
##in the file. Respondents were randomized to a general-election or a primary-election
##condition (trial_election) and to a party (trial_embed_pid, "Assignment to Republican or
##Democratic condition"; in the primary condition it selects the Democratic or Republican
##primary profile set; what it changed in the general condition is not documented), then
##made 7 choices (task 1-7) between two candidates (A = profile 1, B = profile 2).
##Each profile showed 5 issue positions and an ideology label. The 5 issue positions are
##drawn from a pool of 27 issues (each with two sides, e.g. "SUPPORT the death penalty." /
##"OPPOSE the death penalty."); one column per issue, attr_<issue> = the displayed sentence,
##or "(not shown)" when that issue was not among the profile's five; attrpos_<issue> = its
##row (1-5) among the issue rows, NA when not shown. No profile has the same issue twice
##(checked). attr_ideology = the candidate's ideology label (Conservative, Environmentalist,
##Liberal, Libertarian, Nationalist, Progressive, Socialist, Traditional). About a third of
##profiles have an empty label; these are coded "(not shown)". INFERRED: no deposited source
##says an empty label was displayed as nothing; the authors' code treats it as the
##reference category of their label dummies (Analysis_Study2.R cid_* coding). Where the
##label sat relative to the issue rows is not documented.
##Level shares are NOT uniform and differ by arm: in the Democratic-primary set left-leaning
##positions and labels (Liberal, Progressive, Socialist, Environmentalist) are drawn about 4x
##as often as the others; in the Republican-primary set Conservative, Traditional, Nationalist,
##Libertarian and right-leaning positions. In the general set labels and the two sides of each
##issue appear about equally often (no source gives the probabilities).
##Analyses should condition on trial_election x trial_embed_pid.
##Outcome (codebook X*_choice_**): "Candidate preference for conjoint decision tasks",
##1 = Strongly prefer A, 2 = Slightly prefer A, 4 = Slightly prefer B, 5 = Strongly prefer B
##(no midpoint, no opt-out; source codes kept in trial_preference on both rows of the task).
##choice = 1 for the preferred candidate (codes 1-2 -> A, 4-5 -> B), as in the authors'
##vote_can coding. Tasks with no answer are omitted; respondents with no answered task
##(391, mostly breakoffs) are absent.
##The authors analyse 2,433 respondents after dropping attention-check failures, breakoffs
##(Progress < 98) and respondents with >1 quality flag (age/birth-year mismatch, zip/state
##mismatch, junk open-ended answer, speeding, low reCAPTCHA) or >1 implausible label pair;
##this table keeps everyone who answered a task, with both attention checks as covariates.
##Covariates (codebook): cov_gender (1 male, 2 female, 3 something else -> other);
##cov_age = screen_age ("Age (in years) reported during screening"); cov_birth_year = the
##codebook's `age` ("Reported birth year"; kept only 1900-2005); cov_attention_pass_1
##(check1 == 1, the authors' pass rule); cov_attention_pass_2 (check2_3 and check2_4 ticked
##and 1, 2, 5 not ticked, the authors' rule); cov_duration_sec (total survey duration);
##cov_progress. Codes kept with codebook meanings: cov_party_id7_code (pid, 1 Strong Democrat .. 7 Strong
##Republican; middle labels not in the codebook, so not mapped to text);
##cov_selfplace (1 extremely liberal .. 7 extremely conservative); cov_id_* (self-
##identification with each of 14 labels, 0/1); cov_id_cnt; cov_mostimp; cov_strength_1..4;
##cov_news (days per week); cov_polatt (1 always .. 5 never); cov_race_1..8 (1 = ticked:
##white, black, hispanic, asian, native american, middle eastern, mixed, other);
##cov_employ (1 full time, 2 part time, 3 unemployed, 4 retired, 5 homemaker, 6 student,
##7 something else); cov_education_code (1 less than high school .. 6 postgraduate; middle
##labels not in the codebook); cov_income (1 < $10,000 .. 13 > $150,000); cov_state_code
##(screening state, codes unlabelled).
##Dropped: zip_code (PII), free text (source, otherlabel_2_TEXT), RecordedDate, the
##reCAPTCHA score, page timings, check2_* items, otherlabel. No survey weight in the deposit.
##N: 2,550 respondents answered >= 1 task (35,320 rows); 2,508 pass both attention checks with
##Progress >= 98; the paper analyses 2,433 after its further quality flags. Sanity check: in the
##primary arms a co-ideological label raises the choice share (Democratic primary: Liberal .52,
##Conservative .42; Republican primary: Conservative .57, Socialist .42).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data_study2.csv"))
s[, rid := .I]
M <- as.matrix(s[, grep("^(choice|Dprim|Rprim)[1-7]_(attr|ideo)_", names(s)), with = FALSE])
issues <- c("import taxes on non-American goods." = "import_taxes", "restrictions on possession of guns." = "gun_possession",
  "government-run universal healthcare program." = "universal_healthcare", "restrictions on sale of firearms." = "firearm_sales",
  "military strike on Iran's nuclear facilities." = "iran_strike",
  "legal status for employed, taxpaying, undocumented immigrants." = "legal_status_immigrants",
  "taxes on the wealthy." = "taxes_wealthy", "carbon tax to reduce greenhouse gas emissions." = "carbon_tax",
  "allowing doctors to prescribe marijuana." = "medical_marijuana",
  "parental consent requirements for teen abortions." = "parental_consent_abortion",
  "school-choice voucher programs." = "school_vouchers", "marriage equality for same-sex couples." = "marriage_equality",
  "legalizing recreational marijuana." = "recreational_marijuana",
  "US contributions to UN peacekeeping missions." = "un_peacekeeping", "government funding for the arts." = "arts_funding",
  "citizenship for undocumented immigrants brought to US as children." = "dreamers_citizenship",
  "affirmative action for racial minorities." = "affirmative_action",
  "religious exemptions that allow employers to avoid paying for birth control." = "religious_exemptions",
  "offshore oil drilling." = "offshore_drilling", "legal abortion after 15 weeks of pregnancy." = "abortion_15_weeks",
  "the death penalty." = "death_penalty", "American involvement in global affairs." = "global_involvement",
  "government spending to stimulate economic growth." = "stimulus_spending",
  "government subsidized loans for low-income college students." = "student_loans",
  "government programs to reduce income inequality." = "inequality_programs",
  "regulations to protect the environment." = "environmental_regulations",
  "increasing federal minimum wage to $15." = "minimum_wage_15")
stopifnot(length(issues) == 27, !anyDuplicated(issues))
labs <- c("Conservative", "Environmentalist", "Liberal", "Libertarian", "Nationalist", "Progressive", "Socialist", "Traditional")
rows <- list()
for (t in 1:7) {
  ans <- s[[paste0("X", t, "_choice_gen_ideo")]]
  ans <- fifelse(!is.na(ans), ans, fifelse(!is.na(s[[paste0("X", t, "_choice_dem_ideo")]]), s[[paste0("X", t, "_choice_dem_ideo")]],
                                           s[[paste0("X", t, "_choice_rep_ideo")]]))
  # at most one arm answered per task
  stopifnot(rowSums(!is.na(s[, paste0("X", t, "_choice_", c("gen", "dem", "rep"), "_ideo"), with = FALSE])) <= 1)
  pre <- fifelse(s$election == "general", "choice", fifelse(s$embed_pid == "Democrat", "Dprim", "Rprim"))
  for (p in 1:2) {
    d <- data.table(rid = s$rid, task = t, profile = p, trial_preference = as.integer(ans), pre = pre)
    for (k in 1:5) d[, paste0("slot", k) := M[cbind(seq_len(.N), match(paste0(pre, t, "_attr_", k, "_", p), colnames(M)))]]
    d[, ideo := M[cbind(seq_len(.N), match(paste0(pre, t, "_ideo_", p), colnames(M)))]]
    rows[[length(rows) + 1]] <- d[!is.na(trial_preference)]
  }
}
d <- rbindlist(rows)
stopifnot(all(d$trial_preference %in% c(1, 2, 4, 5)), all(d$pre %in% c("choice", "Dprim", "Rprim")))
d[, choice := as.integer((profile == 1 & trial_preference %in% 1:2) | (profile == 2 & trial_preference %in% 4:5))]
stopifnot(all(d$ideo %in% c("", labs)))
d[, attr_ideology := fifelse(ideo == "", "(not shown)", ideo)]
for (v in issues) { d[, paste0("attr_", v) := "(not shown)"]; d[, paste0("attrpos_", v) := NA_integer_] }
for (k in 1:5) {
  x <- d[[paste0("slot", k)]]
  stopifnot(grepl("^(SUPPORT|OPPOSE|INCREASE|DECREASE|RAISE|REDUCE|MORE|FEWER) ", x))
  stem <- sub("^[A-Z]+ ", "", x); v <- issues[stem]; stopifnot(!is.na(v))
  for (u in unique(v)) {
    i <- which(v == u)
    stopifnot(d[[paste0("attr_", u)]][i] == "(not shown)")  # no issue twice in a profile
    set(d, i, paste0("attr_", u), x[i]); set(d, i, paste0("attrpos_", u), k)
  }
}
d[, trial_election := s$election[rid]][, trial_embed_pid := s$embed_pid[rid]]
stopifnot(all(d$trial_election %in% c("general", "primary")), all(d$trial_embed_pid %in% c("Democrat", "Republican")))
stopifnot(d[, .N, .(rid, task)][, all(N == 2)], d[, sum(choice), .(rid, task)][, all(V1 == 1)])
# covariates
cv <- s[, .(rid, cov_gender = c("male", "female", "other")[gender], cov_age = as.integer(screen_age),
            cov_birth_year = fifelse(age >= 1900 & age <= 2005, as.integer(age), NA_integer_),
            cov_attention_pass_1 = as.integer(check1 == 1),
            cov_attention_pass_2 = as.integer(!is.na(check2_3) & check2_3 == 1 & !is.na(check2_4) & check2_4 == 1 &
                                                is.na(check2_1) & is.na(check2_2) & is.na(check2_5)),
            cov_duration_sec = duration, cov_progress = Progress, cov_selfplace = selfplace)]
for (v in c(grep("^id_", names(s), value = TRUE), "mostimp", paste0("strength_", 1:4), "news", "polatt",
            paste0("race_", 1:8), "employ", "income")) cv[, paste0("cov_", v) := s[[v]]]
cv[, cov_party_id7_code := s$pid][, cov_education_code := s$education][, cov_state_code := s$state]
d <- merge(d, cv, by = "rid")
d[, id := rid]
d[, c("rid", "pre", "ideo", paste0("slot", 1:5)) := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "attr_ideology", paste0("attr_", issues), paste0("attrpos_", issues)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "trexler_2025_ideology_labels.csv"))
