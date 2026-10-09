##Family-migration and migrant-admission conjoints from
##Ahlén, A., Borevi, K., Gschwind, L., Hultin Rosenberg, J., & Wejryd, J. (2026). Universalist
##attitudes to family migration in Germany, Italy and Sweden: A new 'opinion-policy gap'.
##European Union Politics. https://doi.org/10.1177/14651165261463044
##Replication data: Harvard Dataverse doi:10.7910/DVN/KQ1FZX, CC0 1.0 (README names Wejryd, Ahlén
##and Gschwind). File read: "Curated dataset for Universalist attitudes.tab" (Dataverse original
##.dta). The do-files (Figure 2.do, Figure 3.do, Appendix.do, Description of the sample.do) were read
##as text. The article and questionnaire were not available: question wording is paraphrased.
##Usage: Rscript ahlen_2026.R <dir holding curated.dta (the original .dta renamed)> <output dir>
##
##Online survey (Enkätfabriken), Feb-Mar 2024, 4,119 respondents: Germany 1,390, Italy 1,419,
##Sweden 1,310 (orderedcountry). The deposit holds two conjoints with different attribute sets,
##each 6 paired tasks, so two tables (one per experiment, countries pooled with cov_country as in
##the authors' main models, which pool all three countries in Figure 2):
##1. ahlen_2026_family_reunification (profilenumber 71-122 = survey tasks 7-12, renumbered 1-6):
##   profiles describe a fictitious RESIDENT family member who wants to bring a family member to
##   the country; 8 attributes (migration background, language skills, legal status, work, economic
##   resources, gender, religion, role of religion). The country of origin of the incoming family
##   member (India/Syria/Ukraine/USA) was fixed per respondent (constant over all 12 rows; the
##   paper's Appendix Figure A4 splits by it) -> trial_incoming_origin, English rendering of the
##   Swedish value labels Indien/Syrien/Ukraina/USA.
##   choice = famchosen ("Fictious family-member profile chosen in conjoint"): which resident
##   family member should be allowed family reunification (paraphrase from the Figure 2 axis title).
##   rating = famrating, 1-7 ("Rating of fictious family-member profile"); higher = more willing
##   (Figure 3.do calls respondents with mean rating < 4.25 "restrictive"); anchors not deposited.
##2. ahlen_2026_migrant_admission (profilenumber 11-62 = tasks 1-6): migrant profiles with 7
##   attributes (reason for migrating, education, work experience/demand, language, gender, role
##   of religion, religion-and-country combined); choice = migchosen ("Migrant profile chosen in
##   conjoint (for reference)"); not analysed in the article except an appendix figure.
##Levels are the deposit's English value labels of the authors' e_* recodes ("RECODE of f_*"; the
##f_* originals and the German/Italian/Swedish screen text are not deposited). Forced choice in
##both (exactly one chosen per task, checked).
##Covariates (value-label text): cov_gender (sex: Woman = 0 -> female, Man = 1 -> male),
##cov_age_group (agegrp, quota bands), cov_education (isced, ISCED band text: the only education
##variable deposited), cov_leftright (0-1 as deposited), cov_birth_origin (shortorigin), cov_citizen,
##cov_home, cov_occupation (shortoccupation), cov_country. Panel tokens re-keyed to integers.
##Dropped: equage, low_hi_ed (recodes), dates, the authors' diagnostics (fam_straight_chooser,
##numberofconflictingfamtasks, mean_fam_rating, srelfam), use (always 1). No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.dta$", full.names = TRUE); stopifnot(length(f) == 1)
x <- as.data.table(read_dta(f))
stopifnot(all(x$use == 1))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
ids <- sort(unique(x$token)); x[, id := match(token, ids)]
x[, `:=`(task0 = as.integer(profilenumber) %/% 10L, profile = as.integer(profilenumber) %% 10L)]
stopifnot(all(x$profile %in% 1:2), all(x$task0 %in% 1:12))
sx <- as.integer(zap_labels(x$sex)); stopifnot(all(sx %in% 0:1))
cv <- x[, .(cov_country = c("Germany", "Italy", "Sweden")[orderedcountry], cov_gender = c("female", "male")[sx + 1L],
            cov_age_group = lab(agegrp), cov_education = lab(isced), cov_leftright = as.numeric(leftright),
            cov_birth_origin = lab(shortorigin), cov_citizen = lab(citizen), cov_home = lab(home), cov_occupation = lab(shortoccupation))]
inc <- c(Indien = "India", Syrien = "Syria", Ukraina = "Ukraine", USA = "USA")
fam <- x[, c(.(id = id, task = task0 - 6L, profile = profile, choice = as.integer(famchosen), rating = as.integer(famrating),
               attr_migration_background = lab(e_famprofile_origin_), attr_language = lab(e_famprofile_language_),
               attr_legal_status = lab(e_famprofile_legal_status_), attr_work = lab(e_famprofile_work_),
               attr_economy = lab(e_famprofile_economy_), attr_gender = lab(e_famprofile_gender_),
               attr_religion = lab(e_famprofile_religion_), attr_religiosity = lab(e_famprofile_religiosity_),
               trial_incoming_origin = unname(inc[lab(e_famprofile_incoming_origin_)])), cv)][task >= 1]
mig <- x[, c(.(id = id, task = task0, profile = profile, choice = as.integer(migchosen),
               attr_reason = lab(e_migprofile_reason_), attr_education = lab(e_migprofile_education_),
               attr_work_experience = lab(e_migprofile_workexperience_), attr_language = lab(e_migprofile_language_),
               attr_gender = lab(e_migprofile_gender_), attr_religiosity = lab(e_migprofile_religiosity_),
               attr_religion_country = lab(e_migprofile_count_relig_)), cv)][task <= 6]
for (d in list(fam, mig)) {
  ac <- grep("^attr_", names(d), value = TRUE)
  stopifnot(!anyNA(d[, ..ac]), !anyNA(d$choice), d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
}
stopifnot(!anyNA(fam$trial_incoming_origin), fam[, uniqueN(trial_incoming_origin), id][, all(V1 == 1)], all(fam$rating %in% 1:7))
setorder(fam, id, task, profile); setorder(mig, id, task, profile)
fwrite(fam, file.path(out, "ahlen_2026_family_reunification.csv"))
fwrite(mig, file.path(out, "ahlen_2026_migrant_admission.csv"))
cat(nrow(fam), uniqueN(fam$id), nrow(mig), uniqueN(mig$id), "\n")
