##Judicial candidate gender x campaign appeal vignette from
##Gunderson, A., Kim, J., Lane, E., Bauer, N., Davis, B., & Searles, K. (2025). Candidate gender, campaign appeals,
##and voter support in judicial elections. Journal of Politics, 87(1), 172-189. https://doi.org/10.1086/730721
##Replication data: Harvard Dataverse doi:10.7910/DVN/SYFWXB, CC0 1.0. File read: experiment_qualtricsdata.xlsx
##(Qualtrics export, 2,054 Lucid respondents; row 1 holds the question text); JOP_appendix_experiment.R and readme.rtf
##read as text. Usage: Rscript gunderson_2025.R <dir holding f8109135 = the xlsx> <output dir>
##
##Respondents were randomly assigned one of four judicial-candidate vignettes (blocks Q4-Q7): a county judge
##candidate "Mary Bailey" or "Michael Bailey" (Green County) running on a criminal-justice reform (rehabilitation) or a
##tough-on-crime platform (2 x 2, JOP_appendix_experiment.R: candidate = female/male, platform = rehab/tough).
##The same 2,054-respondent file also holds a second, separate experiment (attorney Michelle/Michael Larsen
##oral-argument transcripts, Q8-Q11, gender only) that is NOT built here (single factor). Respondents with a
##candidate-vignette answer (blocks Q4-Q7) are those kept: one vignette each, task = 1, profile = 1, id re-keyed 1..n in file order.
##The vignette text is not in the deposit; attr_candidate is the displayed name; attr_platform is "criminal justice
##reform" / "tough on crime" (the paper's labels for the appeals; wording of the platform text paraphrased from the
##article description, not verbatim). LABELS: paraphrased.
##Outcomes (raw Qualtrics codes; the xlsx has numeric codes without labels, directions inferred from the authors' own
##reversal in JOP_appendix_experiment.R lines 50-56, which recodes 1->4, 2->3, 3->2, 4->1 for vote, win chance,
##impartiality, Q12_* and Q13 "so that higher = more"): rating_vote (Q6: how likely to vote for the candidate),
##rating_win_chance (Q7), rating_impartial (Q8: trust to reach impartial decisions), rating_perf_people_like_her_him /
##rating_perf_your_interests / rating_perf_safety / rating_perf_fair_trial (Q10_1-4, 1-7 very ineffective to very effective),
##rating_crime_property / rating_crime_violent / rating_crime_recidivism (Q12_1-3, how well will the candidate address the
##issue), rating_reduce_incarceration (Q13: how likely the candidate will reduce incarceration). 1-4 items: raw 1 = the
##most positive option (e.g. "very likely"/"very well"), 4 = the least (inferred from the reversal; exact option text not
##in the file). Direction therefore: LOWER raw = more favourable for the 1-4 items.
##Covariates: cov_gender (gender: 1 male, 2 female; authors' female = gender == 2), cov_age (age, years). Education,
##household income, ethnicity, party, region are numeric codes without labels in the deposit and are not kept.
##Dropped: ResponseId, rid (panel id), attention/consent items, recall checks, derived columns.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "f8109135"), col_types = "text"))[-(1:2)]
bl <- list(c(block = "Q4", cand = "Mary Bailey", plat = "criminal justice reform"),
           c(block = "Q5", cand = "Michael Bailey", plat = "criminal justice reform"),
           c(block = "Q6", cand = "Michael Bailey", plat = "tough on crime"),
           c(block = "Q7", cand = "Mary Bailey", plat = "tough on crime"))
sfx <- c(rating_vote = ".6", rating_win_chance = ".7", rating_impartial = ".8", rating_perf_people_like_candidate = ".10_1",
         rating_perf_your_interests = ".10_2", rating_perf_safety = ".10_3", rating_perf_fair_trial = ".10_4",
         rating_crime_property = ".12_1", rating_crime_violent = ".12_2", rating_crime_recidivism = ".12_3",
         rating_reduce_incarceration = ".13")
x[, id := .I]
L <- rbindlist(lapply(bl, function(b) {
  s <- x[!is.na(get(paste0(b["block"], ".6")))]
  d <- data.table(id = s$id, task = 1L, profile = 1L)
  for (n in names(sfx)) d[[n]] <- as.integer(s[[paste0(b["block"], sfx[[n]])]])
  d[, `:=`(attr_candidate = b["cand"], attr_platform = b["plat"])]
  d[, `:=`(cov_gender = c("male", "female")[as.integer(s$gender)], cov_age = as.integer(s$age))]
  d
}))
stopifnot(!anyDuplicated(L$id)); L[, id := frank(id, ties.method = "dense")] # re-key to 1..n
setcolorder(L, c("id", "task", "profile", names(sfx), "attr_candidate", "attr_platform"))
setorder(L, id, task, profile)
fwrite(L, file.path(out, "gunderson_2025_judicial_appeals.csv"))
