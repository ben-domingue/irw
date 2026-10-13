##Vignette experiment on voter preferences for ethnoracial minority candidates in Japan from
##Igarashi, A., & Ono, Y. (2025). Voter preferences for ethnoracial minority candidates: The role of policy alignment and shared
##identity. Journal of Experimental Political Science. https://doi.org/10.1017/XPS.2025.1
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z518MY, CC0 1.0. File read: replication_row.tab (the .csv export, saved as
##data.tab); replication.do and readme.txt as text. Journal title and article details come from the article page.
##Usage: Rscript igarashi_2025_minority_candidates.R <dir holding data.tab> <output dir>
##
##3,000 respondents of the Rakuten Insight online panel (12-18 March 2024; quota sample on gender, age and area; valid responses after an
##attention check), one vignette each (id = a running number; task = profile = 1) about a hypothetical Liberal Democratic Party
##candidate for national office. Three attributes, text as displayed (Japanese; the readme gives the translations):
##  attr_candidate_name   誠一郎 (Seiichiro: Japanese name), ジェームズ (James: American name), 超鴻（チョウコウ）(a Chinese name)
##  attr_candidate_origin 近隣の自治体からこの選挙区に移り住んできました (moved to the district from a neighbouring municipality: Japanese
##                        origin) / アメリカからこの選挙区に移り住み、日本国籍に帰化しました (moved from the U.S., naturalized: American) /
##                        中国からこの選挙区に移り住み、日本国籍に帰化しました (moved from China, naturalized: Chinese)
##  attr_candidate_policy 永住外国人の地方参政権を始めとする市民の平等な政治参加を促進すること (promote equal political participation of
##                        citizens including local voting rights for permanent-resident foreigners) / 永住外国人の地方参政権に断固反対し
##                        日本人第一の社会づくりを行うこと (firmly oppose local voting rights for permanent-resident foreigners and build a
##                        Japanese-first society)  (translations from readme.txt)
##Restrictions (the do file's nameorigin variable, article): five name x origin combinations x two policies = ten vignettes. A Japanese-
##origin candidate always has the Japanese name; an American-origin candidate has the Japanese or the American name; a Chinese-origin
##candidate has the Japanese or the Chinese name; the American name never appears with another origin and the Chinese name only with
##Chinese origin (checked in the data: three of the nine name x origin cells are empty).
##Outcomes (ratings, 5-point; the question wording and the answer labels are not in the deposit or the article page, and the
##instrument is in the supplement, so only the authors' variable meanings are used):
##  rating_vote_willingness  Q13.5, willingness / likelihood to vote for the candidate. STORED RAW. The authors' variable
##                           willingness_vote = 6 - Q13.5, so that higher = more willing: raw 1 is therefore the most willing end and 5 the
##                           least (inferred from that recode; not a labelled scale).
##  rating_favorability      Q13.4, favorability toward the candidate (appendix figures A2-A4 use favorability = 6 - Q13.4): STORED RAW,
##                           raw 1 = most favourable by the same inference.
##Covariates: cov_gender_code (Q2.2: 1 and 2 as the do file; the do file's own coding is gender 1 = q22 1, 2 = q22 2, other = 3;
##the labels are not in the deposit), cov_age (Q2.1, years), cov_education_code (Q2.6, 1-8; the do file groups 1-2, 3-5, 6, 7+ without
##labels), cov_attention_pass (1 if the three manipulation checks Q14.1-Q14.3 were all correct, as the authors' attentionall:
##origin check Q14.1 = 2/3/4 for Japanese/American/Chinese origin, policy check Q14.2 = 1 equal / 2 restrictive, Q14.3 = 1).
##Dropped: ResponseId, the three threat-perception items (Q8.1_1-3), Q5.3 (ideology item, scale direction not documented).
##Count check: N = 3,000 as in the article page; all ten vignette cells occur.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "data.tab"), encoding = "UTF-8", showProgress = FALSE)
stopifnot(nrow(k) == 3000, !anyNA(k$name), !anyNA(k$origin), !anyNA(k$policy))
o_r <- ifelse(grepl("^近隣", k$origin), 1L, ifelse(grepl("^アメリカ", k$origin), 2L, ifelse(grepl("^中国", k$origin), 3L, NA)))
p_r <- ifelse(grepl("促進", k$policy), 0L, ifelse(grepl("断固反対", k$policy), 1L, NA))
stopifnot(!anyNA(o_r), !anyNA(p_r))
att <- as.integer((o_r == 1 & k[["Q14.1"]] == 2) | (o_r == 2 & k[["Q14.1"]] == 3) | (o_r == 3 & k[["Q14.1"]] == 4)) *
       as.integer((p_r == 0 & k[["Q14.2"]] == 1) | (p_r == 1 & k[["Q14.2"]] == 2)) * as.integer(k[["Q14.3"]] == 1)
o <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, rating_vote_willingness = as.integer(k[["Q13.5"]]),
  rating_favorability = as.integer(k[["Q13.4"]]), attr_candidate_name = k$name, attr_candidate_origin = k$origin,
  attr_candidate_policy = k$policy, cov_gender_code = as.integer(k[["Q2.2"]]), cov_age = as.integer(k[["Q2.1"]]),
  cov_education_code = as.integer(k[["Q2.6"]]), cov_attention_pass = att)
stopifnot(!anyNA(o$rating_vote_willingness), !anyNA(o$rating_favorability), o[, uniqueN(.SD), .SDcols = patterns("^attr_")] == 10)
setorder(o, id, task, profile)
fwrite(o, file.path(out, "igarashi_2025_minority_candidates.csv"))
