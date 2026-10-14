##Paired candidate policy-position conjoint, Japan (2021 general election), from
##Miwa, H. (2023). 2021 nen sosenkyo ni okeru yukensha no seisaku senko oyobi soten no juyodo to toohyo
##[Voters' policy preferences, issue importance and vote in the 2021 general election]. Senkyo Kenkyu
##[Japanese Journal of Electoral Studies], 38(2), 48-62. https://doi.org/10.14854/jaes.38.2_48
##Replication data: Harvard Dataverse doi:10.7910/DVN/JDURC1, CC0 1.0. File read: conjoint_data.tab, "original
##format" download = conjoint_data.csv (Shift-JIS/CP932, Qualtrics export with the cjoint read.qualtrics layout).
##online_appendix.pdf (codebook B.2, design B.2/Table A1) and conjoint_code.R read as text (not run). The
##deposit's default .tab download is mojibake; only the original CSV is read.
##Usage: Rscript miwa_2023_policy_positions.R <dir holding conjoint_data.csv> <output dir>
##
##2,236 Japanese adults aged 18-69 (online panel, quota sample on gender, age and education, Feb 2022; n = 2,236 in
##the appendix, D.1), 15 tasks x 2 hypothetical candidates ("candidate 1"/"candidate 2" = profile 1/2) whose
##main policy positions are shown in a table. Ten attributes with two levels each, text as stored (Japanese phrase
##completing the attribute label; label in parentheses, authors' short name in the code):
##  attr_constitution (憲法改正, constitution): 改正すべき / 改正すべきでない  (should / should not be revised)
##  attr_attack (敵基地攻撃能力の保有): 検討すべき / 検討すべきでない  (should / should not consider counter-strike capability)
##  attr_pubwork (公共事業による雇用確保): 必要である / 必要でない  (public works for jobs necessary / not necessary)
##  attr_consumption_tax (消費税率): 引き下げるべき / 引き下げるべきでない  (should / should not be cut)
##  attr_corporate_tax (企業が納める法人税率): 引き上げるべき / 引き上げるべきでない  (should / should not be raised)
##  attr_surname (選択的夫婦別姓): 法律で認めるべき / 認めるべきでない  (legally permit / not permit)
##  attr_samesex (男性同士・女性同士の結婚（同性婚）): 法律で認めるべき / 認めるべきでない
##  attr_nuclear (原子力発電): 廃止すべき / 維持すべき  (abolish / maintain)
##  attr_lockdown (強制的な外出自粛や休業措置（ロックダウン）): 法整備をすべき / 法整備をすべきでない
##  attr_covid_priority (コロナ対策の最優先事項): 治療体制の拡充 / 治療薬やワクチンの開発・確保  (expand treatment
##      capacity / develop and secure drugs and vaccines)
##Attribute order is randomized once per respondent (the position is constant across a respondent's 15 tasks, checked) and recorded: attrpos_<name> = row position (1-10) of the attribute in the
##task table, from the F-<task>-<position> columns (attribute label at each position). Level text: F-<task>-<cand>-<pos>.
##Randomization restrictions: none documented (the authors test all 45 pairwise interactions with all combinations
##occurring, appendix D.2.2); level shares ~50/50 for every attribute but no probabilities are stated.
##Outcome: rating = Q<task>_C_<candidate>, "How likely are you to vote for each of the candidates?" (あなたは
##それぞれの候補者について，どのくらい投票する可能性がありますか), judged only on the stated policy positions, six-point
##scale with poles 「絶対に投票しない」 (definitely would not vote) and 「高い確率で投票する」 (high probability of voting)
##(appendix B.2). The numeric direction is not stated; stored raw 1-6. HIGHER = MORE LIKELY TO VOTE is inferred from the
##signs of the attribute effects (see the sign check printed below, e.g. cutting the consumption tax raises the rating)
##and from the authors' use of the rating as "voting probability" (投票可能性) in lm_robust. Not a forced choice: no
##choice column.
##Covariates: cov_gender (gender.2: 1 Man = male, 2 Woman = female, 3 non-binary = other, 4 prefer not to say = NA;
##appendix B.2), cov_age (age in years), cov_education (edu, appendix answer text: 中学校, 高校, 高等専門学校,
##専門学校／専修学校, 短期大学, 4年制大学, 大学院（修士課程）, 大学院（博士課程）; code 9 "none of the above" ends the
##survey), cov_party_id (PID: long-term party closeness, appendix answer text, 11 = どの政党でもない "no party"),
##cov_vote_pr_2021 (PR: recalled 2021 PR vote, answer text, 11 投票しなかった did not vote, 12 覚えていない
##don't remember), cov_prefecture_code (pref: JIS prefecture code, 1-47).
##Dropped: the survey-level policy preference items (P1, P2, const), start/end timestamps, IMC attention-check text
##(all kept respondents passed it), gender (quota binary), citizenship (all Japanese), derived scales.
##Count check: 2,236 respondents, 67,080 profile rows = 2,236 x 15 x 2.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "conjoint_data.csv")
k <- fread(text = iconv(rawToChar(readBin(f, "raw", file.size(f))), "CP932", "UTF-8"), colClasses = "character", na.strings = "", header = TRUE)
k <- k[-(1:2)]
stopifnot(nrow(k) == 2236, uniqueN(k$rid) == 2236)
an <- c("憲法改正" = "constitution", "敵基地攻撃能力の保有" = "attack", "公共事業による雇用確保" = "pubwork",
        "消費税率" = "consumption_tax", "企業が納める法人税率" = "corporate_tax", "選択的夫婦別姓" = "surname",
        "男性同士・女性同士の結婚（同性婚）" = "samesex", "原子力発電" = "nuclear",
        "強制的な外出自粛や休業措置（ロックダウン）" = "lockdown", "コロナ対策の最優先事項" = "covid_priority")
