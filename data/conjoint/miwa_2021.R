##Ideological-label conjoint (Japan) from
##Miwa, H., Arami, R., & Taniguchi, M. (2023). Detecting voter understanding of ideological
##labels using a conjoint experiment. Political Behavior, 45(2). (Online 2021.)
##https://doi.org/10.1007/s11109-021-09719-5
##Replication data: Harvard Dataverse doi:10.7910/DVN/FIHGN0, CC0 1.0. File read:
##ideological_label_conjoint_data.csv ("original format" of ideological_label_conjoint_data.tab,
##the raw survey export, UTF-8). The authors' 0_data_preparation.r and readme.txt were read as
##text (not run); they are the only documentation in the deposit (no codebook, no questionnaire;
##the article itself was not accessible, so outcome wording below is a paraphrase from the code).
##Usage: Rscript miwa_2021.R <dir holding the csv> <output dir>
##
##Japanese online survey respondents; each saw 3 tasks of 2 hypothetical candidates described
##only by their positions on 8 issues. Issue (attribute) text and position (level) text are
##Japanese, stored as displayed: levels 賛成 (agree), 賛成でも反対でもない (neither agree nor
##disagree), 反対 (disagree). Attributes (issue statement shown as the row label):
##  attr_article9          憲法9条を改正すべきである (Article 9 of the constitution should be revised)
##  attr_defense           日本の防衛力を強化すべきである (Japan should strengthen its defence)
##  attr_stop_apology      日本は戦前・戦中の出来事に関して近隣諸国に謝罪するのをやめるべきである
##  attr_women             専業主婦世帯の税制を見直し，女性の社会進出を促進すべきである
##  attr_samesex_marriage  男性同士，女性同士での結婚を法律で認めるべきである
##  attr_foreign_workers   日本は外国人労働者を積極的に受け入れるべきである
##  attr_growth            経済的格差の是正よりも，経済成長を優先すべきである
##  attr_tax_rich          裕福な人に対する課税を強化すべきである
##Issue order was randomized once per respondent (the same order in all 3 tasks: checked) and is
##recorded (F-t-k columns name the issue in row k): attrpos_<issue> = row position 1-8.
##Restrictions and level probabilities are not documented (see design record).
##Label experiment (between subjects, trial_label): condition 0 = "right" label, condition 1 =
##"left" label (authors' code comment: 'right'-label condition = 0, 'left'-label = 1).
##  choice_more_right: (right arm only) which of the two candidates is more to the right
##    (paraphrase; Q4.t.1-1, 1 = left-hand candidate, 2 = right-hand candidate). Forced choice.
##  choice_more_left:  (left arm only) which candidate is more to the left (paraphrase; Q4.t.1-2).
##    Each is NA on the other arm's rows.
##  rating: placement of each candidate on a 1-10 left-right scale (Q4.t.2-c_1/_2; the authors
##    pool both arms without reversal). Endpoint labels are not in the deposit. Observed: in the
##    right arm the candidate chosen as more right is rated 1.3-1.7 points higher, in the left arm
##    the candidate chosen as more left is rated 1.5-1.8 lower, so higher = more right in both arms.
##Profile 1 = left column of the table, 2 = right column (authors' code: position.right).
##trial_page_submit_sec = page-submit time of the task's choice page (Qualtrics timing, Q4.t-cT_3).
##Sample: the authors drop respondents aged over 69 (Q5.2 >= 53; one respondent); same here:
##1,504 respondents x 3 tasks x 2 profiles. The authors' main analyses further drop 'satisficers'
##(failed either directed question) and tasks answered in <= 5 seconds; nothing else is dropped
##here: the attention items are cov_attention_pass_1 (Q1_9, pass = 5) and cov_attention_pass_2
##(Q1_10, pass = 1), from the authors' satisficing rule, and the timing is kept.
##Covariates: cov_gender (Q5.1: 1 = male, 2 = female; authors' code "gender (dummy, woman = 1) <-
##Q5.1 - 1"), cov_age (Q5.2 + 17, authors' code), cov_education_code (Q5.3, codes 1-7; the code
##only groups 1-2 high school or lower, 3-5 technical/community/vocational college, 6-7 college or
##higher, so no answer text), cov_prefecture_code (Q5.4, 1-47, prefecture index), cov_knowledge
##(Q2, self-reported knowledge of left-right labels, code; authors treat < 3 as high knowledge),
##cov_ideology (self-placement 1-10 from the Q3_1..Q3_10 one-hot columns, authors' code; NA if none),
##cov_attitude_<issue> (Q1_1..Q1_8, 5-point codes, wording/anchors not in the deposit).
##Dropped: survey timing of non-task pages, the authors' derived dummies and DID ratio.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "ideological_label_conjoint_data.csv"), encoding = "UTF-8")
s <- s[Q5.2 < 53]
s[, id := .I]
stopifnot(nrow(s) == 1504)
issues <- c(article9 = "憲法9条を改正すべきである", defense = "日本の防衛力を強化すべきである",
            stop_apology = "日本は戦前・戦中の出来事に関して近隣諸国に謝罪するのをやめるべきである",
            women = "専業主婦世帯の税制を見直し，女性の社会進出を促進すべきである",
            samesex_marriage = "男性同士，女性同士での結婚を法律で認めるべきである",
            foreign_workers = "日本は外国人労働者を積極的に受け入れるべきである",
            growth = "経済的格差の是正よりも，経済成長を優先すべきである",
            tax_rich = "裕福な人に対する課税を強化すべきである")
