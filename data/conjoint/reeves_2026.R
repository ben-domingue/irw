##House of Councillors candidate conjoint (Japan, 2019) from
##Reeves, J. F., & Smith, D. M. (2026). Getting to know her: Information and gender bias in
##preferential voting systems. Electoral Studies, 103120. https://doi.org/10.1016/j.electstud.2026.103120
##Replication data: Harvard Dataverse doi:10.7910/DVN/E4IQSC, CC0 1.0. One zip,
##Reeves-Smith-2026-replication_archive.zip; files read from it: HoC_merged_clean.dta (only the
##2019 rows and the columns used below), instruments/Survey_Instruments-2019_conjoint_addendum.pdf
##(design, English translation) and instruments/Survey_Instruments_and_Translations_Simplified.pdf
##(treatment groups); _Figure6.do / _FigureA6.do read as text (not run).
##Usage: Rscript reeves_2026.R <dir holding HoC_merged_clean.dta> <output dir>
##
##2019 online survey of Japanese voters, 2,018 respondents, all with 10 tasks of 2 hypothetical
##candidates for the House of Councillors PR list ("人物1", "人物2"), 7 attributes, shown in
##Japanese. The conjoint followed the main voting experiment; the 2016 survey had no conjoint.
##  choice = Conjoint_A<t>_num (1 = person 1, 2 = person 2): "次の2人の人物のうち、どちらがより
##           比例代表選出の参議院議員として望ましいと思いますか。" (Which of the following two
##           persons do you think is the most desirable as a PR list member of the House of
##           Councillors?), forced choice, no opt-out (addendum).
##Levels are the Japanese display text from the Qualtrics display columns F_<t>_<p>_<pos> (the
##attribute at row <pos> named in F_<t>_<pos>). As designed, hometown and prefectural-assembly
##levels name the respondent's own prefecture (e.g. "東京都以外", "東京都議会議員"; addendum note
##on "X"), so these attributes have one level set per prefecture; the authors collapse them to
##inside/outside and "prefectural assembly" (_Figure6.do). An HTML "<br>" in display text is
##removed. Attribute names: attr_age 年齢, attr_gender 性別, attr_incumbency 新旧 (当選回数),
##attr_politics 国会議員以外の政治経験, attr_hometown 出身地, attr_education 最終学歴,
##attr_occupation 職歴. Attribute order randomized (addendum), once per respondent (the same
##order in all 10 tasks in the display columns); attrpos_* record it.
##trial_treatment_group: the main experiment's arm, assigned before the conjoint
##(instrument p. 4): 1 free vote, no candidate information; 2 free vote, with information;
##3 compulsory preference vote, no information; 4 compulsory preference vote, with information.
##The paper estimates the conjoint by group (Figure 6, A6-A8); one table, group as trial_.
##Covariates: cov_gender from female_respondent (survey: Male/Female only); cov_age (years);
##cov_education and cov_party_id are the authors' English category text in the .dta
##(education: elementary or middle / high school / junior college / still in school /
##university or grad school; party_id: party abbreviations, "No Party"). The Qualtrics response
##ID is re-keyed to integers. Free-text answers (*_reason_text) and click timings not kept.
##No survey weight in the deposit. Randomization: levels drawn at random (addendum); no
##restrictions or probabilities stated.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fcols <- c(sprintf("F_%d_%d", rep(1:10, each = 7), 1:7),
           sprintf("F_%d_%d_%d", rep(1:10, each = 14), rep(rep(1:2, each = 7), 10), 1:7))
s <- as.data.table(read_dta(file.path(raw, "HoC_merged_clean.dta"),
  col_select = any_of(c("response_id", "year", "treatment_group", "female_respondent", "age", "education", "party_id",
                        sprintf("Conjoint_A%d_num", 1:10), fcols))))
s <- s[year == 2019]
stopifnot(nrow(s) == 2018, !anyDuplicated(s$response_id))
an <- c("年齢" = "age", "性別" = "gender", "新旧 (当選回数)" = "incumbency", "国会議員以外の<br>政治経験" = "politics",
        "出身地" = "hometown", "最終学歴" = "education", "職歴" = "occupation")
W <- rbindlist(lapply(1:10, function(t) rbindlist(lapply(1:7, function(k) rbindlist(lapply(1:2, function(p)
  data.table(rid = s$response_id, task = t, profile = p, pos = k, aname = s[[sprintf("F_%d_%d", t, k)]],
             lev = s[[sprintf("F_%d_%d_%d", t, p, k)]])))))))
stopifnot(all(W$aname %in% names(an)), !anyNA(W$lev), all(W$lev != ""))
W[, att := an[aname]][, lev := trimws(gsub("<br>", "", lev, fixed = TRUE))]
stopifnot(W[, .(n = uniqueN(att)), .(rid, task, profile)]$n == 7,
          unique(W[, .(rid, att, pos)])[, .N, .(rid, att)]$N == 1)
P <- dcast(W, rid + task + profile ~ paste0("attr_", att), value.var = "lev")
Q <- dcast(unique(W[profile == 1, .(rid, task, att, pos)]), rid + task ~ paste0("attrpos_", att), value.var = "pos")
P <- merge(P, Q, by = c("rid", "task"))
C <- melt(s[, c("response_id", sprintf("Conjoint_A%d_num", 1:10)), with = FALSE], id.vars = "response_id",
          variable.name = "task", value.name = "pick")
C[, task := as.integer(sub("Conjoint_A(\\d+)_num", "\\1", task))]
stopifnot(all(C$pick %in% 1:2))
P <- merge(P, C, by.x = c("rid", "task"), by.y = c("response_id", "task"))
P[, choice := as.integer(pick == profile)][, pick := NULL]
cv <- s[, .(rid = response_id, trial_treatment_group = as.integer(treatment_group),
            cov_gender = ifelse(female_respondent == 1, "female", "male"), cov_age = as.integer(age),
            cov_education = as.character(education), cov_party_id = as.character(party_id))]
stopifnot(all(cv$trial_treatment_group %in% 1:4), !anyNA(cv$cov_gender))
cv[cov_education == "", cov_education := NA][cov_party_id == "", cov_party_id := NA]
d <- merge(P, cv, by = "rid")
ids <- data.table(rid = sort(unique(d$rid), method = "radix"))[, id := .I]
d <- merge(d, ids, by = "rid")[, rid := NULL]
atts <- c("age", "gender", "incumbency", "politics", "hometown", "education", "occupation")
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", atts), paste0("attrpos_", atts), "trial_treatment_group"))
stopifnot(d[, .(n = .N, s = sum(choice)), .(id, task)][, all(n == 2 & s == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "reeves_2026_councillor_candidates.csv"))
