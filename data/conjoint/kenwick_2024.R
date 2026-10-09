##Border-security policy conjoints (United States), two surveys, from
##Kenwick, M. R., & Maxey, S. (2024). Explaining public demands for border militarization.
##Journal of Conflict Resolution, 69(6), 1005-1032. https://doi.org/10.1177/00220027241268482
##Replication data: Harvard Dataverse doi:10.7910/DVN/EKVWUC, CC0 1.0, no restricted files.
##Files read: survey1.RData (objects `data`, one row per respondent, and `res`, the authors'
##long conjoint file) and survey2.RData (`data_tr`, `res_tr`; the free-text object `text` is not
##used), each loaded into its own environment. Read as text: README_kenwickmaxey_jcr.txt.rtf and
##preprocess/00_preprocess.R (how `res` was built from the Qualtrics export: bots
##(Q_RecaptchaScore <= 0.5) and attention-check failures removed before deposit; traits<k>a/b
##split on "|" into agency|strategy|budget|immig|ht|dt|terror; Policy A rows first).
##Usage: Rscript kenwick_2024.R <dir holding survey1.RData and survey2.RData> <output dir>
##
##Two separately fielded experiments with the same 7 attributes; the authors analyse them
##separately, so two tables:
##  kenwick_2024_border_militarization  survey 1, "conjoint-only" (Nov 2022), 776 respondents
##  kenwick_2024_border_treatments      survey 2 (Dec 2022), 3,240 respondents randomly given one
##                                      of four status-threat vignettes before the conjoint
##                                      (trial_arm; README "version of the conjoint experiment
##                                      with treatments")
##Each: up to 5 tasks of two border-security policies (Policy A = profile 1, Policy B = 2).
##Attribute text is the text shown, as stored in the Qualtrics embedded traits strings (the
##authors' res keeps it; their padding spaces in ht/dt/terror are trimmed; strategy is the
##original text `strategy1`, not the authors' short relabel): attr_agency (AGENCY),
##attr_strategy (STRATEGY, 7 levels, e.g. "Supporting and patrolling border walls"),
##attr_budget (BUDGET, e.g. "0 - 5% increase"), attr_immigration ("EFFECT ON ILLEGAL
##IMMIGRATION"), attr_human_trafficking ("HUMAN TRAFFICKING"), attr_drug_trafficking ("EFFECT ON
##DRUG TRAFFICKING"), attr_terrorism ("EFFECT ON TERRORISM"); attribute names are the authors'
##plot labels in 00_preprocess.R. Randomization restrictions and attribute order are not
##documented in the deposit.
##Outcome: choice = chosen, from policy_preference<k> ("Policy A" / "Policy B"); forced choice.
##The question wording is not in the deposit (paraphrase in the design record). Tasks with no
##answer (chosen NA; respondents who stopped) are omitted: survey 1 has none; survey 2 loses
##the rows the authors set NA: 3,228 of the 3,240 respondents answered at least one task
##(32,110 rows; 3,196 answered all 5). The article's Ns were not checked (paywalled).
##Covariates (answer text as stored): cov_gender (Male -> male, Female -> female, Other ->
##other), cov_education, cov_ideology (7-point text), cov_military_service (milserve; "" -> NA),
##cov_attention_politics, cov_hispanic, cov_race, cov_income, cov_age_group (age bands), and
##cov_party5: the authors' party_order mapped back to the answer text it was built from
##(00_preprocess.R: -2 pid3 "Democrat", -1 pid_lean "Lean to the Democrat Party", 0 "Lean to
##neither", 1 "Lean to the Republican Party", 2 pid3 "Republican"; NA otherwise). Survey 2 also:
##trial_arm (treatment_condition: 1 domestic status retention, 2 domestic status loss,
##3 international status retention, 4 international status loss; pre-processing comments),
##cov_manipulation_pass (manip_pass, the authors' 0/1), cov_attention_pass (attn2_pass: 1 =
##slider set between 45 and 55 as instructed, the authors' coding). Dropped: start/end
##timestamps, the authors' dummies (rep, dem, white_nonhisp, dom_ret, ...), raw slider values,
##the free-text answers. Respondent ids are the authors' row numbers (no platform ids in the
##deposit's RData).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
party <- c(`-2` = "Democrat", `-1` = "Lean to the Democrat Party", `0` = "Lean to neither",
           `1` = "Lean to the Republican Party", `2` = "Republican")
blank <- function(x) { x <- as.character(x); x[x == ""] <- NA; x }
build <- function(res, dat, survey2) {
  r <- as.data.table(as.data.frame(res)); p <- as.data.table(dat)
  r[, id := as.integer(as.character(id))]
  r <- r[!is.na(chosen)]
  r[, profile := seq_len(.N), .(id, task)]
  stopifnot(r[, .N, .(id, task)][, all(N == 2)], r[, sum(chosen), .(id, task)][, all(V1 == 1)])
  d <- r[, .(id, task = as.integer(task), profile = as.integer(profile), choice = as.integer(chosen),
             attr_agency = trimws(as.character(agency)), attr_strategy = trimws(as.character(strategy1)),
             attr_budget = trimws(as.character(budget)), attr_immigration = trimws(as.character(immig)),
             attr_human_trafficking = trimws(as.character(ht)), attr_drug_trafficking = trimws(as.character(dt)),
             attr_terrorism = trimws(as.character(terror)))]
  if (survey2) {
    if ("profile" %in% names(res)) stopifnot(all(r$profile == as.integer(res$profile[!is.na(res$chosen)])))
    arm <- c("Domestic status retention", "Domestic status loss", "International status retention", "International status loss")
    d[, trial_arm := arm[as.integer(r$treatment_condition)]]
  }
  i <- match(d$id, p$id); stopifnot(!anyNA(i))
  g <- c(Male = "male", Female = "female", Other = "other")
  d[, `:=`(cov_gender = unname(g[p$gender[i]]), cov_education = blank(p$education[i]), cov_ideology = blank(p$ideology[i]),
           cov_military_service = blank(p$milserve[i]), cov_attention_politics = blank(p$attention_politics[i]),
           cov_hispanic = blank(p$hispanic[i]), cov_race = blank(p$race[i]), cov_income = blank(p$income[i]),
           cov_age_group = blank(p$age[i]), cov_party5 = unname(party[as.character(p$party_order[i])]))]
  if (survey2) d[, `:=`(cov_manipulation_pass = as.integer(p$manip_pass[i]), cov_attention_pass = as.integer(p$attn2_pass[i]))]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(p$gender %in% names(g)))
  setorder(d, id, task, profile)
  d
}
e1 <- new.env(); load(file.path(raw, "survey1.RData"), envir = e1)
d1 <- build(e1$res, e1$data, FALSE)
stopifnot(uniqueN(d1$id) == 776L, nrow(d1) == 7760L)
fwrite(d1, file.path(out, "kenwick_2024_border_militarization.csv"))
e2 <- new.env(); load(file.path(raw, "survey2.RData"), envir = e2)
d2 <- build(e2$res_tr, e2$data_tr, TRUE)
fwrite(d2, file.path(out, "kenwick_2024_border_treatments.csv"))
cat("survey2:", uniqueN(d2$id), "respondents,", nrow(d2), "rows\n")