lev <- c("賛成", "賛成でも反対でもない", "反対")
# issue order identical across tasks
for (t in 2:3) for (k in 1:8) stopifnot(all(s[[sprintf("F-1-%d", k)]] == s[[sprintf("F-%d-%d", t, k)]]))
rows <- list()
for (t in 1:3) for (p in 1:2) {
  d <- data.table(id = s$id, task = t, profile = p)
  cond <- s$condition
  ch <- ifelse(cond == 0, s[[sprintf("Q4.%d.1-1", t)]], s[[sprintf("Q4.%d.1-2", t)]])
  d[, choice_more_right := fifelse(cond == 0, as.integer(ch == p), NA_integer_)]
  d[, choice_more_left := fifelse(cond == 1, as.integer(ch == p), NA_integer_)]
  d[, rating := as.integer(ifelse(cond == 0, s[[sprintf("Q4.%d.2-1_%d", t, p)]], s[[sprintf("Q4.%d.2-2_%d", t, p)]]))]
  for (k in 1:8) {
    iss <- s[[sprintf("F-%d-%d", t, k)]]
    pos <- if (p == 1) s[[sprintf("F-%d-1-%d", t, k)]] else s[[sprintf("F-%d-2-%d", t, k)]]
    nm <- names(issues)[match(iss, issues)]
    stopifnot(!anyNA(nm), all(pos %in% lev))
    for (n in names(issues)) {
      w <- nm == n
      if (k == 1) { d[, paste0("attr_", n) := NA_character_]; d[, paste0("attrpos_", n) := NA_integer_] }
      set(d, which(w), paste0("attr_", n), pos[w]); set(d, which(w), paste0("attrpos_", n), k)
    }
  }
  d[, trial_label := c("right", "left")[cond + 1L]]
  d[, trial_page_submit_sec := ifelse(cond == 0, s[[sprintf("Q4.%d-1T_3", t)]], s[[sprintf("Q4.%d-2T_3", t)]])]
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), !anyNA(d$rating))
stopifnot(d[trial_label == "right", sum(choice_more_right), .(id, task)][, all(V1 == 1)],
          d[trial_label == "left", sum(choice_more_left), .(id, task)][, all(V1 == 1)])
cv <- data.table(id = s$id, cov_gender = c("male", "female")[s$Q5.1], cov_age = as.integer(s$Q5.2 + 17L),
                 cov_education_code = as.integer(s$Q5.3), cov_prefecture_code = as.integer(s$Q5.4),
                 cov_knowledge = as.integer(s$Q2))
stopifnot(all(s$Q5.1 %in% 1:2))
id10 <- as.matrix(s[, paste0("Q3_", 1:10), with = FALSE]); id10[is.na(id10)] <- 0
ideo <- as.integer(id10 %*% (1:10)); ideo[ideo == 0] <- NA
stopifnot(all(rowSums(id10) <= 1))
cv[, cov_ideology := ideo]
for (i in 1:8) cv[, paste0("cov_attitude_", names(issues)[c(1, 2, 3, 4, 5, 6, 7, 8)][i]) := as.integer(s[[paste0("Q1_", i)]])]
cv[, cov_attention_pass_1 := as.integer(s$Q1_9 == 5)][, cov_attention_pass_2 := as.integer(s$Q1_10 == 1)]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice_more_right", "choice_more_left", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miwa_2021_ideological_labels.csv"))
