##Democracy-vs-security society conjoint (Australia, Canada, UK) from
##Bordeleau, J.-N. (2024). Are people equally willing to trade different dimensions of democracy for
##material and physical security? (OSF project; the article is not yet published -- an EPSA 2025 paper and a uOttawa thesis chapter).
##Replication data: OSF project osf.io/vmbr9 (doi:10.17605/OSF.IO/VMBR9), CC BY 4.0 (node licence).
##Files read: cj_dem_data.csv. Read as text: Conjoint_Levels.docx, Questionnaire_Conjoint.docx
##(the preregistered questionnaire), Supplementary Material.pdf, code_cjdem.R.
##Usage: Rscript bordeleau_2024.R <dir holding cj_dem_data.csv> <output dir>
##
##3,033 Qualtrics panel respondents (quota samples, 28 Nov - 5 Dec 2024): Australia 1,005,
##Canada 1,002, United Kingdom 1,026 (Supplementary Table S1 gives the same Ns). One table with
##cov_country: the author pools the three samples in the main models (code_cjdem.R) and the
##attribute text is identical English in all three.
##Each respondent saw 3 pairs of hypothetical societies (Society A / Society B), 7 attributes with
##two levels each (economy, crime, elections, media, checks and balances [source `executive`],
##accountability [source `law`], free speech). Level text is the text stored per profile in the
##wide columns <attr><task>.<profile>; it differs in small ways from Conjoint_Levels.docx (e.g.
##"The prime minister can rule without constraints from parliament and courts.", "People can
##criticize ..."), and the stored text is kept. The questionnaire says "the dimensions will be
##randomized"; attribute order is not recorded.
##Outcomes (questionnaire Q17/Q18):
##  choice: which of the two societies "you consider to be the best one for you; that is, the
##    society in which you would be the most content" (conjoint<t> = 1/2). Forced choice.
##  rating: "rate each society on a range from 0 (very bad) to 10 (very good)" (rating<t>_<p>).
##Covariates: cov_age (years), cov_gender (Male/Female -> male/female; 8 missing), cov_education
##(codes 1-3 mapped to the answer text of the Supplementary Material p. 5 EDUCATION item, matching
##the author's ed.group), cov_ideology (0-10, 0 = left), cov_economic_condition and
##cov_crime_perception (the author's recodes as stored: Secure/Insecure; Low/Moderate/High),
##cov_party_id_code (PID; country-specific dropdown codes 1-6, 98, 99 with no labels in the
##deposit), cov_pid_strength_1..5 (PIDstrength._1.._5, as stored), cov_manipcheck_3..7
##(robustness_check._3.._7: the post-conjoint 0-10 "affects me" items; their order on the five
##dimensions is not documented), cov_survey_date (fielding date), cov_country.
##Dropped: Qualtrics ResponseId (re-keyed), derived dummies (female, age.*, lowed/ed/highered,
##*ideology, ideology.group, age.group, ed.group). No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "cj_dem_data.csv"))
stopifnot(nrow(s) == 3033, uniqueN(s$ResponseId) == 3033)
s[, id := .I]
edlab <- c("Secondary school or lower", "Further education (academic or vocational, including undergraduate studies)",
        "Higher education (professional degree, master's or doctorate)")
stopifnot(all(s$education %in% 1:3), s[, all(substr(edlab[education], 1, 7) == substr(`ed.group`, 1, 7))])
src <- c(economy = "economy", crime = "crime", elections = "elections", media = "media",
         checks_balances = "executive", accountability = "law", free_speech = "free_speech")
d <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = s$id, task = t, profile = p,
                  choice = as.integer(s[[paste0("conjoint", t)]] == p),
                  rating = as.integer(s[[paste0("rating", t, "_", p)]]))
  for (n in names(src)) x[, paste0("attr_", n) := s[[paste0(src[[n]], t, ".", p)]]]
  x
}))))
cv <- s[, .(id, cov_country = country, cov_age = as.integer(age),
            cov_gender = c(Male = "male", Female = "female")[gender], cov_education = edlab[education],
            cov_ideology = as.integer(ideology), cov_economic_condition = economic_condition,
            cov_crime_perception = crime_perception, cov_party_id_code = as.integer(PID),
            cov_pid_strength_1 = PIDstrength._1, cov_pid_strength_2 = PIDstrength._2, cov_pid_strength_3 = PIDstrength._3,
            cov_pid_strength_4 = PIDstrength._4, cov_pid_strength_5 = PIDstrength._5,
            cov_manipcheck_3 = robustness_check._3, cov_manipcheck_4 = robustness_check._4,
            cov_manipcheck_5 = robustness_check._5, cov_manipcheck_6 = robustness_check._6,
            cov_manipcheck_7 = robustness_check._7, cov_survey_date = as.character(date))]
d <- merge(d, cv, by = "id")
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""), uniqueN(d[[v]]) == 2)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 0:10))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bordeleau_2024_democracy_security.csv"))
