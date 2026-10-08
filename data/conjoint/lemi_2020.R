##Multiracial candidate conjoint (US) from
##Lemi, D. C. (2021). Do voters prefer just any descriptive representative? The case of multiracial
##candidates. Perspectives on Politics, 19(4), 1061-1081 (online 2020; corrigendum
##doi:10.1017/S1537592720004338 not read). https://doi.org/10.1017/S1537592720001280
##Replication data: Harvard Dataverse doi:10.7910/DVN/E7CLML, CC0 1.0. File read:
##Lemi_PoP_Do_Voters_Prefer_Just_Any_Final.tab ("original format" csv: the author's long file made
##with cjoint::read.qualtrics, one row per respondent x task x profile, after her exclusions).
##Lemi_PoP_Do_Voters Prefer_Just_Any_Descriptive_Representative.do read as text (not run): it gives
##the questionnaire wording and answer codes of the covariates and the attribute labels. No
##questionnaire for the conjoint itself ships and the article was not accessible, so the outcome
##wording is a paraphrase.
##Usage: Rscript lemi_2020.R <dir holding the csv saved as data.csv> <output dir>
##
##786 White, Black, Asian and Hispanic US respondents (Qualtrics online panel, May 2016; the
##abstract's N), after the author's exclusions (no consent, not a good complete, no data-use
##permission, unfinished, one non-US resident, other races and multiracial respondents).
##10 tasks x 2 candidate profiles, 6 attributes: race (10 levels: 4 single and 6 two-race
##combinations), gender, party, ideology, nativity, political experience; text as stored (the
##author's do-file labels the same strings). Attribute order randomized once per respondent and
##recorded (*rowpos, constant within respondent): attrpos_.
##  choice: which of the two candidates the respondent would vote for (paraphrase; `selected`).
##  Forced choice. 6 tasks (3 respondents) have no answer and are omitted.
##Covariates (do-file questionnaire labels): cov_age (Q2 "What is your age?", years; one answer of
##1983 is a birth year, set to 33 as in the do-file), cov_gender (Q3 "Are you male or female?":
##1 Male, 2 Female), cov_english_first (Q4: Yes/No), cov_education (Q5 answer text), cov_income
##(Q6 answer text), cov_party_id (Q11 answer text: Democrat, Republican, Independent, Something
##else), cov_ideology (Q15 answer text; "Not Sure" kept), cov_race (Q7, single group by
##construction: White, Black/African American, Hispanic/Latino, Asian or Pacific Islander),
##cov_state_code (Q8 code, do-file lists the states). Dropped: Qualtrics response ids (re-keyed),
##timestamps, consent/permission fields, linked-fate and group-identity items, region dummies.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.csv"))
stopifnot(uniqueN(x$respondent) == 786, x[, .N, respondent][, all(N == 20)])
x[, id := match(respondent, sort(unique(respondent)))]
x <- x[!is.na(selected)]
d <- x[, .(id, task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_race = race, attrpos_race = racerowpos, attr_gender = gender, attrpos_gender = genderrowpos,
           attr_party = party, attrpos_party = partyrowpos, attr_ideology = ideology, attrpos_ideology = ideologyrowpos,
           attr_nativity = nativity, attrpos_nativity = nativityrowpos, attr_experience = experience,
           attrpos_experience = experiencerowpos)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 15720 - 12)
ed <- c("Less than High School", "High School / GED", "Some College", "2-year College Degree", "4-year College Degree",
        "Masters Degree", "Doctoral Degree", "Professional Degree (JD, MD)")
inc <- c("Less than 30,000", "30,000 – 39,999", "40,000 – 49,999", "50,000 – 59,999", "60,000 – 69,999",
         "70,000 – 79,999", "80,000 – 89,999", "90,000 – 99,999", "100,000 or more")
ideo <- c("1" = "Very liberal", "9" = "Liberal", "10" = "Moderate/Middle-of-the-Road", "11" = "Conservative",
          "12" = "Very conservative", "13" = "Not Sure")
r <- unique(x[, .(id, q2, q3, q4, q5, q6, q8, q11, q15, white, black, hispanic, asian)])
stopifnot(nrow(r) == 786, all(r$white + r$black + r$hispanic + r$asian == 1), all(r$q3 %in% 1:2), all(r$q15 %in% as.integer(names(ideo))))
cv <- r[, .(id, cov_age = fifelse(q2 == 1983L, 2016L - q2, q2), cov_gender = c("male", "female")[q3],
            cov_english_first = c("Yes", "No")[q4], cov_education = ed[q5], cov_income = inc[q6],
            cov_party_id = c("Democrat", "Republican", "Independent", "Something else")[q11],
            cov_ideology = ideo[as.character(q15)],
            cov_race = fcase(white == 1, "White", black == 1, "Black/African American", hispanic == 1, "Hispanic/Latino",
                             asian == 1, "Asian or Pacific Islander"),
            cov_state_code = q8)]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lemi_2020_multiracial_candidates.csv"))
