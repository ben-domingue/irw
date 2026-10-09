##Hiring vignettes (Switzerland), 2 x 2 factorial, two samples, from
##Ruedin, D. (2020). Labour Market Vignettes: Hiring [Data set]. Harvard Dataverse.
##Replication data: Harvard Dataverse doi:10.7910/DVN/KRSN2Z, CC0 1.0, no restricted files, no
##terms. No article (data-only deposit; the author's description says the population results
##suggest no discrimination "but I don't trust them"). A replication of Baert & De Pauw (2014),
##Economics Letters 125(2). Files read: hiring_population_20200426.csv and
##hiring_students_20200426.csv (Dataverse original format), hiring_documentation.txt (codebook),
##"Questionnaire Population Sample DE.docx" (German questionnaire), "Question wording student
##sample.txt" (French vignette and items). Not built: hiring_priming_20200426 (n = 17).
##Usage: Rscript ruedin_2020.R <dir holding the two csv files> <output dir>
##
##Design: one vignette per respondent (task 1, profile 1). Respondents imagine recruiting for a
##large firm and see a CV. Two randomized factors (codebook "vignette" 1-4): the job (receptionist
##vs director of sales) and the candidate's name (Swiss vs migrant-origin); every CV states Swiss
##nationality, a local residence, and the same skills. Full 2 x 2, no restrictions possible.
##Level text is the FRENCH version as displayed to French-language respondents: job "un/e
##réceptionniste" / "un/e directeur/rice des ventes" (population file `Job`; the student file has
##only the code, mapped with the same French text, which the student question wording shows as
##"un/e directeur/rice des ventes"); name "François Meylan" / "Ervin Beqiri" (population,
##`Name`) and "François Meylan" / "Dalmat Beqiri" (students, codebook). German-language
##respondents saw "eine/n Rezeptionistin/en" / "eine/n Vertriebsleiterin/er" and the Swiss name
##"Martin Baumgartner" (population file Job_DE/Name_DE; same migrant name). Which language a
##respondent used is NOT recorded, so the French text stands for both (label_language fr).
##Samples are separate tables (different populations, fieldings and response formats):
##  ruedin_2020_hiring_population: general population via Qualtrics, 12-20 Aug 2016, n = 211;
##    outcomes on a continuous slider, stored 0-7 as in the source (the codebook says "1:7", but
##    every item has values from 0 to 7 with one decimal, e.g. 22 zeros on rating_often_ill, so
##    the slider evidently ran 0-7; values not rescaled). Covariate sliders (Edu, MCP, JobRare*)
##    are also continuous.
##  ruedin_2020_hiring_students: BA/MA students, Nov 2014, n = 197 (one vignette at the end of
##    the survey in doi:10.7910/DVN/GBPLBI), categorical 1-7. The 2 respondents with no answer on
##    any of the 12 outcome items are dropped (rows with no outcome are omitted): 195 kept, ids
##    re-keyed 1..195 (the source has no respondent ID; ids are row numbers in both tables). 3 more
##    answered only the manipulation checks, not the nine evaluation items.
##Outcomes (all ratings, raw; anchors of the 1/0-7 scales are not documented, so unknown).
##German item text from the population questionnaire Q44, French from the student file:
##  rating_invite "Ich lade die Person für ein Erstgespräch ein." / "J'invite cette personne pour
##    un premier rendez-vous"; rating_hire "Ich denke, dass ich diese Person einstellen werde.";
##  rating_employer_happy, rating_colleagues_happy, rating_clients_happy ("... würde(n) es
##    wahrscheinlich schätzen, mit dieser Person zusammenzuarbeiten"); rating_competent;
##  rating_profile; rating_risk ("Ich würde ein Risiko eingehen, diese Person einzustellen";
##    higher = more risk); rating_often_ill ("Diese Person wird oft krank geschrieben sein").
##  Manipulation checks (Q43, Ja = 1 / Nein = 2 as stored; the codebook's "1 yes, 0 no" does not
##  match the data, which hold 1/2 as in the questionnaire): rating_check_woman ("Der/die
##  Kandidat/in ist eine Frau."), rating_check_swiss ("... ist schweizerischer Herkunft."),
##  rating_check_canton ("... wohnt im Kanton Aargau" / "habite dans le canton de Neuchâtel").
##Covariates: cov_gender (Sex 1 female, 2 male per codebook; "3 other" offered but unused);
##cov_age (students only, years); cov_education_years (population, Edu "Jahre Ausbildung");
##cov_party_id (ClosestParty, codebook's French party labels); cov_born_ch_code (1 Switzerland,
##2 abroad), cov_citizenship_code (CHNaturalized 1 Swiss, 2 naturalized, 3 foreign; population),
##cov_minority_code (DiscriminatedMinority 1 no, 2 yes), cov_job_rare_gender, cov_job_rare_foreign
##(population, slider, codebook "0 disagree, 4 agree"), cov_mcp (self-monitoring item, as stored),
##cov_task_difficulty (population, 1 very easy .. 5 very difficult), cov_duration_sec (population,
##whole survey, seconds). Student study and family covariates are left out.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
party <- c("UDC", "PS - Parti socialiste suisse", "PLR- Les Libéraux-Radicaux", "PDC - Parti Démocrate-Chrétien",
           "PBD - Parti Bourgeois Démocratique Suisse", "PES - Les verts/Parti écologiste suisse", "PVL - Parti vert'libéral",
           "PEV - Parti Evangelique Suisse", "PCS - Parti chrétien-social", "Lega dei Ticinesi", "UDF - Union Démocratique Fédérale",
           "AL - La Gauche", "MSL - Mouvement socio-libéral", "MCG - Mouvement citoyens genevois",
           "PST - Parti Suisse du Travail - Parti Ouvrier et Populaire", "solidaritéS", "DS - Démocrates Suisses", "Piratenpartei")
