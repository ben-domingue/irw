##Household-arrangement conjoint (US parents) from
##Hutchinson, A., Khan, S., & Matfess, H. (2023). Childcare, work, and household labor during a
##pandemic: Evidence on parents' preferences in the United States. Journal of Experimental
##Political Science, 10(2), 155-173. https://doi.org/10.1017/XPS.2022.24
##Replication data: Harvard Dataverse doi:10.7910/DVN/E6J9AS, CC0 1.0, no restricted files, no
##terms (deposit authors listed Khan, Hutchinson, Matfess). Files read: HKM_profiledata.csv (one
##row per profile; tab-separated), HKM_respondentdata.csv (one row per respondent). HKM_codebook.rtf
##and HKM_analyze.R read as text only.
##Usage: Rscript hutchinson_2023.R <raw dir> <output dir>
##
##1,938 US heterosexual parents (online sample, August 2020; provider not named in the deposit or
##the APSA summary), 4 tasks x 2 vignettes of a married couple with two children. profilenum
##(1-8, "nth profile shown", RECORDED) gives task = ceiling(profilenum / 2) and profile = 1 for odd,
##2 for even; exactly one profile per complete task is chosen (checked).
##Attributes (codebook names; the stored level is the phrase inserted into the vignette text,
##whose template is not in the deposit):
##  attr_childcare     Childcare Availability ("determined that there are no childcare options
##                     available" / "at least one childcare option available to them")
##  attr_wife_work     Wife's work status (not working and earns $0 / full time $50k / full time $100k a year)
##  attr_husband_work  Husband's work status (same three levels)
##  attr_chore_time    Time Division on Household Chores: the wife spends "much less time than" /
##                     "about the same time as" / "much more time than" the husband (codebook)
##  attr_husband_feminine_tasks  Husband's Contribution to Feminine Tasks (rarely / sometimes / regularly)
##No restrictions are documented; all 9 wife x husband work combinations occur at similar rates.
##Outcomes:
##  choice  profile1_chosen. The article: respondents chose which arrangement they would
##          personally prefer to be in (exact wording not in the deposit). Forced choice.
##  rating  "How FAIR do you think Couple A's/B's situation is?" 1 = Very unfair, 2 = Somewhat
##          unfair, 3 = Neither fair nor unfair, 4 = Somewhat fair, 5 = Very fair (the codebook says
##          "Extremely", the data and the authors' recode say "Very"); higher = fairer. The 4
##          profiles with no rating fall in dropped tasks.
##Dropped: 8 tasks (16 rows) where every attribute is the string "NA" (levels not saved), and 24
##tasks (48 rows) with no choice recorded (as the authors' na.omit); 3 respondents lose all
##tasks, leaving 1,935 respondents, 7,720 tasks. Respondent UUIDs re-keyed.
##Covariates (text as in the files): cov_gender (dem_gender, "Which gender do you identify
##with?", codebook options Male / Female / Other / Prefer not to say, lowercased to male /
##female / other, "Prefer not to say" = NA; the data hold only Male and Female), cov_age (years,
##age_consent), cov_employment, cov_party_id (pid, codebook "Generally speaking, do you think of
##yourself as a...": Republican / Democrat / Independent), cov_education (edu, codebook "What is
##the highest level of education you have received?", the codebook's 8 answer texts),
##cov_race, cov_household_income, cov_modern_sexism_1..4 (agreement with the four codebook
##statements, Strongly Agree .. Strongly Disagree). The deposit has no survey weight, attention
##check or duration (codebook, read.me.rtf). No repeated task (profilenum 1-8 all distinct).
##The files are read in Dataverse's archival tab-separated form (the default download); the
##?format=original CSVs are comma-separated with CR line ends and do not parse here.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
p <- fread(file.path(raw, "HKM_profiledata.csv"), na.strings = "")
r <- fread(file.path(raw, "HKM_respondentdata.csv"), na.strings = "")
stopifnot(p[, .N, rid][, all(N == 8)], !anyDuplicated(r$rid), setequal(p$rid, r$rid))
r[, id := .I]
p <- merge(p, r[, .(rid, id)], by = "rid")
p[, task := (profilenum + 1L) %/% 2L][, profile := 2L - profilenum %% 2L]
lv <- c("childcare_level", "contribution_level", "fearnings_level", "mearnings_level", "division_level")
p[, bad := Reduce(`|`, lapply(.SD, function(x) is.na(x) | x == "NA")), .SDcols = lv]
p[, drop := any(bad) | anyNA(profile1_chosen), .(id, task)]
stopifnot(p[bad == TRUE, all(childcare_level == "NA" & contribution_level == "NA" & fearnings_level == "NA" &
                             mearnings_level == "NA" & division_level == "NA")], p[bad == TRUE, .N] == 16)
p <- p[drop == FALSE]
fair <- c("Very unfair" = 1L, "Somewhat unfair" = 2L, "Neither fair nor unfair" = 3L, "Somewhat fair" = 4L, "Very fair" = 5L)
stopifnot(all(p$profile_fair %in% c(names(fair), "NA", NA)))
d <- p[, .(id, task, profile, choice = as.integer(profile1_chosen), rating = unname(fair[profile_fair]),
           attr_childcare = childcare_level, attr_wife_work = fearnings_level, attr_husband_work = mearnings_level,
           attr_chore_time = division_level, attr_husband_feminine_tasks = contribution_level)]
stopifnot(all(r$dem_gender %in% c("Male", "Female", "Other", "Prefer not to say", NA)))
r[, gender := c(Male = "male", Female = "female", Other = "other")[dem_gender]]
d <- merge(d, r[, .(id, cov_gender = gender, cov_age = as.integer(age_consent), cov_employment = employ, cov_party_id = pid,
                    cov_education = edu, cov_race = race, cov_household_income = income_house,
                    cov_modern_sexism_1 = modernsexism_1, cov_modern_sexism_2 = modernsexism_2,
                    cov_modern_sexism_3 = modernsexism_3, cov_modern_sexism_4 = modernsexism_4)], by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hutchinson_2023_household_arrangements.csv"))
