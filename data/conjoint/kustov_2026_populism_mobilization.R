##Candidate-pair conjoint with populist rhetoric (US), from
##Kustov, A., & Dai, Y. (2026). What is populism good for? An experimental test of mobilization effects.
##Research & Politics. https://doi.org/10.1177/20531680261434109
##Replication data: Harvard Dataverse doi:10.7910/DVN/3OMMOS, CC0 1.0. File read: data_clean.tab (Dataverse original
##format = comma-separated text, saved here as data.csv; the deposit's .tab is actually comma-separated); rep.Rmd (the
##authors' PopulismConjoint_rap_replication.Rmd) and README.txt read as text; rap_conjoint_by_cand.RData used only to
##check the candidate/preference coding (not an input to the table).
##Usage: Rscript kustov_2026_populism_mobilization.R <dir holding data.csv> <output dir>
##
##3,502 US adults (rep.Rmd: n = 3502 respondents / 28,016 candidates; matches). Each saw 8 tasks of 2 candidates
##(wide columns choice<t>_<attr><1|2>, pref<t>); 5 attributes shown as text: job (16 occupations), office (never held
##office before / held office for many years), and three statements drawn from banks of 32, 32 and 64 sentences:
##attr_pluralism_statement (populist "people" / anti-pluralist wording or pluralist wording), attr_moralism_statement
##(anti-elite wording or a neutral criticism of the government) and attr_policy_statement (immigration / economic policy
##position). The authors' derived `populist` flag (both rhetoric statements populist) and the congruence variables are
##dropped.
##The pluralism statement is blank for 1,703 of 56,032 candidate rows (3.0%), only on candidates whose moralism statement is
##non-populist (and which the authors code populist = 0). Because it is confined to one rhetoric condition and occurs
##uniformly across tasks, it is read as "pluralism statement not shown by design" and stored as `(not shown)`; the
##deposit does not document this, so it is an INFERENCE (README rule: a blank would otherwise mean missing).
##Outcome: choice = candidate chosen in the pair; pref 1 = candidate 1, 2 = candidate 2, 0 = abstained (neither),
##so OPT-OUT: 4,516 of 28,016 tasks have choice = 0 on both profiles. Wording of the vote question is not given in the deposit
##(rep.Rmd: "voted = whether respondent voted for either candidate in a candidate-pair; 0: abstained").
##Position within the pair (profile 1/2) is the _1/_2 column and is recorded. Covariates: cov_gender (Gender: Male = male,
##Female = female, Other = other), cov_college (College, 0/1 degree indicator as in the file), cov_ideology
##(ideology3 text: liberal / moderate / conservative), cov_party_id (partyid3 text: Democrat / Independent / Republican;
##the literal "NA" -> missing). Dropped: derived dummies (Female, Republican2, Democrat2, Populist2, partyid2), the
##populist-attitude scale (populismatt, populismattstr), immigrationLR and econLR. No survey weight. id is the file's
##integer id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.csv"), na.strings = NULL)
stopifnot(nrow(s) == 3502, !anyDuplicated(s$id))
L <- list()
for (t in 1:8) for (p in 1:2) {
  g <- function(a) s[[sprintf("choice%d_%s%d", t, a, p)]]
  pl <- g("pluralism"); pl[pl == ""] <- "(not shown)"
  L[[length(L) + 1]] <- data.table(id = s$id, task = t, profile = p,
    choice = as.integer(s[[paste0("pref", t)]] == p),
    attr_job = g("job"), attr_office = g("office"), attr_pluralism_statement = pl,
    attr_moralism_statement = g("moralism"), attr_policy_statement = g("policy"))
}
d <- rbindlist(L)
stopifnot(all(unlist(s[, paste0("pref", 1:8), with = FALSE]) %in% 0:2))
stopifnot(!anyNA(d), d[, all(nzchar(attr_job) & nzchar(attr_office) & nzchar(attr_moralism_statement) & nzchar(attr_policy_statement))])
cov <- data.table(id = s$id, cov_gender = c(Male = "male", Female = "female", Other = "other")[s$Gender],
  cov_college = as.integer(s$College), cov_ideology = s$ideology3,
  cov_party_id = fifelse(s$partyid3 %in% c("NA", ""), NA_character_, s$partyid3))
d <- merge(d, cov, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kustov_2026_populism_mobilization.csv"))
