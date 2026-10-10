##Latino "Americanness" paired conjoint from
##Ocampo-Roland, A. N. (2025). Group prototypicality and boundary definition: Comparing White and
##Black perceptions of whether Latinos are American. American Political Science Review, 119(4), 1581-1598.
##https://doi.org/10.1017/S000305542400131X
##Replication data: Harvard Dataverse doi:10.7910/DVN/CXT4YN, CC0 1.0. Files read:
##1_raw_data_for_long.csv (Dataverse original; one row per respondent), with level text from
##questionnaire.pdf (Table A1, "Full list of conjoint experimental characteristics") and the code
##numbers from codebook.pdf p. 9-12 / 2_cleaning_long_form_data.R (read as text, not run).
##Usage: Rscript ocampo_2025.R <dir holding the csv> <output dir>
##
##1,500 US adults (2020 "Survey of Political Opinion"; 750 White and 750 Black respondents, the
##two groups the paper compares; pooled in one table with cov_race, as the paper's Figure 1 AMCE
##pools all respondents), 5 tasks of 2 profiles of "individuals living in the U.S." who "are either
##immigrants or come from a family with a history of immigration", 9 attributes. Task and profile
##are recorded (Q3A..Q3E = tasks 1-5 in the order of the authors' cj_tidy reshape; _1/_2 = left/right).
##Outcomes (questionnaire B.2):
##  choice = Q3_2/Q3_5/Q3_8/Q3_11/Q3_14 (1 = left, 2 = right): "If you had to choose between them,
##           which of them do you personally believe is more American?" Forced choice, no opt-out.
##  rating = Q3_3_1/_2 ... Q3_15_1/_2: "On a scale from 1 to 7, where 1 indicates that you would not
##           rate this person as American at all and 7 indicates that you would very much rate this
##           person as American, how would you rate each person?" 1-7, 7 = most American. 21 ratings
##           coded 998 (skipped) are NA, as in the authors' cleaning; the choice is kept.
##The questionnaire also lists a 1-7 "want this person to be your friend" rating; it is not in the
##deposit ("Replication data only includes variables that were used in the analyses").
##Attribute text: the questionnaire's Table A1 wording (codes matched to it through the codebook's
##short labels), except
##  attr_faces: shown only as a photograph (questionnaire Figure A2); stored as the authors' coding
##    of the photo (codebook: White/Light/Medium/Brown/Black x man/woman);
##  attr_identifies code 2 "Latino": in the codebook and code but missing from questionnaire Table A1
##    (which lists six levels); stored as "Latino";
##  attr_spouse code 5: stored as Table A1's "Spouse is (same identity as profile)"; the text
##    respondents saw presumably named the identity, which is not recorded.
##Restrictions and level weights (authors' 3_amce_and_marginal_means_by_race.R, cjoint makeDesign):
##no Doctor/IT/Teacher with a high-school-or-less education, no Doctor with a Bachelor's degree, no
##US-born profile with "Does not speak English", no immigrant/naturalized profile with "Only speaks
##English", no IT/Doctor/Sales manager/Teacher with "Does not speak English", no White/Light/Medium
##face identifying as Black, no Brown/Black face identifying as White. Party drawn 2/9 each and 3/9
##"Not political"; spouse 5/15 not married, 3/15 American, 2/15 Black, 2/15 White, 3/15 same.
##Attribute order not documented. The authors' AMCEs use the survey weight. Spot check: a weighted
##lm of (rating-1)/6 within the languages allowed for every background gives background AMCEs of
##-0.036/-0.195/-0.018/-0.042 (legal/undocumented immigrant, naturalized, US-born undoc. parents)
##against the paper's Table A5 -0.04/-0.21/-0.02/-0.05 (cjoint with the constraint design).
##Covariates: cov_survey_weight (weight; codebook "Survey weight"), cov_race (race: White/Black
##respondent, codebook), cov_gender (gender 1 Male / 2 Female, codebook), cov_education (educ,
##codebook text), cov_party_id7 (pid7, codebook text, "Not sure" kept as answer text),
##cov_birth_year (birthyr). Kept as source codes (labels in codebook.pdf): cov_employ, cov_faminc_new
##(97 = prefer not to say), cov_religpew (98 skipped), cov_ideo5, cov_presvote16post, cov_votereg,
##cov_q7_2/cov_q7_3/cov_q7_4 (importance of American identity / racial identity / feels typical
##American, 1-4, 8 skipped), cov_q4_3 (born in US), cov_q4_5_2 (parents' birthplace). caseid is a
##panel case number: re-keyed to 1..1500 in file order. The authors' derived splits (*_high,
##rating_r) are dropped. Count check: 1,500 respondents x 5 x 2 = 15,000 rows = the authors'
##3_long_data_for_analysis.csv; choices and ratings match it row for row (checked when built).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- fread(file.path(raw, "1_raw_data_for_long.csv"))
stopifnot(nrow(f) == 1500, uniqueN(f$caseid) == 1500)
f[, rid := .I]
lab <- list(
  Faces = c("White man", "White woman", "Light man", "Light woman", "Medium man", "Medium woman",
            "Brown man", "Brown woman", "Black man", "Black woman"),
  Background = c("Legal immigrant", "Undocumented immigrant", "Naturalized citizen",
                 "Born in U.S.; parents were legal immigrants", "Born in U.S.; parents were undocumented immigrants",
                 "Born in U.S.; grandparents were legal immigrants", "Born in U.S.; grandparents were undocumented immigrants"),
  Identifies = c("American", "Latino", "Hispanic", "Mexican-American", "Mexican", "White", "Black"),
  Language = c("Only speaks English", "Bilingual", "Speaks limited English", "Does not speak English"),
  Education = c("Dropped out of high school", "High school graduate", "Bachelor’s degree", "Advanced/graduate degree"),
  Profession = c("Waiter", "Janitor", "Sales manager", "Teacher", "IT Professional", "Doctor", "Small business owner"),
  Religion = c("Presbyterian", "Evangelical", "Catholic", "Not religious"),
  Political = c("Democrat", "Republican", "Independent", "Not political"),
  Spouse = c("Not married", "Spouse is American", "Spouse is Black", "Spouse is White", "Spouse is (same identity as profile)"))
