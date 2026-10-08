##Candidate-selection conjoint with German party delegates, from
##Rehmert, J. (2022). Party elites' preferences in candidates: Evidence from a conjoint
##experiment. Political Behavior, 44 (online 2020). https://doi.org/10.1007/s11109-020-09651-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/IRUDXK, CC0 1.0, no restricted files.
##Files read: conjoint_data.dta (long: ResponseID x TaskID x ConceptID, attribute value labels in
##German, choice, respondent survey answers) and README.txt (variable list). The authors'
##replication_code.R was read as text (not run): it translates the German levels to English and
##recodes age 1/2/3 to "30/45/65 Years Old"; the table keeps the German value labels of the .dta.
##The article was not accessible here; design facts below come from the deposit only.
##Usage: Rscript rehmert_2022.R <dir holding conjoint_data.dta> <output dir>
##
##Respondents: delegates of party conventions (CDU, SPD, FDP, Die LINKE, Buendnis 90/Die Gruenen;
##the deposit's `party`) choosing between two hypothetical candidates (for a list position, per the
##article's abstract). 296 respondents with conjoint data; 293 did 5 paired tasks, 3 did fewer
##(1 did 3 tasks, 2 did 4); 50 rows of 50 further respondents carry no task, attributes or choice
##(no conjoint answered) and are omitted. 1,476 tasks, 2,952 rows. The authors drop 1 respondent
##(8 rows) whose party_id is missing; the table keeps them (cov_party NA). The article's subgroup
##plots give n = 133 + 116 (first-time / veteran) and 119 + 131 (female / male delegates).
##Outcome: choice = the candidate chosen (deposit `choice`, "Selected"); forced choice, exactly one
##chosen per task (checked); no opt-out. The question wording is not in the deposit (paraphrase).
##10 attributes (German level text = .dta value labels): age (Alter: "30", "45", "65": the labels
##are bare numbers; the authors render them "30/45/65 Years Old"), gender (Geschlecht), education
##(Schulbildung), occupation (Beruf), district (Wahlkreiskandidatur), experience (Legislative
##Erfahrung), party_length (Laenge der Parteimitgliedschaft), ideology (Position innerhalb der
##Partei), party_office (Parteiamt), activity (Aktivitaet in Ihrem Kreisverband).
##Randomization: no source in the deposit states the scheme. The table shows clearly unequal and
##dependent level shares: occupation Rechtswesen/Landwirt occur almost only with Abitur (25 and 15
##of ~1,000 Hauptschule profiles), and party_length "6 Jahre" dominates when experience is MdL or
##Kreistag (881/942, 866/918) but not when it is Keine; the authors interact education x occupation
##and experience x party_length in every model. No pair is entirely absent, so restrictions are
##recorded `unknown` and level_weights `observed` (see the design record).
##Covariates (deposit columns, codings as stored): cov_party (party of the convention; "" -> NA),
##cov_gender (del_gender "Woman" -> female, "Man" -> male, as the authors' code recodes them
##to Female/Male; "" -> NA), cov_age (del_age, "R's age" in README), cov_birth_year (yob),
##cov_university (del_education "studied"/"not studied"; "" -> NA), cov_education_code (education_1,
##codes 2-7 with no value labels or codebook: kept as codes), cov_lr_own / cov_lr_party (own and
##own party's left-right position, as stored), cov_joined_party (year joined, as stored; one
##respondent has 26), cov_time_delegate (times as delegate), cov_party_office (del_ptyoffice text),
##cov_leg_experience (del_experience text).
##Dropped: the multi-select dummies parteiamt_* and exp_* (summarised by del_ptyoffice and
##del_experience), party_id (= party), and derived del_exp_dichotom, del_ideology, del_membership.
##No platform IDs; ResponseID (survey sequence numbers) re-keyed to 1..N in source order.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "conjoint_data.dta"))
at <- c("age", "gender", "education", "occupation", "district", "experience", "party_length",
        "ideology", "party_office", "activity")
d <- as.data.table(k[, c("ResponseID", "TaskID", "ConceptID", "choice")])
for (v in at) set(d, j = paste0("attr_", v), value = as.character(as_factor(k[[v]], levels = "labels")))
cv <- as.data.table(k[, c("party", "del_gender", "del_age", "yob", "del_education", "education_1",
                          "lr_own", "lr_party", "joined_party", "time_delegate", "del_ptyoffice",
                          "del_experience")])
d <- cbind(d, cv)
d <- d[!is.na(choice)]
stopifnot(d[, !anyNA(.SD), .SDcols = paste0("attr_", at)])
stopifnot(d[, sum(choice), by = .(ResponseID, TaskID)][, all(V1 == 1)], d[, .N, by = .(ResponseID, TaskID)][, all(N == 2)])
d[, id := match(ResponseID, unique(ResponseID))]
setnames(d, c("TaskID", "ConceptID"), c("task", "profile"))
d[, `:=`(task = as.integer(task), profile = as.integer(profile), choice = as.integer(choice))]
blank <- function(x) fifelse(x == "", NA_character_, x)
stopifnot(all(d$del_gender %in% c("", "Man", "Woman")))
d[, `:=`(cov_party = blank(party),
         cov_gender = c(Man = "male", Woman = "female")[del_gender],
         cov_age = del_age, cov_birth_year = as.integer(yob), cov_university = blank(del_education),
         cov_education_code = as.integer(education_1), cov_lr_own = lr_own, cov_lr_party = lr_party,
         cov_joined_party = as.integer(joined_party), cov_time_delegate = as.integer(time_delegate),
         cov_party_office = blank(del_ptyoffice), cov_leg_experience = blank(del_experience))]
## covariates constant within respondent
stopifnot(d[, lapply(.SD, uniqueN), by = id, .SDcols = patterns("^cov_")][, all(unlist(.SD) == 1), .SDcols = -1])
d <- d[, c("id", "task", "profile", "choice", paste0("attr_", at), grep("^cov_", names(d), value = TRUE)), with = FALSE]
stopifnot(uniqueN(d$id) == 296, nrow(d) == 2952)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rehmert_2022_party_delegates.csv"))
