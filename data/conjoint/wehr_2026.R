##Swiss housing-densification conjoint from
##Wehr, M., Wicki, M. L., Wittwer, S., & Kaufmann, D. (2026). Beyond NIMBY-ism: Rethinking
##acceptance of housing densification in a direct democratic renters society. Journal of Public
##Policy, 46(1), 21-49. https://doi.org/10.1017/S0143814X25100883
##Replication data: Harvard Dataverse doi:10.7910/DVN/I40Q2E, CC0 1.0, no restricted files, no
##terms. Files read (inside acceptance_density_swiss.zip): data/derived/240905_data_con.RData
##(d_con: wide conjoint data) and data/derived/240905_data_robustness.RData (d3: respondent
##covariates, joined by id). Level text: the deposit's *_en columns, which match word for word the
##English screen in the article's Figure 1 ("A single conjoint table ... as displayed online");
##the article's Table 1 gives the long meaning of each level (below).
##Usage: Rscript wehr_2026.R <dir holding the two .RData files> <output dir>
##
##3,500 respondents in the file (article: 3,497 completed) from a stratified sample of the Swiss
##residents registry (FSO) in 162 urban municipalities, online, January-March 2023, in German,
##French, Italian or English (cov_survey_language = Qualtrics UserLanguage DE/FR/IT/EN; the
##English labels are stored for everyone). Four tasks of two proposals (Proposal 1 = profile 1,
##left; Proposal 2 = profile 2), 7 attributes, levels "fully randomized" (article); attribute row
##order as in Figure 1 (no statement on whether it was randomized).
##  attr_usage    residential / residential and small commercial / residential, small and larger
##                commercial / residential, small and larger commercial, leisure
##  attr_actors   public actor / non-profit developer / institutional investor / private individual
##  attr_densification  0 % / 33 % / 66 % / 100 %  (Table 1: increase in residents; 100 % =
##                doubling)
##  attr_cost_rent      0 % / 33 % / 66 % / 100 %  (Table 1: share of housing units at cost rent)
##  attr_green_space    no additional green space / additional green space, accessible to
##                residents / additional green space, publicly accessible / additional
##                biodiverse green space, access limited
##  attr_climate  neither / climate protection measures / climate adaptation measures / climate
##                protection and climate adaptation measures
##  attr_decision elected government / experts committee / electorate/ballot / project developer
##                / residents council
##Outcomes:
##  choice = con_t.3 "Which of the two proposals would you prefer? Please consider the following
##           two proposals." (Figure 1), Proposal 1 / Proposal 2, forced (no opt-out).
##  rating_accept = con_t.4 (Proposal 1) / con_t.5 (Proposal 2): whether the respondent accepts
##           the proposal (article: respondents indicated "whether they accepted or rejected the
##           project"; exact wording not given), Yes = 1, No = 0 (source text recoded to 0/1).
##No missing choices; con_t.6 (a free-text field) is dropped.
##Covariates (from d3): cov_gender (authors' code: 1 Male -> male, 2 Female -> female, 3 Non
##binary -> other; 01_data_management.R), cov_age (the authors' 2022 minus year of birth),
##cov_education (edu, answer text in English; "Do not know" kept), cov_left_right (0 left .. 10
##right; prefer not / don't know NA), cov_tenure (liv_1.1 answer text: tenant, owner, ...),
##cov_survey_language, cov_duration_sec (Qualtrics Duration in seconds, whole survey).
##Dropped: postal code and municipality number (postalCode, gnr: location PII), free text,
##the authors' derived variables (owner dummy, bougy, rel_hcost, ...). No survey weight in the
##deposit or article; no attention check; no repeated task.
##N: 3,500 vs the article's 3,497 completed (28,000 rows vs its 27,976 observations; the deposit
##keeps 3 more). Spot check: AMCE (lm, clustered by id) of 33 % vs 0 % cost rent on choice is
##positive, as in the article's Figure 2.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "240905_data_con.RData"), envir = e); w <- as.data.table(e$d_con)
e2 <- new.env(); load(file.path(raw, "240905_data_robustness.RData"), envir = e2); cv <- as.data.table(e2$d3)
stopifnot(uniqueN(w$id) == nrow(w), setequal(w$id, cv$id))
cv <- cv[match(w$id, cv$id)]
nm <- c(use = "usage", act = "actors", den = "densification", cost = "cost_rent", green = "green_space", cli = "climate", dec = "decision")
rows <- list()
for (t in 1:4) for (p in 1:2) {
  s <- paste0("P", t, c("L", "R")[p])
  ch <- w[[paste0("con_", t, ".3")]]; ac <- w[[paste0("con_", t, ".", 3 + p)]]
  stopifnot(all(ch %in% c("Proposal 1", "Proposal 2")), all(ac %in% c("Yes", "No")))
  x <- data.table(id = as.integer(w$id), task = t, profile = p, choice = as.integer(ch == paste("Proposal", p)),
                  rating_accept = as.integer(ac == "Yes"))
  for (v in names(nm)) { col <- if (v %in% c("den", "cost")) paste0(v, s) else paste0(v, s, "_en"); x[, paste0("attr_", nm[[v]]) := w[[col]]] }
  rows[[length(rows) + 1]] <- x
}
d <- rbindlist(rows)
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
cvd <- data.table(id = as.integer(w$id), cov_gender = c("male", "female", "other")[cv$gender], cov_age = as.integer(cv$age),
                  cov_education = as.character(cv$edu), cov_left_right = as.integer(cv$left_right), cov_tenure = as.character(cv$liv_1.1),
                  cov_survey_language = as.character(cv$lan), cov_duration_sec = as.numeric(cv$duration))
stopifnot(all(cv$gender %in% c(1:3, NA)))
cvd[cov_education %in% c("Prefer not to answer", ""), cov_education := NA]
cvd[cov_tenure %in% c("Prefer not to answer", ""), cov_tenure := NA]
cvd[!(cov_age >= 16 & cov_age <= 110), cov_age := NA]
d <- merge(d, cvd, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wehr_2026_housing_densification.csv"))
