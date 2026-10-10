##Democratic-candidate conjoint with a loss-narrative treatment, from
##Haines, P., & Masket, S. (2023). "You had better mention all of them": Race and gender
##effects in election loss narratives. Political Research Quarterly, 77(1), 417-431.
##https://doi.org/10.1177/10659129231217511
##Replication data: Harvard Dataverse doi:10.7910/DVN/FDFMZT, CC0 1.0, no restricted files.
##File read: StackedAllConjoint.csv (Dataverse "original format" download): one row per
##respondent x candidate, white and Black respondent samples stacked. LossNarrativesReplication.R
##(authors' code) read as text. StandardAll.csv was downloaded to check the sample size only (it
##holds free-text answers, lost16_text / lost18_text, none of which is used). The article is
##not open access and the deposit has no questionnaire, so the outcome wording is a paraphrase.
##Usage: Rscript haines_2023.R <raw dir> <output dir>
##
##1,656 Democratic respondents (abstract; cov_democrat_code is uncoded) (843 white, 813 Black; Qualtrics
##ResponseIds re-keyed to integers in file order), each choosing between two hypothetical
##candidates in 10 match-ups ("heat" = task, "candnum" 1-20 = candidate within respondent in
##order, odd = profile 1). Respondents were first randomly assigned to read (trial_narrative
##= 1) or not (0) a vignette attributing the Democrats' 2016 loss to identity politics (the
##authors' legend: "With / Without Identity Politics Loss Narrative"); the arm is constant within
##respondent.
##TWO TABLES, one per respondent sample: haines_2023_loss_narrative_white and
##haines_2023_loss_narrative_black. The authors analyse white and Black respondents separately
##throughout (separate stacked files, separate models), and the race attribute's level text
##differs between the samples ("Black", "Asian" for white respondents; "African American",
##"Asian American" for Black respondents), so the samples are not pooled.
##Attributes, as the deposit's text label columns (*.lab); whether these are the exact
##displayed strings is not documented:
##  attr_gender    Man / Woman
##  attr_race      White / Black / Asian / Hispanic (white sample); White / African American /
##                 Asian American / Hispanic (Black sample)
##  attr_ideology  Slightly Liberal / Moderately Liberal / Very Liberal
##  attr_policy    Good Jobs / Fair Jobs / Justice Reform / Fair Justice (the authors' dummies
##                 code Good Jobs and Fair Jobs as economic, Fair Jobs and Fair Justice as
##                 identity/equity policy; the dummies are dropped)
##Outcome: choice = candvote, which of the two candidates the respondent would vote for
##(paraphrase); exactly one chosen per task, no opt-out. 23 tasks with no answer (46 rows,
##candvote missing) are omitted.
##Randomization restrictions: none documented.
##Covariates as in the stacked file: cov_gender (female 1 = female, 0 = male), cov_age (years),
##cov_democrat_code (1-3, no labels in the deposit), cov_ideology_code (1-7, no labels).
##Dropped: Qualtrics ResponseId, data.id (authors' integer id), numeric attribute codes and
##derived dummies (candwhite, candasian, candhisp, candblack, candeconpolicy, candidentitypolicy).
##Table sizes: white 843 respondents, Black 812 (one Black respondent answered no task).
##N vs paper: StandardAll.csv has 1,658 respondents (845 white, 813 Black), two more white
##respondents than the stacked conjoint file; the article's N was not checked (paywalled).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "StackedAllConjoint.csv"))
s[, id := match(respondent.id, unique(respondent.id))]
stopifnot(s[, .N, id][, all(N == 20)], s[, all(candnum == (heat - 1) * 2 + (2 - candnum %% 2))],
          s[, uniqueN(treatment), id][, all(V1 == 1)], s[, uniqueN(race), id][, all(V1 == 1)])
d <- s[, .(id, task = as.integer(heat), profile = as.integer(2 - candnum %% 2), choice = as.integer(candvote),
           trial_narrative = as.integer(treatment), attr_gender = candgender.lab, attr_race = candrace.lab,
           attr_ideology = candideol.lab, attr_policy = candpolicy.lab,
           cov_gender = c("male", "female")[female + 1], cov_age = as.integer(age),
           cov_democrat_code = as.integer(democrat), cov_ideology_code = as.integer(ideology), sample = race)]
miss <- d[, .(m = anyNA(choice)), .(id, task)][m == TRUE]
stopifnot(nrow(miss) == 23, d[miss, on = .(id, task)][, all(is.na(choice))])
d <- d[!miss, on = .(id, task)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .(attr_gender, attr_race, attr_ideology, attr_policy)]))
for (g in c("white", "black")) {
  x <- d[sample == g][, sample := NULL]
  x[, id := match(id, unique(id))]
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("haines_2023_loss_narrative_", g, ".csv")))
}