chq <- c("Q3_2", "Q3_5", "Q3_8", "Q3_11", "Q3_14"); rtq <- c("Q3_3", "Q3_6", "Q3_9", "Q3_12", "Q3_15")
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(rid = f$rid, task = t, profile = p,
                  choice = as.integer(f[[chq[t]]] == p), rating = as.integer(f[[paste0(rtq[t], "_", p)]]))
  for (v in names(lab)) {
    code <- f[[paste0("Q3", LETTERS[t], "_", p, "_", v)]]
    stopifnot(all(code %in% seq_along(lab[[v]])))
    x[, paste0("attr_", tolower(v)) := lab[[v]][code]]
  }
  x
}))))
stopifnot(all(d$rating %in% c(1:7, 998L)), sum(d$rating == 998L) == 21)
d[rating == 998L, rating := NA_integer_]
stopifnot(!anyNA(d$choice), d[, sum(choice), .(rid, task)][, all(V1 == 1)])
cv <- f[, .(rid, cov_survey_weight = weight, cov_race = c("White respondent", "Black respondent")[race],
            cov_gender = c("male", "female")[gender],
            cov_education = c("No high school diploma", "High school graduate", "Some college", "2-year college degree",
                              "4-year college degree", "Post-grad education")[educ],
            cov_party_id7 = c("Strong Democrat", "Not very strong Democrat", "Lean Democrat", "Independent",
                              "Lean Republican", "Not very strong Republican", "Strong republican", "Not sure")[pid7],
            cov_birth_year = birthyr, cov_employ = employ, cov_faminc_new = faminc_new, cov_religpew = religpew,
            cov_ideo5 = ideo5, cov_presvote16post = presvote16post, cov_votereg = votereg,
            cov_q7_2 = Q7_2, cov_q7_3 = Q7_3, cov_q7_4 = Q7_4, cov_q4_3 = Q4_3, cov_q4_5_2 = Q4_5_2)]
stopifnot(!anyNA(cv$cov_race), !anyNA(cv$cov_gender), !anyNA(cv$cov_education), !anyNA(cv$cov_party_id7))
d <- merge(d, cv, by = "rid")
setnames(d, "rid", "id")
setorder(d, id, task, profile)
stopifnot(nrow(d) == 15000)
fwrite(d, file.path(out, "ocampo_2025_latinos_american.csv"))