rows <- list()
for (t in 1:15) for (cnd in 1:2) {
  d <- data.table(id = as.integer(k$rid), task = t, profile = cnd, rating = as.integer(k[[sprintf("Q%d_C_%d", t, cnd)]]))
  for (p in 1:10) {
    lab <- k[[sprintf("F-%d-%d", t, p)]]
    nm <- an[lab]; stopifnot(!anyNA(nm))
    lev <- k[[sprintf("F-%d-%d-%d", t, cnd, p)]]
    for (n in unique(nm)) {
      i <- which(nm == n)
      if (!(paste0("attr_", n) %in% names(d))) { d[, (paste0("attr_", n)) := NA_character_]; d[, (paste0("attrpos_", n)) := NA_integer_] }
      set(d, i, paste0("attr_", n), lev[i]); set(d, i, paste0("attrpos_", n), p)
    }
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
stopifnot(!anyNA(d[, grep("^attr", names(d)), with = FALSE]))
g <- k[match(d$id, as.integer(k$rid))]
d[, cov_gender := c("1" = "male", "2" = "female", "3" = "other", "4" = NA)[g$gender.2]]
d[, cov_age := as.integer(g$age)]
edu <- c("中学校", "高校", "高等専門学校", "専門学校／専修学校", "短期大学", "4年制大学", "大学院（修士課程）", "大学院（博士課程）")
d[, cov_education := edu[as.integer(g$edu)]]
pty <- c("自由民主党", "立憲民主党", "公明党", "日本共産党", "日本維新の会", "国民民主党", "れいわ新選組", "社会民主党",
         "NHK受信料を支払わない国民を守る党", "その他の政党", "どの政党でもない")
d[, cov_party_id := pty[as.integer(g$PID)]]
pr <- c(pty[1:9], "その他の政党", "投票しなかった", "覚えていない")
d[, cov_vote_pr_2021 := pr[as.integer(g$PR)]]
d[, cov_prefecture_code := as.integer(g$pref)]
d <- d[!is.na(rating)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miwa_2023_policy_positions.csv"))
cat("rows", nrow(d), "resp", uniqueN(d$id), "\n")
cat("sign check (mean rating by level; high = more likely to vote assumed):\n")
for (n in c("consumption_tax", "samesex", "constitution", "nuclear")) print(d[, .(m = round(mean(rating), 2), n = .N), by = c(paste0("attr_", n))])
