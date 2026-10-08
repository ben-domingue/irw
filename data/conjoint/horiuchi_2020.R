##Japanese legislator candidate conjoint from
##Horiuchi, Y., Smith, D. M., & Yamamoto, T. (2020). Identifying voter preferences for
##politicians' personal attributes: A conjoint experiment in Japan. Political Science Research
##and Methods, 8(1), 75-91. https://doi.org/10.1017/psrm.2018.26
##Replication data: Harvard Dataverse doi:10.7910/DVN/KCIADO, CC0 1.0, no restricted files.
##Files read (from ReplicationPackage.tar.gz): data/Personal_Vote_Japan_final_nosens.csv (raw
##Qualtrics export, 2 header rows), docs/codebook.docx (Japanese questionnaire, read for wording
##and covariate codes); src/20_conjoint-preprocess.R read as text (translations, block layout).
##Usage: Rscript horiuchi_2020.R <dir holding Personal_Vote_Japan_final_nosens.csv> <output dir>
##
##2,200 Japanese adults (online panel, November 2015; all consented, all completed). Each was
##randomly assigned to ONE house (lower = 衆議院 House of Representatives, upper = 参議院
##House of Councillors) and to which electoral tier came first; tasks 1-5 asked about one tier
##(single-member district / prefectural district, or PR) and tasks 6-10 about the other. So 10
##tasks of 2 profiles, 9 attributes. ONE TABLE: same attributes, same respondents, one
##fielding; the authors pool the four conditions and compare them. trial_house (lower/upper)
##and trial_tier (district/pr) give the condition of each task.
##  choice: Q<b>.4, .7, ... .32 (人物１ / 人物２), forced choice, no opt-out. Wording (lower
##    house, district tier; the tier and house words change by block): "次の２人の人物のうち、
##    どちらがより小選挙区選出の衆議院議員として望ましいと思いますか。もし、どちらが望まし
##    いかはっきりとは言えない場合でも、どちらか一方、あえていえばより望ましいと思われる方
##    を選んでください。" (Which of the two is more desirable as a district-elected member of
##    the House of Representatives? Choose one even if unsure.) No task is unanswered.
##Attributes are stored in JAPANESE, exactly as displayed (Qualtrics F-<task>-<profile>-<k>
##fields): party 所属政党, age 年齢, gender 性別, terms 過去の当選回数, experience
##(衆議院議員としての経験 in lower-house blocks, 参議院議員としての経験 in upper-house blocks;
##stored as attr_experience), hometown 出身地, education 最終学歴, occupation 職歴, parent
##親の政治家経験. Hometown, occupation and parent levels name the respondent's own prefecture
##(e.g. "東京都以外", "東京都議会議員"), so they have up to 99 distinct texts; the authors
##collapse them to Inside/Outside, Prefectural governor/assembly member, etc.
##Attribute row order was randomized per respondent and held across tasks: attrpos_<name>
##(1-9) records it. Randomization restriction OBSERVED (no design file deposited): experience
##"在職経験なし" (never in office) occurs exactly when terms = "なし" (none), and otherwise never.
##Covariates (codebook codes): cov_prefecture (Q2.1, 1-47 in JIS order, 13 = 東京都),
##cov_age (Q2.5 code + 19, top code 90 = "90 or older"), cov_female (Q2.6 = 2), cov_education
##(Q2.7: 1 = elementary/junior high, 2 = high school, 3 = junior college/technical, 4 =
##university/graduate, 5 = still in school), cov_income (Q2.8 household income 2014, 1 = under
##1M yen .. 14 = 20M yen or more). The authors' entropy-balancing weights are computed in
##their code, not deposited, and are not rebuilt here.
##Dropped: Qualtrics ResponseID, name/email/external-reference fields (empty), timings,
##consent, municipality type, knowledge quiz, Q7-Q9 attitude/occupation items (the export's
##question-text row is misaligned with its column names there), the free-text occupation
##(Q8.8, Q8.9) and comment (Q9.4) fields, location fields (empty).
##N: 2,200 in the deposit; the article (paywalled) was not checked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
L <- readLines(file.path(raw, "Personal_Vote_Japan_final_nosens.csv"), encoding = "UTF-8")
D <- as.data.table(read.csv(textConnection(L[-2]), stringsAsFactors = FALSE, check.names = FALSE, colClasses = "character"))
stopifnot(nrow(D) == 2200, all(D$Q1.2 == "1"))
D[, id := seq_len(.N)]
D[, blk := fifelse(Q3.4 != "", "Q3", fifelse(Q4.4 != "", "Q4", fifelse(Q5.4 != "", "Q5", fifelse(Q6.4 != "", "Q6", NA_character_))))]
stopifnot(!anyNA(D$blk))
house <- c(Q3 = "lower", Q4 = "lower", Q5 = "upper", Q6 = "upper"); first <- c(Q3 = "district", Q4 = "pr", Q5 = "district", Q6 = "pr")
anames <- c(所属政党 = "party", 年齢 = "age", 性別 = "gender", 過去の当選回数 = "terms", 出身地 = "hometown",
            最終学歴 = "education", 職歴 = "occupation", 親の政治家経験 = "parent")
key <- function(nm) ifelse(grepl("としての経験$", nm), "experience", anames[nm])
qcol <- c(seq(4, 16, 3), seq(20, 32, 3))
rows <- list()
for (t in 1:10) for (p in 1:2) {
  r <- data.table(id = D$id, task = t, profile = p)
  resp <- sapply(seq_len(nrow(D)), function(i) D[[paste0(D$blk[i], ".", qcol[t])]][i])
  r[, choice := as.integer(as.integer(resp) == p)]
  for (j in 1:9) {
    nm <- D[[paste0("F-", t, "-", j)]]; k <- key(nm); stopifnot(!anyNA(k))
    lv <- D[[paste0("F-", t, "-", p, "-", j)]]
    for (kk in unique(k)) { w <- k == kk; r[w, paste0("attr_", kk) := lv[w]]; r[w, paste0("attrpos_", kk) := j] }
  }
  r[, trial_house := unname(house[D$blk])][, trial_tier := if (t <= 5) unname(first[D$blk]) else fifelse(first[D$blk] == "district", "pr", "district")]
  rows[[length(rows) + 1]] <- r
}
d <- rbindlist(rows, use.names = TRUE)
an <- c("party", "age", "gender", "terms", "experience", "hometown", "education", "occupation", "parent")
stopifnot(!anyNA(d[, paste0("attr_", an), with = FALSE]), d[, sum(choice), .(id, task)][, all(V1 == 1)])
stopifnot(d[, all((attr_experience == "在職経験なし") == (attr_terms == "なし"))])
cv <- D[, .(id, cov_prefecture = as.integer(Q2.1), cov_age = as.integer(Q2.5) + 19L, cov_female = as.integer(as.integer(Q2.6) == 2L),
            cov_education = as.integer(Q2.7), cov_income = as.integer(Q2.8))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", an), paste0("attrpos_", an), "trial_house", "trial_tier"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "horiuchi_2020_japan_politicians.csv"))
