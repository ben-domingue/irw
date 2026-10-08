##Candidate choice conjoint on democratic positions (Poland) from
##Wunsch, N., Jacob, M. S., & Derksen, L. (2025). The demand side of democratic backsliding: How
##divergent understandings of democracy shape political choice. British Journal of Political
##Science, 55, e39. https://doi.org/10.1017/S0007123424000711
##Replication data: Harvard Dataverse doi:10.7910/DVN/AKYFQ3, CC0 1.0, no restricted files.
##Files read: cjoint_data.rds (choices), survey_data_subset.rds (covariates). codebook.pdf and
##02_recoding.R (read as text) document them. Level text, question wording and the example task
##are from the article's Supplementary Material (Table A.1, Figures A.1-A.2).
##Usage: Rscript wunsch_2025.R <raw dir> <output dir>
##
##Online sample of Polish adults (Inquiry/YouGov, 12 July - 12 August 2021; quotas on age,
##gender, region, 2020 vote). 2,910 respondents in cjoint_data (ids are already anonymous
##"respondent_NNNN"; re-keyed to integers), 12 tasks each of 2 candidates for the Sejm,
##7 attributes; task (`choice` 1-12) and profile (Candidate A/B) are recorded. Attribute order
##was randomized per task (not recorded). Profiles were fully randomized (article footnote 3: "We deliberately
##choose to fully randomize all candidate profiles"); only candidate gender has unequal level
##probabilities (SI Table A.1). No survey weight in the deposit. No task repeats an earlier pair. One respondent (source respondent_2592) has no
##attribute values and is dropped: 2,909 respondents.
##Outcomes (Polish instrument; English from the SI screenshot, my translation):
##  choice: "Na ktorego kandydata najprawdopodobniej zaglosowal(a)bys?" (Which candidate would you
##     most likely vote for?), Kandydat A / Kandydat B, forced, no opt-out.
##  rating: "Jak oceniasz profil kandydata A/B?" (How do you rate candidate A's/B's profile?),
##     1 = Zdecydowanie nie popieram (strongly disapprove) .. 7 = Zdecydowanie popieram
##     (strongly approve). (The codebook's "1 to 6" is wrong; the data run 1-7.)
##Attributes: respondents saw Polish; attr_ text is the authors' English from SI Table A.1:
##  gender Female/Male (weighted 35%/65%), age (integer 30-65 per SI; data 40-65), party (Law and
##  Justice (PiS), Civic Coalition (KO), Poland 2050, The Left, Confederation), tax reform,
##  abortion legislation, judicial appointments, role of public media (full sentences; the
##  "Lib:/Maj:/Auth:" prefixes in Table A.1 are the authors' annotations and are dropped).
##  Source codes -> text: tax_rich/tax_all/tax_less, abortion_lib/abortion_illib, judges_L/M/A,
##  media_L/M/A, as in Table A.1 order and 02_recoding.R.
##Covariates (survey_data_subset; 2,623 of the respondents, others blank): cov_age
##(2021 - birthyear, computed by the authors in 02_recoding.R L97; kept as their age variable),
##cov_birth_year (birthyear, as recorded), cov_gender (gender, codebook.pdf item 10: Male /
##Female -> male / female), cov_party_preference (Q103 "Party preference of the respondent",
##English labels as deposited; its options include "Would not support any of these", so it reads
##as party support / vote intention, not party identification, and keeps its name),
##cov_education (education_level2_pl_rc, codebook.pdf item 11: Primary/vocational,
##Secondary/Post-secondary, Higher; the deposit's "NA" (codebook "No response") -> NA; the only
##education variable deposited, already grouped by the authors), cov_income ("No response"
##kept as answer text), cov_financial_situation, cov_duration_sec (duration, codebook item 9
##"Duration of the survey response in minutes", x 60: whole-survey duration in seconds), and
##the authors' attention checks cov_attention_pass_1 (instructed-response item Q1_4, re-asked as
##Q2_4 and Q4_4 after a failure: 1 = "Radio" selected at any try, 02_recoding.R L105-108) and
##cov_attention_pass_2 (instructed "select Slightly important" grid Q101A_1-4: 1 = passed in
##any version shown, 02_recoding.R L109-114); their analysis keeps respondents passing either:
##1,979 in the main models after further dropping speeders and failing pre-experiment checks,
##SI B. Not kept: the age_group item,
##the understanding-of-democracy and benchmark items (Q102_*, Q117_*), raw attention-check answers.
##Hungary replication (hungary_choices.rds) is NOT built: it re-hosts two attributes of
##Wunsch & Gessler (2023, Democratization) and is not the full design.
##N: 2,910 in the deposit = the article's initial N = 2,910 (analytic 1,979).
##Covariates are blank for the 287 respondents not in survey_data_subset (2,622 matched).
##Spot check: the paper reports results as figures/IMCEs only; no number was reproduced. Rating
##AMCEs (lm, judges ref. cross-party consensus): government -0.23, ruling-party leader -0.35.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "cjoint_data.rds")))
v <- as.data.table(readRDS(file.path(raw, "survey_data_subset.rds")))
stopifnot(s[, .N, ResponseId][, all(N == 24)], s[, .N, .(ResponseId, choice)][, all(N == 2)])
s <- s[!is.na(attr_gender)]
stopifnot(uniqueN(s$ResponseId) == 2909, !anyNA(s[, .(attr_age, attr_party, attr_tax, attr_abortion, attr_judges, attr_media)]))
s[, id := as.integer(sub("respondent_", "", ResponseId))]
stopifnot(!anyNA(s$id), s[, uniqueN(id)] == s[, uniqueN(ResponseId)])
txt <- c(PiS = "Law and Justice (PiS)", KO = "Civic Coalition (KO)", `Polska 2050` = "Poland 2050", Lewica = "The Left",
         Konfederacja = "Confederation",
         tax_rich = "Tax reform should increase taxes for medium- and high-income households.",
         tax_all = "Tax reform should increase taxes for all households.",
         tax_less = "Tax reform should decrease taxes for low-income households.",
         abortion_lib = "Abortion legislation should grant greater freedom of choice to women.",
         abortion_illib = "Abortion legislation should protect the unborn child's life in all but exceptional circumstances.",
         judges_L = "Judges should be selected based on cross-party consensus.",
         judges_M = "Judges should be selected by the government.",
         judges_A = "Judges should be selected by the leader of the ruling party.",
         media_L = "The role of public media is to report independently on political developments.",
         media_M = "The role of public media is to justify government policy towards the wider public.",
         media_A = "The role of public media is to defend government policy against criticism.")
