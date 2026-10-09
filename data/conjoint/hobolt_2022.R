##Brexit-negotiation-outcome conjoint (Great Britain, April 2017) from
##Hobolt, S. B., Tilley, J., & Leeper, T. J. (2022). Policy preferences and policy legitimacy
##after referendums: Evidence from the Brexit negotiations. Political Behavior, 44(2), 839-858.
##https://doi.org/10.1007/s11109-020-09639-w
##Replication data: Harvard Dataverse doi:10.7910/DVN/EFXNLX, CC0 1.0, no restricted files.
##File read: LSEResults_Brexit_170428_client.sav (Dataverse "original format" download; SPSS
##value labels give the level text). Read as text: questionnaire.docx (survey script: level
##lists, randomization code, screen and question wording), analysis-conjoint-cleaning.R,
##analysis.Rmd (design description), data_dictionary.xlsx.
##Usage: Rscript hobolt_2022.R <raw dir> <output dir>
##
##3,293 YouGov panel respondents (analysis.Rmd: "demographic data being drawn from YouGov's
##profile variables"; respdate 2017-04-26/27), all complete. Each saw 5 pairs (PAIR1-5 -> task)
##of possible Brexit negotiation outcomes, "Outcome A" (= profile 1, *_seen1_*) and "Outcome B"
##(= profile 2), 8 attributes as labelled table rows: immigration ("Policy on immigration from
##the EU"), rights ("Future rights of current EU nationals in Britain and British nationals in
##the EU"), trade ("Trade agreement with the EU"), laws ("EU's legal authority in Britain"),
##budget ("Britain's future payments to the EU budget to access science and regional development
##programmes"), payment ("Britain's one-off payment to the EU to settle outstanding
##commitments"), border ("Border checks between Northern Ireland and the Republic of Ireland"),
##timeline ("When this will come into effect"). Levels drawn uniformly and independently per
##profile and pair (random_shuffle of each list; analysis.Rmd: "No constraints were placed on
##combinations of features"). Row order: list_table shuffled ONCE per respondent and reused for
##all 5 pairs (the Rmd says order was randomized "in each table", but the script never
##re-shuffles it and the data hold one order per respondent: row1_1..row8_1) -> attrpos_.
##A sixth, FIXED pair (one of three preset pairs, QC*) followed; it is not randomized, the
##authors do not analyse it, and it is dropped.
##Outcomes (asked after every pair):
##  choice: "Which of these two outcomes do you prefer?" Outcome A / Outcome B; forced (QB1).
##  rating_acceptable: "How acceptable or unacceptable are each of the outcomes to you
##    personally?" 1 = Completely acceptable, 2 Somewhat acceptable, 3 Somewhat unacceptable,
##    4 = Completely unacceptable (QB2gridA/B), stored RAW: lower = more acceptable. (The
##    authors rescale it to 1, .67, .33, 0.)
##  rating_respects_referendum: "Which outcome(s) do you think would respect the result of the
##    referendum?" (QB4: A would / B would / Both would / Neither would / Don't know), coded per
##    profile: 1 if the answer covers this outcome (A or Both for A; B or Both for B), 0 if it
##    does not; Don't know -> NA on both profiles (the authors' cleaning codes Don't know as 0).
##  rating_likely: "How likely do you think it is that the outcome that you have chosen actually
##    happens?" (QB5) 1 = Very likely .. 4 = Not at all likely, asked about the CHOSEN outcome
##    only, so stored on the chosen profile, NA on the other; Don't know (5) -> NA.
##Level text = SPSS value labels (= questionnaire lists), trailing spaces trimmed.
##Covariates (SPSS value labels; Skipped/Not Asked -> NA): cov_age (years), cov_gender,
##cov_region (region_GOR), cov_vote_euref (pastvote_EURef), cov_vote_2015 (pastvote_2015),
##cov_education (education_level, highest qualification; "Prefer not to say" -> NA),
##cov_social_grade (social_grade_CIE), cov_class_identity (QA1), cov_survey_weight (W8).
##Dropped: open "other" texts (QA1other, QA2*other), timing, media and work items, the
##national-identity items QA2A-C, the fixed sixth pair.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_sav(file.path(raw, "LSEResults_Brexit_170428_client.sav"))
stopifnot(nrow(x) == 3293L, all(x$disposition == 1))
lab <- function(v) { r <- trimws(as.character(as_factor(v, levels = "labels")))
  r[r %in% c("Skipped", "Not Asked", "Refused", "Prefer not to say")] <- NA; r }
