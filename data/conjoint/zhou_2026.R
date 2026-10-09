##Zainichi Korean job-applicant conjoint (Japan), Studies 1 and 2, from
##Zhou, K., & Horiuchi, Y. (2026). Disclosing invisible attributes leads to discrimination.
##Journal of Race, Ethnicity, and Politics, 1-26. https://doi.org/10.1017/rep.2026.10062
##Replication data: Harvard Dataverse doi:10.7910/DVN/59MTHA, CC0 1.0, no restricted files.
##Files read: study1_survey.tab and study2_survey.tab as their original Qualtrics CSV exports
##(read here as study1_survey.csv, study2_survey.csv). Read as text, not run: README.md,
##functions/wrangle_data.R, reshape_conjoint.R, read_Qualtrics.R, expand_profile_data.R,
##scripts/study1.R, study1_questionnaire.docx, study2_questionnaire.docx (Qualtrics exports with
##the Japanese text shown and an English translation), accepted_version.pdf (article).
##irt_pretest_survey (an item pretest, not a conjoint) is not used.
##Usage: Rscript zhou_2026.R <raw dir> <output dir>
##
##TWO TABLES, one per study (separate samples and fieldings; the article analyses them
##separately, pooled only in an appendix figure):
##  zhou_2026_zainichi_hiring_s1: Study 1, national PureSpectrum sample of Japanese citizens,
##    May 16-17 2023, 1,002 complete respondents (article: "approximately 1,000 valid").
##  zhou_2026_zainichi_hiring_s2: Study 2, Kansai-region PureSpectrum sample (respondents outside
##    Kansai screened out), February 14-23 2024, 1,001 complete respondents.
##Respondents kept: complete == 1, as in the authors' wrangle_data.R (excludes non-consent,
##non-citizens, failed screener and, in Study 2, non-Kansai).
##Design (article Section 4.1, Table 1; questionnaires). Pairs of hypothetical applicants, 4
##attributes in a fixed table (row order 名前 name, 学歴 education, 実務経験 experience,
##一次選考の結果 preliminary screening result), Japanese text as displayed:
##  attr_name: 10 names (6 Japanese names, 2 Korean names, 2 Japanese pseudonyms of Zainichi
##    Koreans; half male, half female; names carry ethnicity and gender, which respondents were
##    not told explicitly). Authors' coding (wrangle_data.R): Japanese for Japanese = 前田颯太,
##    斎藤拓也, 田中海斗 (male), 山口明日香, 竹内里奈, 青木遥 (female); Japanese for Zainichi =
##    金田翔太 (male), 張本美咲 (female); Korean for Zainichi = 金智勳 (male), 朴恩智 (female).
##  attr_education: 東京大学, 早稲田大学, 日本大学, 千葉大学
##  attr_experience: 3年, 5年, 7年
##  attr_screening: 優秀 (Excellent), 特に優秀 (Particularly Excellent)
##"All names were assigned equal weight" and other levels equal weight "with no cross-attribute
##constraints" (article). OBSERVED restriction: the two applicants in a pair never share a name
##(0 of 20,040 pairs per study; about 10% would if independent), so names are drawn without
##repetition within a pair.
##Tasks. Each respondent did two sets of 8 tasks, in randomized set order (NOT recorded): a
##private company R&D position (trial_job = "private company") and a public elementary school
##teacher (trial_job = "public school"). Qualtrics drew 7 pairs per respondent (embedded data
##name-<pair>-<applicant> etc.) and BOTH sets show the same 7 pairs (trial_pair = that pair
##number), in this order (questionnaire block order):
##  private company, tasks 1-8: Q11.2-Q17.2 = pairs 1-7, then Q26.2 = pair 1 again
##    (trial_repeat_of = 1 on task 8);
##  public school, tasks 9-16: Q20.2 = pair 2, Q19.2 = pair 1, Q21.2-Q25.2 = pairs 3-7, then Q557
##    = pair 2 again (trial_repeat_of = 9 on task 16).
##Repeated tasks show the profiles in the same positions (not swapped). Task numbers give the
##order within a set; because set order is not recorded, task 9 may have preceded task 1.
##Embedded pairs 8-10 were generated but never shown and are not kept.
##Outcome: choice = forced choice. 仮に、以下の二人の応募者が最終選考に残ったと想定してください。
##あなたはどちらの応募者を採用すべきだと思いますか。... どちらを採用すべきだと思いますか。
##(English in the questionnaire: "Suppose that the following two candidates remain in the final
##selection process. ... Which applicant do you think should be hired?") 応募者１/応募者２
##(exported as "Applicant 1"/"Applicant 2"). No opt-out.
##Covariates (answer text as exported, in English): cov_age (Q9.2, years), cov_gender (Q9.4
##Male/Female -> male/female), cov_prefecture (Q9.3), cov_education (Q9.5), cov_income (Q9.6,
##household), cov_leftright (Q8.3), cov_party_id (Q8.4 "Putting aside which party you will vote
##for in the next election, which party do you usually support?"), cov_party_strength (Q8.5),
##cov_party_preferred (Q8.6), cov_life_satisfaction (Q8.1), cov_life_change (Q8.2),
##cov_nationalism_1..3 (Q5.1-Q7.1), cov_zainichi_discrimination (Q29.1), cov_zainichi_leave
##(Q30.1), cov_zainichi_untrusted (Q31.1), cov_zainichi_ethnic_names (Q32.1),
##cov_zainichi_chima_chogori (Q33.1), cov_zainichi_hate_crimes (Q34.1), cov_zainichi_effort
##(Q35.1); Study 2 also cov_contact_1..4 (contact1-contact4, the article's social-contact items);
##cov_duration_sec (whole survey). Blank answers -> NA.
##Dropped: Qualtrics ResponseId and the panel transaction_id (platform IDs; id re-keyed 1..N in
##file order), free text (Q27.1 thoughts about Zainichi Koreans, Q36.1 comments), timers,
##consent/citizenship/screener items (constant after the filter), panel fields (st, survey_id,
##supplier_id, term, main_launch / pre-test2, region). No survey weight.
##Spot check: over the non-repeated tasks, the Japanese-named Japanese applicant is chosen in
##0.62 of pairs against a Korean-named Zainichi applicant and 0.54 against a Zainichi applicant
##with a Japanese pseudonym (Study 1), exactly the article's Figure 2 marginal means (Study 2:
##0.61 and 0.53).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
na <- function(x) fifelse(x == "", NA_character_, x)
build <- function(study) {
  s <- fread(file.path(raw, paste0(study, "_survey.csv")), colClasses = "character", encoding = "UTF-8")
  s <- s[complete == "1"]
  s[, id := seq_len(.N)]
  plan <- data.table(q = c(sprintf("Q%d.2", 11:17), "Q26.2", "Q20.2", "Q19.2", sprintf("Q%d.2", 21:25), "Q557"),
                     task = 1:16, pair = c(1:7, 1, 2, 1, 3:7, 2),
                     job = rep(c("private company", "public school"), each = 8),
                     rep = c(rep(NA, 7), 1L, rep(NA, 7), 9L))
  d <- rbindlist(lapply(seq_len(nrow(plan)), function(i) {
    p <- plan[i]; ans <- s[[p$q]]
    stopifnot(all(ans %in% c("Applicant 1", "Applicant 2")))
    rbindlist(lapply(1:2, function(k) {
      x <- data.table(id = s$id, task = p$task, profile = k, choice = as.integer(ans == paste("Applicant", k)))
      for (v in c("name", "education", "experience", "screening"))
        x[, paste0("attr_", v) := s[[sprintf("%s-%d-%d", v, p$pair, k)]]]
      x[, `:=`(trial_job = p$job, trial_pair = p$pair, trial_repeat_of = as.integer(p$rep))]
    }))
  }))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, !"trial_repeat_of"]), all(d$attr_name != ""))
  stopifnot(uniqueN(d$attr_name) == 10, uniqueN(d$attr_education) == 4, uniqueN(d$attr_experience) == 3,
            uniqueN(d$attr_screening) == 2)
  stopifnot(all(s$Q9.4 %in% c("Male", "Female")))
  cv <- s[, .(id, cov_age = as.integer(Q9.2), cov_gender = c(Male = "male", Female = "female")[Q9.4],
              cov_prefecture = na(Q9.3), cov_education = na(Q9.5), cov_income = na(Q9.6), cov_leftright = na(Q8.3),
              cov_party_id = na(Q8.4), cov_party_strength = na(Q8.5), cov_party_preferred = na(Q8.6),
              cov_life_satisfaction = na(Q8.1), cov_life_change = na(Q8.2),
              cov_nationalism_1 = na(Q5.1), cov_nationalism_2 = na(Q6.1), cov_nationalism_3 = na(Q7.1),
              cov_zainichi_discrimination = na(Q29.1), cov_zainichi_leave = na(Q30.1), cov_zainichi_untrusted = na(Q31.1),
              cov_zainichi_ethnic_names = na(Q32.1), cov_zainichi_chima_chogori = na(Q33.1),
              cov_zainichi_hate_crimes = na(Q34.1), cov_zainichi_effort = na(Q35.1),
              cov_duration_sec = as.integer(`Duration (in seconds)`))]
  if (study == "study2") cv[, paste0("cov_contact_", 1:4) := lapply(paste0("contact", 1:4), function(v) na(s[[v]]))]
  d <- merge(d, cv, by = "id")
  setorder(d, id, task, profile)
  d
}
d1 <- build("study1"); stopifnot(uniqueN(d1$id) == 1002)
fwrite(d1, file.path(out, "zhou_2026_zainichi_hiring_s1.csv"))
d2 <- build("study2"); stopifnot(uniqueN(d2$id) == 1001)
fwrite(d2, file.path(out, "zhou_2026_zainichi_hiring_s2.csv"))
