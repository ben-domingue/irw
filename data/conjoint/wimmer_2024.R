##Permanent-residency applicant conjoint in 22 countries from
##Wimmer, A., Bonikowski, B., Crabtree, C., Fu, Z., Golder, M., & Tsutsui, K. (2024).
##Geo-political rivalry and anti-immigrant sentiment: A conjoint experiment in 22 countries.
##American Political Science Review, 119(2), 1018-1035. https://doi.org/10.1017/S0003055424000753
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZZYSIZ, CC0 1.0, no restricted files.
##Files read: data_processed.csv (long, one row per profile) and data_test.csv (respondent
##demographics, joined by ResponseId). "Main Survey Instrument.pdf" (a US screenshot) and
##"Supplementary Materials.pdf" (pre-registration text) give the wording; replication_code.R
##was read as text, not run.
##Usage: Rscript wimmer_2024.R <raw dir> <output dir>
##
##Online samples (Lucid Marketplace, quotas on age, gender, education; fielded late Feb to
##early Mar 2022, around the Russian invasion of Ukraine) in 22 countries, each in its national
##language(s). ONE table with cov_country, because the authors pool all 22 surveys (one design,
##one fielding; replication_code.R estimates pooled marginal means) and the deposit carries
##English master labels for every country.
##Prompt (US version): "Imagine that you are an American immigration officer tasked with
##deciding who should be granted permanent resident status in your country. You will be given
##brief excerpts from two applications. Please choose which of the two applications should be
##given priority. ... We will ask you to make this choice for 6 pairs of candidates."
##Question: "Which person do you think would be a better fit to settle in America?"
##Person 1 / Person 2. choice = selected; forced choice, no opt-out.
##Attributes (row labels as on the screenshot; the deposit prefixes each level with its
##attribute name, e.g. "Age: 38", which is stripped): attr_language ("Proficiency in country's
##official language": None/Limited/Fluent), attr_age (21/38/62), attr_origin (country name),
##attr_gender (Male/Female), attr_occupation (Unemployed, Cleaner, Farmer, Accountant, Teacher,
##Doctor; the pre-registration says "janitor", the data and screenshot "Cleaner"),
##attr_residence ("Length of residence": 5/10/15 years). Whether attribute row order was
##randomized is not documented and not in the data.
##Country of origin has four levels per survey country, a 2x2 of rival/non-rival and racially/
##culturally similar/different as classified by the authors. The deposit's derived columns
##(ctry.rival, ctry.race, ctry.race.rival) are dropped; the classification is a function of
##cov_country and attr_origin:
##  different+non-rival / different+rival / similar+non-rival / similar+rival
##  most countries (australia brazil canada france germany hungary italy netherlands poland
##    spain sweden uk us): Japan / China / Ukraine / Russia
##  argentina: Japan / China / Ireland / United Kingdom;  greece: Japan / China / Jordan / Turkey
##  india: Japan / China / Turkey / Pakistan;  japan: Ukraine / Russia / Taiwan / China
##  korea: USA / Australia / Japan / China;  peru: Japan / China / Paraguay / Ecuador
##  philippines: Japan / China / Indonesia / Libya;  south africa: Japan / China / Angola / Zimbabwe
##  turkey: Japan / China / Serbia / Greece
##Restrictions (observed, not documented): in 15 countries no 21-year-old was ever a Doctor
##(in the other 7 Doctor is still rarer than other jobs); "None" language proficiency is
##rarer than the other two levels (about 21% of profiles in most countries, 33% in seven).
##TASK AND PROFILE ARE INFERRED FROM ROW ORDER: each respondent has exactly 12 consecutive
##rows; consecutive row pairs are tasks 1-6, first row of a pair = Person 1 (verified: every
##answered pair has exactly one selected profile). 16 respondents have no answer on any task
##(selected NA) and are dropped: 45,724 respondents, 274,344 tasks, 548,688 rows.
##The article reports 46,549 respondents who completed the survey and passed the attention
##check; the deposit holds 45,740 (809 fewer). Not reconciled.
##Covariates: cov_country (survey country, the source's lowercase name), cov_majority (1 =
##majority, 0 = minority respondent by country-specific census-style ethnic/linguistic/
##religious items; NA for 5 respondents), cov_days_since_invasion (source bef_after_war:
##day of response relative to 24 Feb 2022, negative = before; used for the authors' war
##analysis), cov_superiority_1..3 (the three "belief in national superiority" items, 1-5;
##wording not deposited; LOWER = more agreement, inferred from the authors' chauv_bin "Yes"
##having a mean scale of 1.8 vs 3.5 for "No"), and from data_test.csv (45,396 of 45,724
##matched): cov_age (years, "80+" = 80), cov_female (1 = Woman, 0 = Man, NA otherwise),
##cov_postsec_education (source ed_postsec 0/1; the authors label 1 ">BA"), cov_income_quintile
##(1-5), cov_citizen (1 = citizen of the survey country). Dropped: Qualtrics ResponseId,
##response timestamps and duration, employment and marital status text, the derived
##chauv_scale/chauv_bin and the "majority" text. No survey weight is deposited.
##Spot check: pooled marginal means (mean choice by level) reproduce the authors' Table I to
##3 decimals (e.g. Doctor 0.634, Unemployed 0.339, Language None 0.372, Age 62 0.426).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data_processed.csv"))
stopifnot(s[, .N, ResponseId][, all(N == 12)])
s[, r := seq_len(.N), ResponseId][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
stopifnot(s[, uniqueN(is.na(selected)), .(ResponseId, task)][, all(V1 == 1)],
          s[!is.na(selected), sum(selected), .(ResponseId, task)][, all(V1 == 1)])
s <- s[!is.na(selected)]
strip <- function(x) trimws(sub("^[^:]+: ", "", x))
d <- s[, .(src = ResponseId, task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_language = strip(lang), attr_age = strip(age), attr_origin = origin, attr_gender = strip(gender),
           attr_occupation = strip(occ), attr_residence = strip(residence),
           cov_country = country, cov_majority = fifelse(majority == "Majority respondents", 1L,
                                                         fifelse(majority == "Minority respondents", 0L, NA_integer_)),
           cov_days_since_invasion = as.integer(bef_after_war), cov_superiority_1 = as.integer(chauv_num_1),
           cov_superiority_2 = as.integer(chauv_num_2), cov_superiority_3 = as.integer(chauv_num_3))]
t <- fread(file.path(raw, "data_test.csv"))
stopifnot(!anyDuplicated(t$ResponseId))
t <- t[, .(src = ResponseId, cov_age = suppressWarnings(as.integer(sub("80+", "80", age, fixed = TRUE))),
           cov_female = fifelse(gender == "Woman", 1L, fifelse(gender == "Man", 0L, NA_integer_)),
           cov_postsec_education = as.integer(ed_postsec), cov_income_quintile = as.integer(income_quintile),
           cov_citizen = fifelse(citizen == "Yes", 1L, fifelse(citizen == "No", 0L, NA_integer_)))]
d <- merge(d, t, by = "src", all.x = TRUE, sort = FALSE)
d[, id := as.integer(factor(src, levels = unique(s$ResponseId)))][, src := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
stopifnot(uniqueN(d$id) == 45724, nrow(d) == 548688, d[, uniqueN(cov_country), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wimmer_2024_rivalry_immigrants.csv"))
