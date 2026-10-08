##Refugee-visa conjoint (climate vs political vs economic migrants, US) from
##Adman, P., Lajevardi, N., & Seligsohn, D. (2024). American attitudes toward climate migrants:
##Findings from a conjoint experiment. PS: Political Science & Politics, 57(4).
##https://doi.org/10.1017/S1049096524000258
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZH5LE9, CC0 1.0, no restricted files.
##File read: conjointdata.Rdata (object conjointdata, long: respondent x choiceNum x profileNum,
##attribute level text, Y1, Y2, preference, preference_int, the authors' respondent dummies).
##The authors' "Conjoint Data Analysis.R" and "Stata Data Analysis.do" were read as text (not run).
##conjointdata_final.dta (the open-ended-response analysis file) was downloaded only to check
##labels: it has none and holds IP address, latitude/longitude, MTurkCode and zip (PII); not used.
##Usage: Rscript adman_2024.R <dir holding conjointdata.Rdata> <output dir>
##
##1,117 US adults (Bovitz, September 2022; article "Our 1,117 respondents evaluated five pairs of
##profiles each"), 5 paired tasks each (task = choiceNum, profile = profileNum, both recorded),
##11,170 rows. The article also reports 5,175 profile pairs, which does not equal 1,117 x 5 = 5,585
##(the count in the deposit): flagged, not resolved.
##Outcomes (wording from the article): choice = "Which refugee should receive the visa?" (Y1);
##choice_integrate = "In your opinion, which refugee would be more likely to integrate successfully
##after arriving in the United States?" (Y2). Both forced choice between Refugee 1 and Refugee 2,
##exactly one chosen per task (checked); Y1 equals the deposit's `preference` (profile number chosen).
##No opt-out.
##7 attributes (level text as in the deposit, surrounding spaces trimmed): origin, refugee_cause
##(the long text; the deposit's `Refugee Cause` is a short recode), children, language_skills,
##gender, age, religion ("Unknown" is a displayed level). The article says the attributes were
##randomly varied; nothing on probabilities, restrictions or attribute order.
##Covariates: cov_gender from the authors' respondent dummies female/male (female == 1 -> "female",
##male == 1 -> "male", neither (21 respondents) -> NA; the raw QID67 codes have no labels);
##cov_birth_year (QID68_TEXT); cov_age (the authors' resp_age, = 2022 - birth year, checked).
##Dropped: Qualtrics response IDs (re-keyed to 1..N in source order), the unlabeled QID survey
##codes, and the authors' derived dummies (race, party, education, income, anxiety, etc.).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "conjointdata.Rdata"), envir = e)
k <- as.data.table(e$conjointdata)
at <- c("origin", "refugee_cause", "children", "language_skills", "gender", "age", "religion")
d <- k[, .(rid = X_recordId, task = as.integer(choiceNum), profile = as.integer(profileNum),
           choice = as.integer(Y1), choice_integrate = as.integer(Y2))]
for (v in at) set(d, j = paste0("attr_", v), value = trimws(k[[v]]))
stopifnot(d[, !anyNA(.SD)], all(k$preference == ifelse(k$Y1 == 1, k$profileNum, 3 - as.integer(k$profileNum))))
stopifnot(d[, .(sum(choice), sum(choice_integrate), .N), by = .(rid, task)][, all(V1 == 1 & V2 == 1 & N == 2)])
stopifnot(all(k$QID68_TEXT + k$resp_age == 2022, na.rm = TRUE), !any(k$female == 1 & k$male == 1))
d[, `:=`(cov_gender = fifelse(k$female == 1, "female", fifelse(k$male == 1, "male", NA_character_)),
         cov_birth_year = as.integer(k$QID68_TEXT), cov_age = as.integer(k$resp_age))]
d[, id := match(rid, unique(rid))][, rid := NULL]
stopifnot(uniqueN(d$id) == 1117, nrow(d) == 11170)
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "adman_2024_climate_refugees.csv"))