num <- function(v) as.integer(zap_labels(v))
attrs <- c(immigration = "imigration", rights = "rights", trade = "trade", laws = "laws",
           budget = "budget", payment = "payment", border = "border", timeline = "timeline")
L <- list()
for (t in 1:5) for (p in 1:2) {
  d <- data.table(id = num(x$ID), task = t, profile = p)
  q1 <- num(x[[sprintf("QB1_PAIR%d", t)]]); stopifnot(all(q1 %in% 1:2))
  d[, choice := as.integer(q1 == p)]
  d[, rating_acceptable := num(x[[sprintf("QB2grid%s_PAIR%d", c("A", "B")[p], t)]])]
  q4 <- num(x[[sprintf("QB4_PAIR%d", t)]]); stopifnot(all(q4 %in% 1:5))
  d[, rating_respects_referendum := fifelse(q4 == 5L, NA_integer_, as.integer(q4 == p | q4 == 3L))]
  q5 <- num(x[[sprintf("QB5_PAIR%d", t)]]); stopifnot(all(q5 %in% 1:5))
  d[, rating_likely := fifelse(q1 == p & q5 %in% 1:4, q5, NA_integer_)]
  for (v in names(attrs)) d[, paste0("attr_", v) := lab(x[[sprintf("%s_seen%d_t%d", attrs[[v]], p, t)]])]
  L[[length(L) + 1]] <- d
}
d <- rbindlist(L)
stopifnot(!anyNA(d[, c("choice", "rating_acceptable", paste0("attr_", names(attrs))), with = FALSE]),
          all(d$rating_acceptable %in% 1:4), d[, sum(choice), .(id, task)][, all(V1 == 1)])
rowlab <- c("Policy on immigration from the EU" = "immigration",
  "Future rights of current EU nationals in Britain and British nationals in the EU" = "rights",
  "Trade agreement with the EU" = "trade", "EU’s legal authority in Britain" = "laws",
  "Britain’s future payments to the EU budget to access science and regional development programmes" = "budget",
  "Britain’s one-off payment to the EU to settle outstanding commitments" = "payment",
  "Border checks between Northern Ireland and the Republic of Ireland" = "border",
  "When this will come into effect" = "timeline")
pos <- data.table(id = num(x$ID))
for (k in 1:8) {
  r <- rowlab[trimws(x[[sprintf("row%d_1", k)]])]
  stopifnot(!anyNA(r))
  for (v in names(attrs)) pos[r == v, paste0("attrpos_", v) := k]
}
stopifnot(!anyNA(pos), ncol(pos) == 9L)
cv <- data.table(id = num(x$ID), cov_age = num(x$age),
  cov_gender = c("male", "female")[match(num(x$gender), 1:2)], cov_region = lab(x$region_GOR),
  cov_vote_euref = lab(x$pastvote_EURef), cov_vote_2015 = lab(x$pastvote_2015),
  cov_education = lab(x$education_level), cov_social_grade = lab(x$social_grade_CIE),
  cov_class_identity = lab(x$QA1), cov_survey_weight = as.numeric(x$W8))
cv[!(cov_age %between% c(16L, 110L)), cov_age := NA]
d <- merge(merge(d, pos, by = "id"), cv, by = "id")
d[, id := match(id, sort(unique(id)))]
setcolorder(d, c("id", "task", "profile", "choice", "rating_acceptable", "rating_respects_referendum", "rating_likely"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hobolt_2022_brexit_negotiations.csv"))
