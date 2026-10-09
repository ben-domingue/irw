##Candidate choice conjoint with a terrorist-threat treatment (Denmark) from
##Littmann, B., Nielsen, N. N. J., & Laustsen, L. (2026). Terrorist threat decreases citizens' relative
##preferences for women candidates: Insights from a Danish conjoint experiment. European Journal of
##Political Research. https://doi.org/10.1017/S1475676526101649
##Replication data: Harvard Dataverse doi:10.7910/DVN/F7WN3A, CC0 1.0. File read:
##conjoint_data_anonymized.rds (wide; one row per respondent). 01._Main_graphs_and_analysis.R read as
##text, not run. Design facts from the article (Cambridge Core HTML, read 2026-10-08).
##Spot check: AMCE of a male candidate (vs female), OLS clustered by id: -0.084 (SE 0.012) in
##control, -0.050 (0.012) under threat, the direction the article reports.
##Usage: Rscript littmann_2026.R <dir holding the .rds> <output dir>
##
##1,034 Danish respondents (Epinion omnibus, 25 Oct - 8 Nov 2024; = the article), 8 tasks x 2
##candidates ("Kandidat 1", "Kandidat 2"), 5 attributes, all shown; Danish text as displayed
##(Qualtrics conjoint_<task>_Concept_<profile>_attribute_<k>). The article says partisanship was held
##constant (both candidates from the respondent's preferred party); that is not an attribute here.
##choice: "Which of the two candidates would you prefer as the leading candidate for your party in the
##  upcoming parliamentary election?" (article's English; Danish wording not deposited). Forced, no
##  opt-out. The source stores the chosen option's piped text ("Kandidat 1|{#task.Concept._1...");
##  the profile number is read from its "Kandidat <n>" prefix (the authors' code relabels the two
##  factor levels 1/2 in the same order; checked).
##Treatment (between respondents): group_1 -> trial_terror_threat ("Yes" = read the PET assessment that
##  the terrorist threat to Denmark is significant, with a reminder before each task; "No" = control).
##Level weights: the article says origin country and education were weighted to match Danish political
##  candidates (probabilities in its Supplementary A.2, not seen); observed: origin Danmark ~79%,
##  Tyrkiet ~15%, Pakistan ~3%, Syrien ~2%; education Lang videregående ~49%. Restrictions: not
##  documented. Attribute order: not documented or recorded.
##Covariates: cov_gender (bagg1: Kvinde -> female, Mand -> male; the authors' code treats Kvinde as
##  woman), cov_age (alder, years), cov_age_group (alder_kat text), cov_region, cov_education
##  (uddannelse_det answer text), cov_vote_intention (bagg6_B, party the respondent would vote for;
##  "Vil ikke oplyse" -> NA), cov_vote_last (bagg8_B, last vote, text as stored). The source Id (a
##  scrambled string) is re-keyed to 1..1034 in file order. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "conjoint_data_anonymized.rds")))
stopifnot(nrow(s) == 1034, uniqueN(s$Id) == 1034)
s[, id := seq_len(.N)]
att <- c(gender = 1, age = 2, origin = 3, education = 4, political_experience = 5)
d <- rbindlist(lapply(1:8, function(t) rbindlist(lapply(1:2, function(p) {
  r <- data.table(id = s$id, task = t, profile = p)
  for (k in names(att)) r[, paste0("attr_", k) := as.character(s[[sprintf("conjoint_%d_Concept_%d_attribute_%d", t, p, att[[k]])]])]
  ch <- as.character(s[[sprintf("conjoint_%d_choice", t)]])
  stopifnot(grepl("^Kandidat [12]\\|", ch), identical(levels(s[[sprintf("conjoint_%d_choice", t)]])[1], unique(ch[startsWith(ch, "Kandidat 1")])))
  r[, choice := as.integer(as.integer(substr(ch, 10, 10)) == p)]
  r
}))))
stopifnot(!anyNA(d), !any(d[, .SD, .SDcols = patterns("^attr_")] == ""))
cv <- s[, .(id, trial_terror_threat = as.character(group_1),
            cov_gender = c(Kvinde = "female", Mand = "male")[as.character(bagg1)], cov_age = as.integer(alder),
            cov_age_group = as.character(alder_kat), cov_region = as.character(region), cov_education = as.character(uddannelse_det),
            cov_vote_intention = as.character(bagg6_B), cov_vote_last = as.character(bagg8_B))]
cv[cov_vote_intention == "Vil ikke oplyse", cov_vote_intention := NA_character_]
stopifnot(!anyNA(cv$cov_gender), cv$trial_terror_threat %in% c("No", "Yes"))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice"))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 1034 * 16)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "littmann_2026_terror_women_candidates.csv"))