tr <- function(x) { stopifnot(all(x %in% names(txt))); unname(txt[x]) }
d <- s[, .(id, task = as.integer(choice), profile = match(profile, c("Candidate A", "Candidate B")),
           choice = as.integer(chosen), rating = as.integer(rating0),
           attr_gender, attr_age = as.character(attr_age), attr_party = tr(attr_party), attr_tax = tr(attr_tax),
           attr_abortion = tr(attr_abortion), attr_judges = tr(attr_judges), attr_media = tr(attr_media))]
stopifnot(!anyNA(d$profile), all(d$attr_gender %in% c("Female", "Male")), all(d$rating %in% 1:7),
          d[, sum(choice), .(id, task)][, all(V1 == 1)])
# covariates, keyed on the same anonymous ids
v[, ResponseId := as.character(ResponseId)]
stopifnot(!anyDuplicated(v$ResponseId))
cv <- v[, .(id = as.integer(sub("respondent_", "", ResponseId)),
            cov_age = 2021L - as.integer(as.character(birthyear)), cov_birth_year = as.integer(as.character(birthyear)), cov_gender = tolower(as.character(gender)),
            cov_party_preference = as.character(Q103), cov_education = as.character(education_level2_pl_rc),
            cov_income = as.character(income_PL_rc), cov_financial_situation = as.character(financial_situation_rc),
            cov_duration_sec = round(as.numeric(duration) * 60, 2),
            cov_attention_pass_1 = as.integer(Q1_4 %in% "Radio" | Q2_4 %in% "Radio" | Q4_4 %in% "Radio"),
            cov_attention_pass_2 = as.integer(Q101A_1 %in% "Slightly important" | Q101A_2 %in% "Slightly important" |
                                          Q101A_3 %in% "Slightly important" | Q101A_4 %in% "Slightly important"))]
stopifnot(all(cv$cov_gender %in% c("female", "male")), all(cv$cov_education %in% c("Primary/vocational", "Secondary/Post-secondary", "Higher", "NA")))
cv[cov_education == "NA", cov_education := NA]
cv[cov_income == "NA", cov_income := "No response"]
d <- merge(d, cv, by = "id", all.x = TRUE)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wunsch_2025_democratic_backsliding.csv"))
