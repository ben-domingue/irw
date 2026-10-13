##Federal spending projects (US): project type x amount x administrator x time to completion, from the second survey of
##McLaughlin, P. T. (2025). Priority projects: Constituent spending demand and the benefits of congressional credit claiming.
##Legislative Studies Quarterly, 50(4). https://doi.org/10.1111/lsq.70008 (journal metadata from Crossref)
##Replication data: Harvard Dataverse doi:10.7910/DVN/AZWKVX, CC0 1.0. File read: Exp.2.data.tab (datafile 11037096; Dataverse ingest
##of the original csv, 2,126 respondents x 243 columns; only the columns named below were read), and Exp2.analysis.R,
##Exp1.analysis.R, Exp2.appendix.R as text.
##Usage: Rscript mclaughlin_2025.R <dir with the file; optional 3rd arg = file name, default Exp.2.data.csv> <output dir>
##
##WHAT THIS IS. Exp.2.data holds the paper's second experiment (a 2 x 2 vignette: project priority Top/Six x senator influence
##High/Low, in FL_338_DO) AND, for 1,561 respondents (flow block FL_384_DO = PP_Conjoint_2_a / _b), a paired conjoint of federal
##spending projects: 10 tasks x 2 projects (choiceK_project/amount/admin/time 1 and 2, K = 1..10), outcomes `K_pref_a|b` ("Project 1"
##/ "Project 2") and `K_rate_a|b_1|2` (a 1-7 rating of each project). NEITHER the paper's R code nor the appendix code uses this
##block (grep for pref_/rate_/choice: no hits), so the wording and the a/b difference are undocumented. ONLY the conjoint is built.
##NOT built (held): the 2 x 2 vignette (priority x influence): the displayed text is not deposited, "Top/Six" are the respondent's own
##ranked-priority position and "Amount.High/Low" is relabelled "influence" by the authors; and Exp.1.data (4,602 respondents,
##project-type arms) is a different experiment; both are one-factor-per-arm or text-not-deposited designs.
##Attributes (level text as shipped): project (10 types, e.g. "Hospital upgrades"), amount ($500,000 ... $10,000,000, 7 levels),
##administrator (Your state government, Your county government, A charitable organization), time (1 Year ... 5 Years). The two
##projects of a task may share a level and even the same project type (203 of 1,561 first tasks have the same project type on both
##sides): no exclusion rule is documented.
##Outcomes: choice = the project picked in the pair (pref, "Project 1" -> profile 1; no neutral option appears among the observed
##answers, so no opt-out; tasks with no answer are dropped); rating = 1-7 rating of each project (wording and anchors not in the
##deposit: paraphrase; higher assumed more favourable). Respondents received version a or b (trial_version): the deposit does not say
##how the two differ; the columns are otherwise identical.
##Task = K in the column names and profile = suffix 1/2 (recorded). Whether K is the display order is not documented.
##Exclusions: respondents whose debrief answer is "No, withdraw my responses from the study" (39) are dropped (the authors drop them too);
##of two rows sharing one panel id the second is dropped. The authors' other filters (consent, instructed attention check "Moderately
##interested", finished, non-empty rid) are NOT applied: every respondent with conjoint answers is kept and cov_attention_pass records the
##attention check (1 = answered "Moderately interested", the instructed answer in the authors' filter; 0 = other).
##Covariates: cov_gender (woman: Female -> female, Male -> male, Nonbinary/Two spirit and Other -> other, Prefer not to say -> NA),
##cov_age_group (age_tier text), cov_party_id7 (party text, 7 points incl. Independent), cov_ideology_text (ideology text),
##cov_attention_pass. The panel's numeric demographic codes (education, hhi, ethnicity, region) have no labels in the deposit: dropped.
##Dropped: rid (panel id), zip, all vignette/feeling-thermometer/allocation items, Qualtrics flow columns.
##PII FOUND: rid (36-character panel respondent id) and zip in Exp.2.data: dropped.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- if (length(a) >= 3) a[3] else "Exp.2.data.csv"
d <- fread(file.path(raw, f), encoding = "UTF-8")
stopifnot(nrow(d) == 2126)
d <- d[FL_384_DO != ""]
stopifnot(nrow(d) == 1561)
d <- d[debrief != "No, withdraw my responses from the study"]
d <- d[!duplicated(rid) | rid == ""]
d[, id := .I]
build <- function(k, p) {
  pre <- function(s) paste0("choice", k, "_", s, p)
  x <- data.table(id = d$id, task = k, profile = p,
    attr_project = d[[pre("project")]], attr_amount = trimws(d[[pre("amount")]]), attr_administrator = d[[pre("admin")]],
    attr_time = d[[pre("time")]])
  pa <- d[[paste0(k, "_pref_a")]]; pb <- d[[paste0(k, "_pref_b")]]
  pref <- ifelse(pa != "", pa, pb)
  x[, choice := fifelse(pref == "", NA_integer_, as.integer(pref == paste("Project", p)))]
  ra <- d[[paste0(k, "_rate_a_", p)]]; rb <- d[[paste0(k, "_rate_b_", p)]]
  x[, rating := as.integer(ifelse(is.na(ra), rb, ra))]
  x[, trial_version := ifelse(d$FL_384_DO == "PP_Conjoint_2_a", "a", "b")]
  x
}
t <- rbindlist(lapply(1:10, function(k) rbind(build(k, 1), build(k, 2))))
stopifnot(all(t$attr_project != ""), all(t$attr_amount != ""))
t <- t[!is.na(choice)]
ok <- t[, .(n = .N, s = sum(choice)), .(id, task)]
stopifnot(all(ok$n == 2), all(ok$s == 1))
cv <- d[, .(id, cov_gender = c(Female = "female", Male = "male", `Nonbinary/Two spirit` = "other", Other = "other")[woman],
            cov_age_group = ifelse(age_tier == "", NA, age_tier), cov_party_id7 = ifelse(party == "", NA, party),
            cov_ideology_text = ifelse(ideology == "", NA, ideology),
            cov_attention_pass = as.integer(attention == "Moderately interested"))]
t <- merge(t, cv, by = "id")
setcolorder(t, c("id", "task", "profile", "choice", "rating"))
setorder(t, id, task, profile)
fwrite(t, file.path(out, "mclaughlin_2025_spending_projects.csv"))
