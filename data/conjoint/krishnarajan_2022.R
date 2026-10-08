##Election-pledge statement conjoints (United States, Britain, Denmark) from
##Krishnarajan, S., & Jensen, C. (2022). When is a pledge a pledge? British Journal of Political
##Science, 52(4), 1911-1922. https://doi.org/10.1017/S0007123421000284
##Replication data: Harvard Dataverse doi:10.7910/DVN/X73XUM, CC0 1.0. Files read (Stata originals,
##?format=original): data_us.dta, data_uk.dta, data_dk.dta (one row per respondent x statement;
##data_all.dta is the three stacked and is not read). Design and question wording: the article's
##online appendix (S0007123421000284sup001.docx, Appendix C: questionnaires C2a-c and "Complete
##Conjoint Design"); "Election promises replication dofile.do" read as text.
##Usage: Rscript krishnarajan_2022.R <dir holding data_us/uk/dk.dta> <output dir>
##
##YouGov online panels: US 18-25 Feb 2019, Britain and Denmark 12-19 Dec 2018. Each respondent read 4
##political statements (single profile, text vignette), e.g. "In connection with the latest midterm
##election, the Republicans made the following statement: 'We promise 25% more cancer screenings
##within the next year if the economy allows it.'" Seven randomized components: timing (when the
##statement was made), sender (2 parties + 2 leaders in the US; 4 parties + 2 leaders in Britain and
##Denmark), commitment formulation, numeric goal, policy content (8 subjects: output/outcome pairs on
##health, immigration, labour, Olympics), time horizon, conditionality. One table per country: the
##authors estimate each country separately (dofile Figure 1, appendix D1), the sender levels differ
##and the Danish survey was in Danish.
##task = round (statement 1-4 in order shown, `round`), profile = 1 (single statement).
##Attribute text: the per-round design columns q_timing_k, q_sender_k, q_promise_k, q_subject_k,
##q_time_k, q_conditionality_k (value labels; these are the displayed fragments, in Danish for the
##Danish survey; each equals the long-format design column of its round, checked below). The
##statement had no numeric goal / no time horizon / no condition in the level coded 1 (label "1"):
##stored as "(not shown)", the clause being left out of the sentence by design. Numeric goal is
##"10%"/"25%"/"50%" from the `spec` labels (the appendix vignette examples print "25%", also in the
##Danish example; the appendix design table says 20% but the data have 25%). Danish condition
##fragments lose their leading ", " and the Danish timing fragments keep the verb "udtalte" as
##labelled.
##Outcomes (each asked about the statement; wording from appendix C2, [sender] = the sender):
##  rating: "Would you consider this an election pledge?" Yes = 1 / No = 0 (authors' elec_prom).
##  rating_accountable: "Should [sender] be held accountable for whether this is implemented?"
##    Yes = 1 / No = 0 (authors' pol_acc).
##  rating_priority: "How much do you agree with the following statement? This is a high priority
##    for [sender]." 1 Disagree completely - 5 Agree completely (send_prior).
##  rating_can_act: "Is this something [sender] can do something about if [sender] really wants
##    to?" 1 Definitely not - 5 Definitely (pol_real).
##  rating_cannot_check: "How much do you agree with the following statement? In reality, it is
##    impossible for people like me to check whether [sender] actually implements this." 1 Disagree
##    completely - 5 Agree completely (nocontr).
##  "Don't know" (977) on any outcome is NA (no value on the scale; the authors' long variables do
##  the same); rows with all five outcomes NA are dropped.
##Not a choice: nothing is picked among profiles.
##Covariates: cov_gender (`gender` labels 0 Female / 1 Male), cov_age (US `age`, years),
##cov_age_group (`profile_age` band labels; the only age in Britain and Denmark), cov_education
##(Britain profile_education_level, Denmark profile_education: answer text; "Prefer not to say" /
##"Ønsker ikke at oplyse" -> NA; the US file has only the authors' Low/High split, not kept),
##cov_attention_pass (`att`: 1 = picked "Agriculture" as the topic not read about in q10),
##cov_duration_sec (tot_time, total interview time in seconds), cov_survey_weight (YouGov `weight`),
##and per country as answer text: US cov_party_registration (pp18_partyreg; registration, not
##identification), cov_vote_2016 (presvote16post), cov_left_right (political_viewpoint),
##cov_division; Britain cov_vote_2017 (pastvote_2017), cov_vote_intention (ge_voting_intention),
##cov_left_right (politics_scale_profile_update), cov_region (profile_GOR); Denmark cov_vote_intention
##(FT_next), cov_vote_2015 (FT15), cov_left_right (political_viewpoint), cov_region. "Don't know"
##stays as text; "Vil ikke svare" (won't answer) -> NA.
##Dropped: pre-treatment attitude batteries (q1-q4), page timers, the authors' dummies and derived
##variables (trust_send, vote_sender, left_right, output, subject_theme, ...). RecordNo re-keyed to
##integers.
##N: the deposit has 1,745 (US), 2,050 (Britain) and 1,800 (Denmark) respondents, all with 4
##statements; appendix C1 lists 2,032 / 2,214 / 2,031 "total number of respondents". The deposit
##does not say what removed the difference (attention-check failers are still in the file).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x, v = x) { l <- attr(v, "labels"); unname(setNames(names(l), l)[as.character(as.numeric(x))]) }
dk01 <- function(x) { x <- as.numeric(x); fifelse(x == 977, NA_real_, x) }
yes1 <- function(x) { x <- as.numeric(x); fcase(x == 1, 1L, x == 2, 0L, default = NA_integer_) }
build <- function(cc, n_resp, enc = NULL) {
  d <- read_dta(file.path(raw, sprintf("data_%s.dta", cc)), encoding = enc)
  stopifnot(uniqueN(d$RecordNo) == n_resp, all(table(d$RecordNo) == 4), all(d$round %in% 1:4))
  r <- as.integer(d$round)
  pick <- function(stem) sapply(seq_len(nrow(d)), function(i) as.numeric(d[[paste0(stem, r[i])]][i]))
  per <- function(stem, long) { v <- pick(stem); stopifnot(all(v == as.numeric(d[[long]]))); lab(v, d[[paste0(stem, 1)]]) }
  ns <- function(v) fifelse(v == "1", "(not shown)", v)
  q5 <- pick("q5_"); q8 <- pick("q8_")
  stopifnot(all(yes1(q5) == as.numeric(d$elec_prom), na.rm = TRUE), all(yes1(q8) == as.numeric(d$pol_acc), na.rm = TRUE))
  x <- data.table(rec = as.numeric(d$RecordNo), task = r, profile = 1L,
                  rating = yes1(q5), rating_accountable = yes1(q8),
                  rating_priority = dk01(pick("q6_")), rating_can_act = dk01(pick("q7_")), rating_cannot_check = dk01(pick("q9_")),
                  attr_timing = per("q_timing_", "timing"), attr_sender = per("q_sender_", "sender"),
                  attr_commitment = per("q_promise_", "promise"),
                  attr_numeric_goal = fifelse(as.numeric(d$spec) == 1, "(not shown)", lab(d$spec)),
                  attr_policy = per("q_subject_", "subject_nr"),
                  attr_time_horizon = ns(per("q_time_", "time")),
                  attr_condition = ns(sub("^, ", "", per("q_conditionality_", "cond"))),
                  cov_gender = c(Female = "female", Male = "male")[lab(d$gender)],
                  cov_age_group = lab(d$profile_age))
  stopifnot(all(x$cov_gender %in% c("female", "male")))
  if (cc == "us") x[, cov_age := as.integer(d$age)]
  if (cc == "uk") x[, cov_education := lab(d$profile_education_level)]
  if (cc == "dk") x[, cov_education := lab(d$profile_education)]
  if (cc != "us") x[cov_education %in% c("Prefer not to say", "Ønsker ikke at oplyse"), cov_education := NA]
  x[, `:=`(cov_attention_pass = as.integer(d$att), cov_duration_sec = as.numeric(d$tot_time), cov_survey_weight = as.numeric(d$weight))]
  extra <- switch(cc,
    us = list(cov_party_registration = "pp18_partyreg", cov_vote_2016 = "presvote16post", cov_left_right = "political_viewpoint", cov_division = "division"),
    uk = list(cov_vote_2017 = "pastvote_2017", cov_vote_intention = "ge_voting_intention", cov_left_right = "politics_scale_profile_update", cov_region = "profile_GOR"),
    dk = list(cov_vote_intention = "FT_next", cov_vote_2015 = "FT15", cov_left_right = "political_viewpoint", cov_region = "region"))
  for (nm in names(extra)) { v <- lab(d[[extra[[nm]]]]); v[v %in% c("Vil ikke svare", "Prefer not to say")] <- NA; set(x, j = nm, value = v) }
  ac <- grep("^attr_", names(x), value = TRUE)
  stopifnot(!anyNA(x[, ..ac]))
  oc <- grep("^rating", names(x), value = TRUE)
  x <- x[rowSums(!is.na(x[, ..oc])) > 0]
  x[, id := match(rec, sort(unique(rec)))][, rec := NULL]
  setcolorder(x, c("id", "task", "profile", oc)); setorder(x, id, task, profile)
  fwrite(x, file.path(out, sprintf("krishnarajan_2022_pledges_%s.csv", cc)))
}
build("us", 1745); build("uk", 2050); build("dk", 1800, enc = "latin1")
