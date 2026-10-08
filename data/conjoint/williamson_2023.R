##Muslim preacher conjoint (11 Middle East / North Africa countries) from
##Williamson, S., Yildirim, A. K., Grewal, S., & Kuenkler, M. (2023). Preaching politics: How
##politicization undermines religious authority in the Middle East. British Journal of Political
##Science, 53(2), 555-574. https://doi.org/10.1017/S000712342200028X
##Replication data: Harvard Dataverse doi:10.7910/DVN/PUOUD4, CC0 1.0. File read:
##religion_conjoint_reshaped.rds (authors' long file, one row per respondent x profile). README.txt
##and Politicization_Islam_Replication.R read as text (not run). No codebook or questionnaire ships;
##outcome wording is from the article (open access, CC BY 4.0).
##Usage: Rscript williamson_2023.R <dir holding the .rds> <output dir>
##
##YouGov online panel, December 2017 (Turkey by a partner vendor): 14,466 respondents in Morocco,
##Tunisia, Egypt, Jordan, Lebanon, Turkey, Kuwait, Qatar, UAE, Bahrain, Saudi Arabia (plus one in
##Libya). The authors analyse only Sunni (incl. Salafi) respondents: 12,025, which is the article's
##N; everyone is kept here and cov_sect lets users apply that filter. The authors pool the
##countries in one analysis (country fixed effects in a robustness model), so one table with
##cov_country.
##2 tasks x 2 hypothetical preachers, 9 attributes ("fully randomized without restrictions",
##article). The file's `variable` 1-4 is task 1 preacher 1, task 1 preacher 2, task 2 preacher 3,
##task 2 preacher 4: checked, since each row's rating is the q21a/q22a grid item of that preacher
##and the authors' binary_trust equals "chose that preacher" on q21/q22 (every task has exactly one).
##Attribute text is the authors' English labels (the survey was not in English; the deposit's
##piped-text column is mojibake). Nationality "$q_country" was the respondent's own country,
##"automatically piped into the survey" (article): stored as the respondent's country of residence
##(English name). Saudi respondents never see the "Saudi Arabia" foreign level (their home country
##is Saudi Arabia), so the nationality level set depends on country (restrictions = yes).
##The q21_p*/q22_p* "*_codes" arrays are not documented and are dropped (cjt_* columns used).
##Outcomes (article wording):
##  choice: "Who would you personally trust more as an authority on religious matters?" forced.
##  choice_listen: "If you could only listen to a sermon by one of these preachers, which one would
##    you choose to listen to?" forced.
##  rating: "How much would you personally trust each of the preachers above as an authority on
##    religious matters?" Stored 0-4 as the authors code the answer text: 0 Not trust at all, 1 A
##    little, 2 Somewhat, 3 A lot, 4 Completely trust (higher = more trust).
##Covariates (answer text as stored): cov_gender ("Female"/"Male" -> female/male), cov_education
##(edu_level; "None of these" kept), cov_country (residence_country), cov_sect, cov_religion,
##cov_employment, cov_income, cov_maritalstatus, cov_householdsize, cov_industry, cov_jobtype,
##cov_mosque, cov_religious, cov_corruption, cov_gov_perform, cov_sharia_support,
##cov_political_ideology, cov_religious_influence, cov_terrorism_support; numeric as stored:
##cov_pray, cov_quran, cov_halaqa (no labels in deposit). Dropped: authors' derived dummies
##(islamist, critic, terror_never, college, men, rlgs, rlgn_pca, sums), the empty registered_with_gov
##columns, the code arrays. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(as.data.frame(readRDS(file.path(raw, "religion_conjoint_reshaped.rds"))))
x[, v := as.integer(as.character(variable))]
stopifnot(x[, .N, id][, all(N == 4)], uniqueN(x$id) == 14466, all(x$v %in% 1:4))
x[, task := (v + 1L) %/% 2L][, profile := 2L - v %% 2L]
pick <- function(q, task) as.integer(sub("Preacher ", "", q)) - 2L * (task - 1L)
x[, ch1 := fifelse(task == 1, pick(q21_q21_1_q21_grid, 1L), pick(q22_q22_1_q22_grid, 2L))]
x[, ch2 := fifelse(task == 1, pick(q21_q21_2_q21_grid, 1L), pick(q22_q22_2_q22_grid, 2L))]
stopifnot(all(x$ch1 %in% 1:2), all(x$ch2 %in% 1:2))
tr <- c("Not trust at all" = 0L, "A little" = 1L, "Somewhat" = 2L, "A lot" = 3L, "Completely trust" = 4L)
rtxt <- x[, fcase(v == 1, q21a_q21a_1_q21a_grid, v == 2, q21a_q21a_2_q21a_grid, v == 3, q22a_q22a_1_q22a_grid, v == 4, q22a_q22a_2_q22a_grid)]
stopifnot(all(rtxt == x$trust), all(x$trust %in% names(tr)))
d <- x[, .(id = as.integer(id), task, profile, choice = as.integer(ch1 == profile), choice_listen = as.integer(ch2 == profile),
           rating = tr[trust],
           attr_age = as.character(cjt_age), attr_education = cjt_education,
           attr_nationality = fifelse(cjt_nationality == "$q_country", residence_country, cjt_nationality),
           attr_hafiz = cjt_hafiz, attr_location = cjt_location, attr_followers = cjt_followers,
           attr_ideology = cjt_ideology, attr_usa = cjt_usa, attr_politics = cjt_politics,
           cov_gender = c(Female = "female", Male = "male")[gender], cov_education = edu_level, cov_country = residence_country,
           cov_sect = sect, cov_religion = religion, cov_employment = employment, cov_income = income,
           cov_maritalstatus = maritalstatus, cov_householdsize = householdsize, cov_industry = industry, cov_jobtype = jobtype,
           cov_pray = pray, cov_mosque = mosque, cov_quran = quran, cov_halaqa = halaqa, cov_religious = religious,
           cov_corruption = corruption, cov_gov_perform = gov_perform, cov_sharia_support = sharia_support,
           cov_political_ideology = political_ideology, cov_religious_influence = religious_influence,
           cov_terrorism_support = terrorism_support)]
stopifnot(all(d$choice == x$binary_trust), all(d$choice_listen == x$binary_prefer))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, sum(choice_listen), .(id, task)][, all(V1 == 1)])
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), !anyNA(d$cov_gender))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "williamson_2023_preacher_authority.csv"))