oc <- c(InviteInterview = "rating_invite", ProbablyHire = "rating_hire", EmployerHappy = "rating_employer_happy",
        ColleaguesHappy = "rating_colleagues_happy", ClientsHappy = "rating_clients_happy", IsCompetent = "rating_competent",
        HasProfile = "rating_profile", IsRisk = "rating_risk", IsOftenIll = "rating_often_ill",
        IsWoman = "rating_check_woman", IsSwiss = "rating_check_swiss", IsLocation = "rating_check_canton")
job <- c("un/e réceptionniste", "un/e directeur/rice des ventes")
common <- function(s, migrant) {
  d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L)
  for (v in names(oc)) d[, (oc[[v]]) := s[[v]]]
  d[, attr_job := job[2L - s$Vignette %% 2L]]
  d[, attr_name := fifelse(s$Vignette <= 2L, "François Meylan", migrant)]
  d[, cov_gender := c("female", "male", "other")[s$Sex]]
  d[, cov_party_id := party[s$ClosestParty]]
  d[, cov_born_ch_code := as.integer(s$BornCH)][, cov_minority_code := as.integer(s$DiscriminatedMinority)]
  d[, cov_mcp := s$MCP]
  d
}
p <- fread(file.path(raw, "hiring_population_20200426.csv"), encoding = "UTF-8")
stopifnot(nrow(p) == 211, p[, all(Name == fifelse(Vignette <= 2, "François Meylan", "Ervin Beqiri"))],
          p[, all(Job == job[2L - Vignette %% 2L])], all(p$Sex %in% 1:2))
d <- common(p, "Ervin Beqiri")
d[, `:=`(cov_education_years = p$Edu, cov_citizenship_code = as.integer(p$CHNaturalized),
         cov_job_rare_gender = p$JobRareGender, cov_job_rare_foreign = p$JobRareForeign,
         cov_task_difficulty = as.integer(p$DifficultTask), cov_duration_sec = p$Duration)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ruedin_2020_hiring_population.csv"))
s <- fread(file.path(raw, "hiring_students_20200426.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 197, !anyNA(s$Vignette))
d <- common(s, "Dalmat Beqiri")
d[, cov_age := as.integer(s$Age)]
d <- d[rowSums(!is.na(d[, oc, with = FALSE])) > 0]
d[, id := seq_len(.N)]
setorder(d, id, task, profile)
cat("students kept", nrow(d), "\n")
fwrite(d, file.path(out, "ruedin_2020_hiring_students.csv"))
