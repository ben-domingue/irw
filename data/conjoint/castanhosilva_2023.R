##Populist-candidate conjoint (United States) from
##Castanho Silva, B., Neuner, F. G., & Wratil, C. (2023). Populism and candidate support in the
##US: The effects of "thin" and "host" ideology. Journal of Experimental Political Science, 10(3),
##438-447. https://doi.org/10.1017/XPS.2022.9 (online 2022)
##Replication data: Harvard Dataverse doi:10.7910/DVN/5AEGPM, CC0 1.0, no restricted files.
##File read: castanho_silva_et_al_replication_dataset.csv (tab-separated, one row per candidate,
##15,050 rows). README.pdf and the .Rmd analysis script were read as text.
##Usage: Rscript castanhosilva_2023.R <dir holding the .csv> <output dir>
##
##US adults (Lucid, quotas on gender, age, ethnicity, region; 30 July - 4 August 2019); half of
##the 3,024 were randomly assigned to this conjoint: 1,505 respondents (the article's N), 5 tasks
##of 2 fictitious candidates, no party labels. A replication of Neuner & Wratil's German design.
##task/profile from `candidate_number` (README: 1 = left candidate in round 1, 2 = right in round
##1, 3 = left in round 2, ...): task = ceiling(n / 2), profile = 2 - n %% 2.
##Attributes:
##  Priorities: each candidate was described with a first and a second political priority drawn
##    from 12 (article p. 441). The deposit stores only 12 indicators ("Priority<k>" /
##    "No priority<k>"), so WHICH was first and which second is lost. Each priority is one
##    attr_priority_* column holding its displayed text (from the .Rmd relabelling and README,
##    e.g. "Fight political corruption") when it was one of the candidate's two priorities and
##    "(not shown)" otherwise. Every profile has exactly two priorities shown (checked).
##  Positions (displayed text as stored): attr_immigration, attr_military, attr_redistribution
##    (taxes on the rich), attr_globalization, 4 levels each ("Is for much higher taxes on the
##    rich" ...).
##Attribute order and randomization restrictions beyond "two different priorities" are not
##documented in the deposit (Online Appendix not read).
##Outcome: choice = `votefor`: "which of the two candidates they would rather vote for" (article
##paraphrase), forced; one candidate chosen per task. 132 tasks with no answer are omitted, which
##removes 20 respondents entirely: 1,485 respondents in the table (article: 1,505 assigned).
##Covariates (README coding): cov_female, cov_thin_pop1-8 (populist attitude items, 1-5
##disagree-agree), cov_party_id (Republican / Independent / Democrat, leaners included),
##cov_host1_immigrants, cov_host2_tariffs, cov_host3_intervention, cov_host4_rich (1-7
##disagree-agree), cov_income (hhi, 1-26, 27 = prefer not to answer), cov_age, cov_white,
##cov_black, cov_hispanic (0/1), cov_education (1-12), cov_attention_check (att1; 3 = passed;
##the article keeps failures, 13%).
##Dropped: Qualtrics ResponseId (re-keyed 1..n in file order).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "castanho_silva_et_al_replication_dataset.csv"), encoding = "UTF-8")
pr <- c(B1_corruption = "Fight political corruption", B2_parties = "End the abuse of power by the parties",
        B3_elite = "Overthrow the political elite", B4_democracy = "Strengthen direct democracy",
        B5_citizens = "Defend citizens' interests", B6_environment = "Improve environmental protection",
        B7_growth = "Promote economic growth", B8_justice = "Strengthen social justice",
        B9_islamization = "Prevent Islamization", C1_crime = "Fight crime",
        C2_liberties = "Strengthen civil rights and civil liberties", C3_globalization = "Make globalization more fair")
d <- data.table(id = frank(s$id, ties.method = "dense"), task = (s$candidate_number + 1L) %/% 2L,
                profile = 2L - s$candidate_number %% 2L, choice = as.integer(s$votefor))
for (k in seq_along(pr)) {
  v <- s[[names(pr)[k]]]
  stopifnot(all(v %in% paste0(c("Priority", "No priority"), k)))
  d[, paste0("attr_priority_", sub("^[BC][0-9]_", "", names(pr)[k])) := ifelse(v == paste0("Priority", k), pr[[k]], "(not shown)")]
}
d[, attr_immigration := s$A1_immigration][, attr_military := s$A2_military]
d[, attr_redistribution := s$A3_redistribution][, attr_globalization := s$A4_globalization]
cv <- c(cov_female = "female", setNames(paste0("thin_pop", 1:8), paste0("cov_thin_pop", 1:8)), cov_party_id = "party_id",
        cov_host1_immigrants = "thick_pop1_immigrants", cov_host2_tariffs = "thick_pop2_tariffs",
        cov_host3_intervention = "thick_pop3_intervention", cov_host4_rich = "thick_pop4_rich", cov_income = "hhi",
        cov_age = "age", cov_white = "White", cov_black = "Black", cov_hispanic = "Hispanic", cov_education = "Education",
        cov_attention_check = "att1")
for (v in names(cv)) d[, (v) := s[[cv[[v]]]]]
stopifnot(d[, rowSums(.SD != "(not shown)") == 2, .SDcols = patterns("^attr_priority_")],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, .N, .(id, task)][, all(N == 2)])
d <- d[!is.na(choice)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "castanhosilva_2023_populism_us.csv"))
