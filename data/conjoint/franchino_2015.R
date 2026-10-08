##Italian candidate-choice conjoint (valence and ideology) from
##Franchino, F., & Zucchini, F. (2015). Voting in a multidimensional space: A conjoint analysis
##employing valence and ideology attributes of candidates. Political Science Research and
##Methods, 3(2), 221-241. https://doi.org/10.1017/psrm.2014.24
##Replication data: Harvard Dataverse doi:10.7910/DVN/26639, CC0 1.0, no restricted files.
##File read: data.dta (Dataverse original; Stata value labels). "Conjoint survey.docx" (the full
##Italian instrument, incl. all 27 candidate pairs as displayed), "Stated choice example.docx",
##"Replication guidelines.pdf" and the do-files (as text) were read for wording and design.
##Usage: Rscript franchino_2015.R <raw dir> <output dir>
##
##405 students of three degree programmes (Campione: international studies, globalization,
##political science) at the University of Milan, two survey waves (2012: 186, 2013: 219; the same
##instrument, pooled by the authors; cov_survey_wave). Each saw the SAME fixed set of 27 pairs of
##candidates (Candidato A = profile 1, Candidato B = profile 2), in randomized order ("LA SEQUENZA DI
##QUESTE 27 DOMANDE E' RANDOMIZZATA"). task = n_contest, the position at which the pair was shown
##(the authors' carryover diagnostics condition on it); trial_contest = n_vote, the pair's number in
##the instrument (1-27). Both recorded.
##Outcome: choice (the authors' Y = vote == candidate): "Per ogni coppia, deve scegliere il candidato
##per il quale Lei voterebbe. PER CHI VOTEREBBE?" ("For each pair, choose the candidate you would
##vote for. Who would you vote for?"); options Candidato A / Candidato B, forced, no opt-out.
##23 pairs with no answer are omitted.
##Attributes, Italian text as displayed in the pair tables (rows: Istruzione, Reddito, Altre
##informazioni, Opinione su servizi sociali e tasse, Opinione sul diritto di famiglia; fixed order):
##  education: Licenza media / Diploma superiore / Laurea
##  income: Meno di 900 euro di reddito al mese / Tra i 900 e i 3000 euro di reddito al mese / Più di
##    3000 euro di reddito al mese
##  corruption: Nessun procedimento a carico del candidato / Il candidato è indagato per corruzione /
##    Il candidato è stato condannato per corruzione
##  taxes_services: Più servizi sociali, anche a costo di più tasse / Mantenere il livello di
##    fornitura di servizi sociali e di tassazione / Tagliare le tasse, anche a costo di minori servizi
##    sociali
##  same_sex_rights: Pari diritti alle coppie omosessuali / Alcuni diritti alle coppie omosessuali /
##    Nessun diritto alle coppie omosessuali
##  The two opinion attributes were shown in quotation marks; the marks are not stored. The codes
##  in data.dta were checked against all 54 displayed profiles of the instrument: all agree.
##Design: a fixed fractional set of 27 pairs (not independent randomization per respondent), so
##restrictions = yes (only these 54 profiles occur).
##Covariates (Stata labels): cov_degree (SIE/GLO/SPO), cov_pol_interest (1 none .. 4 substantial),
##cov_importance_education / _income / _integrity / _taxes_services / _same_sex (Q29, 1 none ..
##4 substantial), cov_left_right (1 left .. 10 right), cov_voted (0/1), cov_birth_year, cov_age
##(authors': survey year - birth year), cov_gender (Q.32 'Il suo genere è' Maschio/Femmina, Conjoint survey.docx;
##data.dta `gender` labels Female = 0, Male = 1 -> female/male), cov_italian (0/1),
##cov_secondary_school (1 liceo, 2 istituto tecnico, 3 istituto professionale, 66 other),
##cov_work_hours (1 do not work, 2 1-10, 3 11-20, 4 21-30, 5 more than 30 hours), cov_iseeu (means
##tested, 0/1), cov_school_grade (authors' converted grade), cov_lives_milan (0/1),
##cov_survey_wave (2012/2013). cov_age is the deposit's own `age` (label '= survey - birthy'),
##not computed here. The deposit documents no survey weight.
##Dropped: IDContatto (panel contact id; re-keyed), Data (date and time of participation), the
##raw nationality code (only Italy/Albania/France/China/Romania labelled; the authors' italian
##dummy kept), derived ftstudent/lyceum dummies, gr, nonmissing, vote/candidate (in choice/profile).
##N = 405 respondents in the deposit; the article's count was not checked (paywalled).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(s) == 21870, uniqueN(s$IDContatto) == 405, identical(unname(attr(s$gender, "labels")), c(0, 1)),
          identical(names(attr(s$gender, "labels")), c("Female", "Male")), s$gender %in% 0:1)
s[, id := match(IDContatto, sort(unique(IDContatto)))]
z <- function(x) as.integer(zap_labels(x))
lv <- list(education = c("Licenza media", "Diploma superiore", "Laurea"),
           income = c("Meno di 900 euro di reddito al mese", "Tra i 900 e i 3000 euro di reddito al mese",
                      "Più di 3000 euro di reddito al mese"),
           corruption = c("Nessun procedimento a carico del candidato", "Il candidato è indagato per corruzione",
                           "Il candidato è stato condannato per corruzione"),
           taxspend = c("Più servizi sociali, anche a costo di più tasse", "Mantenere il livello di fornitura di servizi sociali e di tassazione",
                        "Tagliare le tasse, anche a costo di minori servizi sociali"),
           samesex = c("Pari diritti alle coppie omosessuali", "Alcuni diritti alle coppie omosessuali", "Nessun diritto alle coppie omosessuali"))
an <- c(education = "education", income = "income", corruption = "corruption", taxspend = "taxes_services", samesex = "same_sex_rights")
d <- data.table(id = s$id, task = z(s$n_contest), profile = z(s$candidate), choice = z(s$Y), trial_contest = z(s$n_vote))
for (k in names(lv)) { code <- z(s[[k]]); stopifnot(all(code %in% 1:3)); d[, paste0("attr_", an[[k]]) := lv[[k]][code]] }
stopifnot(d[, all(choice == (z(s$vote) == profile), na.rm = TRUE)])
# each respondent: 27 positions, each a distinct contest
stopifnot(d[, .(uniqueN(task), uniqueN(trial_contest), .N), id][, all(V1 == 27 & V2 == 27 & N == 54)])
stopifnot(d[, uniqueN(trial_contest), .(id, task)][, all(V1 == 1)])
d <- d[!is.na(choice)]
stopifnot(d[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)])
cv <- unique(s[, .(id, cov_degree = as.character(as_factor(Campione)), cov_pol_interest = z(pol_interest),
                   cov_importance_education = z(edu_imp), cov_importance_income = z(inc_imp), cov_importance_integrity = z(hon_imp),
                   cov_importance_taxes_services = z(taxspend_imp), cov_importance_same_sex = z(samesex_imp),
                   cov_left_right = z(left_right), cov_voted = z(voter), cov_birth_year = z(birthy), cov_age = z(age),
                   cov_gender = c("female", "male")[z(gender) + 1L], cov_italian = z(italian), cov_secondary_school = z(sec_school), cov_work_hours = z(working_h),
                   cov_iseeu = z(ISEEU), cov_school_grade = as.numeric(school_grade2), cov_lives_milan = z(milan),
                   cov_survey_wave = 2012L + z(survey))])
stopifnot(!anyDuplicated(cv$id))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "franchino_2015_candidate_valence.csv"))
