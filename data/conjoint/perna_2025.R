##Healthcare-priority patient conjoint (Belgium, Spain) from
##Perna, R., & Umpierrez de Reguero, S. (2025). Intra-EU migration and healthcare deservingness:
##A conjoint experiment in Belgium and Spain. Social Science & Medicine, 367.
##https://doi.org/10.1016/j.socscimed.2025.117714
##Data: Perna, R., & Umpierrez de Reguero, S. (2024). EU-TRHeaDS Conjoint Dataset. Zenodo.
##doi:10.5281/zenodo.13144054, CC BY 4.0. Files read: EU-TRHeaDS_conjoint_dataset.csv (';'
##separated) and "EU-TRHeaDS_Codebook conjoint.pdf" (all labels below are from it).
##Usage: Rscript perna_2025.R <dir holding the csv> <output dir>
##
##YouGov web panels, July-August 2022, samples representative on gender, age, education and
##region; 4 forced-choice tasks of two fictitious patients (A/B), 4 attributes "all randomly
##assigned" (codebook p.1). Two tables, one per country: the article analyses Belgium and Spain
##side by side and stresses the country differences (abstract), and the own-nationality level
##differs ("Belgian" vs "Spanish"):
##  perna_2025_healthcare_be  (1,307 respondents)   perna_2025_healthcare_es  (1,307)
##Task = `Task` (recorded); profile = row order within task (2 rows per task; Patient A then B
##assumed from file order: INFERRED, the file has no profile column; exactly one row chosen per
##task).
##Outcomes:
##  choice = ChosenPatient, "Among these two patients, which one would you prioritise to be
##           visited today?" forced choice (no opt-out).
##  rating = ProbChosen, "On a scale from 0 to 10, how probable is that you will prioritise this
##           patient over the other?" 0 = Not at all, 10 = Totally. Asked only about the chosen
##           patient, so it is NA on the other profile.
##Attribute text: the codebook's English labels (the screen text, presumably Dutch/French and
##Spanish, is not deposited): nationality 0 = own nationality, written "Belgian" / "Spanish" per
##country (codebook "Belgian/Spanish (depending on participating country)"), 1 Danish, 2
##Italian, 3 Bulgarian; migration status Born in the country / Long term / Short term (codebook
##p.1: born in / long-term resident in / short-term resident in the reporting country);
##responsibility over ill health Genetic / Unhealthy ("genetic history of a disease", "unhealthy
##behaviour"); employment status Employed / Unemployed (in the reporting country).
##Dropped: one Belgian respondent (source ID 1842317331) whose rows are corrupt (ChosenPatient
##missing on 5 of 8 rows, ProbChosen 0/1): Belgium 1,308 -> 1,307 = article n per country.
##The source ID (a 10-digit panel number) is re-keyed to 1..n.
##Covariates (codebook labels): cov_age_group (ageRec bands 18-24 ... 65 or over), cov_gender
##(1 Male, 2 Female), cov_education (educationRec, ISCED groups; 27 Spanish respondents blank ->
##NA), cov_citizenship (citizenshipRec), cov_region (Belgium only: Brussels Capital / Flanders /
##Wallonia). Spain keeps cov_region_code: its codes run 1-17 while the codebook lists 18 regions,
##and code 7 (codebook: Ceuta and Melilla) holds 40 respondents, so the mapping is doubtful.
##trial_time_sec = time on that task (timeTask1-4; two values use a decimal comma, read as
##decimals). No survey weight in the deposit.
##Spot check (choice shares): own nationality .57 (BE) / .58 (ES) vs Danish/Italian/Bulgarian
##.46-.49; short-term migrant .42/.41 vs born in the country .56/.59, the direction of the article's
##penalties (abstract); numbers not compared with the article's tables.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "EU-TRHeaDS_conjoint_dataset.csv"), sep = ";", colClasses = list(character = paste0("timeTask", 1:4)))
stopifnot(nrow(s) == 20920, uniqueN(s$ID) == 2615)
s <- s[ID != 1842317331]
stopifnot(s[, .N, .(ID, Task)][, all(N == 2)], s[, uniqueN(Task), ID][, all(V1 == 4)], !anyNA(s$ChosenPatient))
s[, profile := seq_len(.N), .(ID, Task)]
tt <- function(x) as.numeric(sub(",", ".", x, fixed = TRUE))
s[, trial_time_sec := fcase(Task == 1, tt(timeTask1), Task == 2, tt(timeTask2), Task == 3, tt(timeTask3), Task == 4, tt(timeTask4))]
own <- c(Belgium = "Belgian", Spain = "Spanish")
d <- s[, .(country = Country, src = ID, task = as.integer(Task), profile, choice = as.integer(ChosenPatient), rating = as.integer(ProbChosen),
           attr_nationality = fifelse(Nationality == 0, own[Country], c("Danish", "Italian", "Bulgarian")[pmax(Nationality, 1L)]),
           attr_migration_status = c("Born in the country", "Long term", "Short term")[MigrationStatus],
           attr_responsibility_illness = c("Genetic", "Unhealthy")[ResponsibilityIllness],
           attr_employment_status = c("Employed", "Unemployed")[EmploymentStatus], trial_time_sec,
           cov_age_group = c("18-24", "25-34", "35-44", "45-54", "55-64", "65 or over")[ageRec],
           cov_gender = c("male", "female")[gender],
           cov_education = c("Less than primary, primary and lower secondary education",
                             "Upper secondary and post-secondary non tertiary education", "Tertiary")[educationRec],
           cov_citizenship = c("Citizen of the reporting country", "Citizen of a EU country (other than the reporting one)",
                               "Citizen of a non-EU country")[citizenshipRec], region)]
stopifnot(d[, sum(choice), .(src, task)][, all(V1 == 1)], d[choice == 1, all(rating %in% 0:10)], d[choice == 0, all(is.na(rating))],
          !anyNA(d[, .(attr_nationality, attr_migration_status, attr_responsibility_illness, attr_employment_status)]))
for (cc in c("Belgium", "Spain")) {
  x <- d[country == cc]
  x[, id := match(src, unique(src))]
  if (cc == "Belgium") x[, cov_region := c("Brussels Capital", "Flanders", "Wallonia")[region]] else x[, cov_region_code := region]
  x[, c("country", "src", "region") := NULL]
  setcolorder(x, c("id", "task", "profile", "choice", "rating"))
  stopifnot(uniqueN(x$id) == 1307)
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, sprintf("perna_2025_healthcare_%s.csv", c(Belgium = "be", Spain = "es")[cc])))
}
