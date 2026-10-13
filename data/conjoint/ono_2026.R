##Multi-member local-election candidate conjoint (Japan), single vs block vote, from
##Ono, Y., Miwa, H., & Kasuya, Y. (2026). Voting for gender balancing? The effect of a
##multiple-vote system on women's representation. Political Science Research and Methods.
##https://doi.org/10.1017/psrm.2026.10108
##Replication data: Harvard Dataverse doi:10.7910/DVN/BC6GSL, CC0 1.0. Files read from
##Ono_Miwa_Kasuya_PSRM_replication.zip: data/survey_data_jp.csv (the raw Qualtrics export
##in Japanese: row 1 question text, row 2 ImportId, then 5,400 respondents) and codebook.pdf
##(pdftotext). script/data_preprocessing_en.R was read as text to confirm the task mapping.
##The derived SNTV_data.csv / BV_*_data.csv files are not used.
##Usage: Rscript ono_2026.R <dir holding survey_data_jp.csv> <output dir>
##
##Design: Lucid online panel, Japan. Every respondent saw 5 tasks of 6 hypothetical
##candidates in a municipal-assembly election with 3 seats, randomly assigned to one of two
##ballot rules (trial_arm): SNTV (1,456 respondents; write one name) or BV (block vote,
##3,944 respondents; write three names, in order of preference). One experiment with one
##attribute set, so one table; the arm is a task-level column.
##Attributes (Qualtrics F-x-y-z: task x, candidate y, attribute slot z; F-x-z names the
##attribute in slot z), stored as the Japanese text shown: 性別 gender (男/女), 年齢 age
##(30代-70代), 学歴 education, 前職 previous occupation, 出身地 hometown, 議員経験 assembly
##experience. The attribute ORDER was randomized once per respondent (codebook: constant
##across tasks; checked below); attrpos_<attr> is the slot (1-6). Slot 7 held a pictogram
##(icon_man.jpg / icon_woman.jpg) matching the gender attribute (codebook F-x-y-7); not
##stored as a separate attribute. Hometown was piped from the respondent's own municipality
##(Qualtrics ${q://QID13/ChoiceGroup/SelectedAnswers/2}, i.e. "<municipality>" or
##"<municipality>外" = outside it); to avoid publishing each respondent's municipality the
##piped name is replaced by the placeholder 〔回答者の市区町村〕, giving the two levels
##〔回答者の市区町村〕 (inside) and 〔回答者の市区町村〕外 (outside).
##Outcomes (values = displayed position 1-6 of the chosen candidate, codebook):
##  choice_sntv       SNTV arm, Q1_SNTV1 (task 1), Q1-Q4_SNTV2 (tasks 2-5): vote for one.
##  choice_bv_first   BV arm, Q*_BV*_1: "まず1番目の候補者を選んでください" (first-ranked)
##  choice_bv_second  BV arm, Q*_BV*_2: second-ranked candidate
##  choice_bv_third   BV arm, Q*_BV*_3: third-ranked candidate
##Each is a pick among the 6 profiles, so it is a choice column; together the three BV
##columns are a partial ranking (top 3 of 6). No respondent picked the same candidate twice
##within a task (checked). Columns of the other arm are NA. No opt-out: every task in the
##export is answered (checked).
##Covariates: cov_gender (gender, codebook: 1 Man = male, 2 Woman = female, 3 Non-binary/third
##gender = other, 4 Prefer not to say = NA); cov_age (Lucid-supplied age in years);
##cov_education (edu, Lucid-supplied, codebook English labels: Junior high school, High
##school, Technical college, Vocational school, Junior college, University, Graduate school
##(Master's course), Graduate school (Doctoral course)); cov_sexism_1-5 (hostile-sexism items,
##codes as stored, 1 = Strongly agree ... 6 = Strongly disagree, wording in codebook).
##Dropped: municipality_1/2 (residence, quota variables), the attention checks sexism_6/7
##(constant: failures were screened out), the pictogram slot.
##N: 1,456 SNTV + 3,944 BV = 5,400 respondents, matching the counts printed by the authors'
##preprocessing (length(unique(respondent))). Restrictions and level weights are not
##documented.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "survey_data_jp.csv"), colClasses = "character", encoding = "UTF-8")[-(1:2)]
stopifnot(nrow(s) == 5400)
s[, id := .I]
amap <- c("性別" = "gender", "年齢" = "age", "学歴" = "education", "前職" = "occupation",
          "出身地" = "hometown", "議員経験" = "experience")
