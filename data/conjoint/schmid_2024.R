##Colombian adults' choices between two fictitious forest-conservation projects in an area affected by FARC violence,
##described by seven present/absent peacebuilding components (Experiment 2), from
##Schmid, D., & Vlaskamp, M. C. (2024). Public preferences of environmental peacebuilding: The case of forest
##conservation projects in Colombia. Environment and Security, 2(4), 568-598. https://doi.org/10.1177/27538796241241581
##Data: Schmid, D., & Vlaskamp, M. C. (2023). Public preferences for environmental peacebuilding in Colombia: survey data
##and replication code [Data set]. figshare. https://doi.org/10.6084/m9.figshare.23717253 (CC BY 4.0).
##Files read: SupportingData-figshare.xlsx (one sheet, 9,024 rows x 30 columns) and the record description;
##230720_Script_Publication.R read as text only (never run).
##Usage: Rscript schmid_2024.R <dir holding the .xlsx> <output dir>
##
##Sample (record description): Netquest online panel, Colombia, 22-30 July 2021, quotas on gender, age, geography,
##stratum, region; 1,504 respondents x 3 tasks x 2 profiles. The depositors had ALREADY excluded respondents who failed
##either of two manipulation checks; those respondents are not in the deposit (cannot be restored). Experiment 1 of the
##survey is not deposited.
##Task/profile: no task or profile column. Rows are keyed by ResponseID (increasing within RespondentID, 6 per
##respondent); consecutive rows 1-2, 3-4, 5-6 in ResponseID order form the three pairs. Verified: exactly one profile
##Selected in each of the 4,512 pairs, and the chosen row is first in about half the pairs (not outcome-ordered).
##task and profile are INFERRED from that order (display position not recorded).
##CODED ATTRIBUTES (#3474). Seven binary components, each 0/1 as deposited, analysed by the authors as binary
##regressors. The authors' labels for the "1" level (replication script, plot labels; English, the survey was in
##Spanish): attr_jobs_code "Generates well-paid jobs", attr_publicservices_code "Improves public services",
##attr_dialogue_code "Stimulates dialogue between former combatants and victims", attr_memory_code "Create memorials",
##attr_integrationcombatants_code "Supports integration of former combatants", attr_decisionmaking_code "Includes
##inclusive decision-making processes", attr_publicsecurity_code "Includes measures to improve public security".
##1 = the component is part of the project; 0 = it is not. How an absent component was displayed (omitted, or stated as
##absent) is not documented, and the Spanish wording is not deposited, so all seven are kept as codes.
##Outcome: choice = Selected (1 = project chosen), forced choice, opt_out = no; question wording not deposited.
##Covariates: cov_age; cov_sex_code (Sex 0/1, unlabelled; one respondent has 0.5, kept as deposited);
##cov_department (text); cov_size_place_code (SizePlaceofResidence, unlabelled; the authors treat >= 4 as urban);
##cov_social_stratum (1-6 estrato); cov_ideology (1-10 left-right, per the record description); cov_support_peace_agreement
##(1-4; the authors code >= 3 as supporting the 2016 agreement); cov_respondent_victim_guerilla, cov_family_victim_guerilla,
##cov_territory_farc (0/1). Dropped: the authors' derived dummies (Under40, Age40to59, Age60Plus, Urban, LowForest,
##LowStrata, MediumStrata, HighStrata, LeftIdeology, ProPeaceAgreement), ResponseID. RespondentID re-keyed to 1..N.
##No further exclusions applied.
##Counts: 1,504 respondents, 9,024 rows = the record and the paper's stated N.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_excel(file.path(raw, "SupportingData-figshare.xlsx"), 1, na = "NA"))
stopifnot(nrow(d) == 9024L, uniqueN(d$ResponseID) == 9024L, d[, .N, RespondentID][, all(N == 6L)])
setorder(d, RespondentID, ResponseID)
d[, k := seq_len(.N), RespondentID]
d[, `:=`(task = as.integer((k + 1L) %/% 2L), profile = as.integer(2L - k %% 2L))]
stopifnot(d[, sum(Selected), .(RespondentID, task)][, all(V1 == 1)])
at <- c(Jobs = "jobs", PublicServices = "publicservices", Dialogue = "dialogue", Memory = "memory",
        IntegrationCombatants = "integrationcombatants", Decisionmaking = "decisionmaking", PublicSecurity = "publicsecurity")
o <- d[, .(id = match(RespondentID, sort(unique(RespondentID))), task, profile, choice = as.integer(Selected))]
for (k in names(at)) { stopifnot(all(d[[k]] %in% 0:1)); set(o, j = paste0("attr_", at[[k]], "_code"), value = as.integer(d[[k]])) }
o[, `:=`(cov_age = as.integer(d$Age), cov_sex_code = d$Sex, cov_department = d$Department,
         cov_size_place_code = as.integer(d$SizePlaceofResidence), cov_social_stratum = as.integer(d$SocialStratum),
         cov_ideology = as.integer(d$Ideology), cov_support_peace_agreement = as.integer(d$SupportPeaceAgreement),
         cov_respondent_victim_guerilla = as.integer(d$RespondentVictimGuerilla),
         cov_family_victim_guerilla = as.integer(d$FamilyVictimGuerilla), cov_territory_farc = as.integer(d$TerritoryFARC))]
setorder(o, id, task, profile)
fwrite(o, file.path(out, "schmid_2024_peacebuilding_colombia.csv"))
cat(nrow(o), uniqueN(o$id), "\n")