pipe <- "${q://QID13/ChoiceGroup/SelectedAnswers/2}"
rows <- list()
for (x in 1:5) for (y in 1:6) {
  r <- data.table(id = s$id, task = x, profile = y)
  for (z in 1:6) {
    nm <- amap[s[[sprintf("F-%d-%d", x, z)]]]
    stopifnot(!anyNA(nm))
    lev <- s[[sprintf("F-%d-%d-%d", x, y, z)]]
    lev <- gsub(pipe, "〔回答者の市区町村〕", lev, fixed = TRUE)
    r[, paste0("slot", z, "_name") := nm][, paste0("slot", z, "_lev") := lev]
  }
  rows[[length(rows) + 1]] <- r
}
L <- rbindlist(rows)
long <- rbindlist(lapply(1:6, function(z) L[, .(id, task, profile, attr = get(paste0("slot", z, "_name")),
                                                level = get(paste0("slot", z, "_lev")), pos = z)]))
stopifnot(long[, .N, .(id, task, profile, attr)][, all(N == 1)])
stopifnot(long[, uniqueN(pos), .(id, attr)][, all(V1 == 1)])   # order fixed within respondent
d <- dcast(long, id + task + profile ~ attr, value.var = c("level", "pos"))
setnames(d, sub("^level_", "attr_", names(d)))
setnames(d, sub("^pos_", "attrpos_", names(d)))
stopifnot(!anyNA(d), all(d$attr_gender %in% c("男", "女")),
          all(d$attr_hometown %in% c("〔回答者の市区町村〕", "〔回答者の市区町村〕外")))
## outcomes
sq <- c("Q1_SNTV1", "Q1_SNTV2", "Q2_SNTV2", "Q3_SNTV2", "Q4_SNTV2")
bq <- c("Q1_BV1", "Q1_BV2", "Q2_BV2", "Q3_BV2", "Q4_BV2")
s[, arm := fifelse(get(sq[1]) != "", "SNTV", fifelse(get(paste0(bq[1], "_1")) != "", "BV", NA_character_))]
stopifnot(!anyNA(s$arm), s[, sum(arm == "SNTV")] == 1456, s[, sum(arm == "BV")] == 3944)
o <- rbindlist(lapply(1:5, function(x) data.table(id = s$id, task = x, arm = s$arm,
  sntv = as.integer(s[[sq[x]]]), bv1 = as.integer(s[[paste0(bq[x], "_1")]]),
  bv2 = as.integer(s[[paste0(bq[x], "_2")]]), bv3 = as.integer(s[[paste0(bq[x], "_3")]]))))
stopifnot(o[arm == "SNTV", all(sntv %in% 1:6) & all(is.na(bv1))],
          o[arm == "BV", all(bv1 %in% 1:6) & all(bv2 %in% 1:6) & all(bv3 %in% 1:6) & all(is.na(sntv))],
          o[arm == "BV", all(bv1 != bv2 & bv1 != bv3 & bv2 != bv3)])
d <- merge(d, o, by = c("id", "task"))
d[, `:=`(choice_sntv = as.integer(profile == sntv), choice_bv_first = as.integer(profile == bv1),
         choice_bv_second = as.integer(profile == bv2), choice_bv_third = as.integer(profile == bv3),
         trial_arm = arm)]
d[, c("sntv", "bv1", "bv2", "bv3", "arm") := NULL]
## covariates
g <- s$gender; stopifnot(all(g %in% c("1", "2", "3", "4")))
edulab <- c("Junior high school", "High school", "Technical college", "Vocational school", "Junior college",
         "University", "Graduate school (Master's course)", "Graduate school (Doctoral course)")
stopifnot(all(s$edu %in% as.character(1:8)))
cv <- s[, .(id, cov_gender = c("male", "female", "other", NA)[as.integer(g)], cov_age = as.integer(age),
            cov_education = edulab[as.integer(edu)],
            cov_sexism_1 = as.integer(sexism_1), cov_sexism_2 = as.integer(sexism_2), cov_sexism_3 = as.integer(sexism_3),
            cov_sexism_4 = as.integer(sexism_4), cov_sexism_5 = as.integer(sexism_5))]
d <- merge(d, cv, by = "id")
stopifnot(nrow(d) == 5400 * 30)
setcolorder(d, c("id", "task", "profile", "choice_sntv", "choice_bv_first", "choice_bv_second", "choice_bv_third",
                 paste0("attr_", amap), paste0("attrpos_", amap), "trial_arm"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ono_2026_multiple_vote.csv"))
