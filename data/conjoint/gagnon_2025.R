##Two Japanese candidate-choice conjoints from
##Gagnon, E., Ikeda, F., & McElwain, K. M. (2025). Preferring national elites or local
##candidates: A conjoint analysis of voter heuristics. Journal of Politics.
##https://doi.org/10.1086/737779
##Replication data: Harvard Dataverse doi:10.7910/DVN/E4OOYT, CC0 1.0. Files read:
##main_survey_final.csv (survey 1) and follow_up_survey_rakuten.csv (survey 2), Dataverse
##"original format" downloads (Qualtrics exports with 3 header rows), saved as
##main_survey_final.csv and follow_up.csv. Read as text: README.txt, Codebook.pdf (Japanese +
##English wording of every question), 1_format_first_survey.R, 2_format_second_survey.R,
##attribute_mapper.yaml, colnames_mapper.yaml, plot_label_mapper.yaml. The article (JOP) was
##not reachable, so sample sizes and fielding details are not checked.
##Usage: Rscript gagnon_2025.R <dir holding the two csv files> <output dir>
##
##Two tables: the surveys used different attribute sets and samples (separate experiments).
##
##gagnon_2025_local_candidates (survey 1): Japanese adults, 8 pairs of hypothetical House of
##  Representatives candidates ("Candidate A" / "Candidate B"), 9 attributes in a fixed row order
##  (F-<task>-<profile>-<k>; names from the authors' format script): university, high_school,
##  job (career before politics), time_on_job, incumbency (genshoku), father_job,
##  policy_position, last_name, gender. Level text is the Japanese as stored. LIMITATION: six
##  attributes were piped from Qualtrics embedded fields that are NOT in this export
##  (respondent_prefecture, outside_prefecture, university_local, university_outside,
##  todai_kyodai); the stored text keeps the placeholder, rewritten from "${e://Field/x}" to
##  "[x]", e.g. "[respondent_prefecture]の高校" = a high school in the respondent's own
##  prefecture. Survey 2's export shows what these were (the respondent's prefecture, Tokyo or
##  Osaka, the prefecture's national university, the University of Tokyo or Kyoto University),
##  but survey 1 respondents' values are not deposited. The authors' English labels are in
##  plot_label_mapper.yaml (e.g. Local / Non-local High School, UTokyo/KyotoU). time_on_job is
##  stored as the bare number (10/20/30/40; unit not shown in the export). One trailing newline
##  in a policy level is trimmed.
##  Outcomes (codebook wording; options Candidate A / Candidate B, forced):
##    choice: Q26/Q167/Q172/Q177/Q182/Q186/Q189/Q213 "Which candidate would you prefer to vote
##      for? Even if there is no candidate you want to choose, please select one candidate you
##      would prefer if you were forced to."
##    choice_benefit_me / choice_benefit_prefecture / choice_benefit_japan: Q108_1/_2/_3 (and the
##      matching Q169_*, ..., Q214_*) "Considering separately the benefits to you personally,
##      your prefecture, and Japan as a whole, which candidate do you think would bring more
##      benefits to each?" (- For you personally / - [your prefecture] / - Japan).
##  Covariates (Codebook.pdf survey 1, Japanese option text): cov_prefecture_code (Q35_1, 1-47
##  dropdown), cov_ideology (Q36_1, 0 left - 10 right), cov_party_id (Q37 option text: 1
##  自由民主党, 2 立憲民主党, 3 国民民主党, 4 公明党, 5 日本共産党, 6 日本維新の会, 7 社会民主党,
##  8 れいわ新選組, 9 その他の政治団体, 10 どの政党でもない, 99 わからない), cov_gender (Q27:
##  0 男性 -> "male", 1 女性 -> "female", 98 その他 -> "other", 99 答えたくない -> NA),
##  cov_birth_year (Q28), cov_education (Q31_1 option text: 1 小学校・中学校, 2 高等学校,
##  3 専修学校（専門学校）, 4 短大・高専, 5 大学, 6 大学院; 99 -> NA: the codebook calls it
##  わからない, the authors' 10_make_descriptive_table.R calls it "Don't Want to Answer"),
##  cov_city_size (Q216: 3 Tokyo wards/designated/capital, 2 other city, 1 town/village, 99),
##  cov_duration_sec (the export's "Duration (in seconds)", the whole survey), cov_finished
##  (the authors keep finished == 1).
##  Restrictions and level weights: none documented; observed level shares are close to uniform
##  (within 1.08x) and no attribute combination is missing. Attribute order is fixed: every
##  F-<t>-<p>-<k> position holds the same attribute's levels for all respondents.
##
##gagnon_2025_local_status (survey 2, Rakuten Insight panel per the file name): 3 pairs of
##  hypothetical male candidates, 4 randomized attributes in a fixed row order (F-t-k names
##  constant): last_name, local_status (a biography sentence with 3 versions: local-born, local
##  schooling and local career; non-local throughout; elite = local high school, University of
##  Tokyo/Kyoto, national bureaucrat in Tokyo), party (LDP / CDP / DPFP / JCP, Japanese names),
##  time_on_job (22/24/25/26, bare number). Gender is fixed at 男性 for every profile (not
##  stored). The first name shown next to the surname is a separate embedded field
##  (task_<t>_profile_<p>_name) and is kept as attr_first_name. Here the embedded fields ARE in
##  the export, so the piped text is filled in with each respondent's values: the stored
##  local_status text is what that respondent saw (newlines trimmed). Respondents with no
##  embedded values (2) cannot be filled and are dropped.
##  Outcomes (codebook; Candidate A / B, forced): choice = Q20/Q167/Q172 vote (same wording as
##  survey 1); choice_business_attraction, choice_tourism, choice_public_works,
##  choice_government_debt, choice_diplomacy, choice_pensions = Q224_1-6 (Q225_*, Q226_*)
##  "Which candidate do you think will take a more active role in addressing the following
##  policy issues? Please consider each issue separately and answer. - <issue>";
##  choice_prefecture_issues = Q227/Q228/Q229 "Which candidate do you think will take a more
##  active role in addressing the political issues in your prefecture?"
##  Covariates: cov_prefecture (respondent_prefecture embedded field, text), cov_party_id (Q42,
##  same options and text as Q37 above, Codebook.pdf survey 2), cov_gender (Q22, as Q27 above),
##  cov_birth_year (Q24), cov_education (Q223: the export has codes 1-5 and 99, not the six
##  options the codebook lists, so the text is the authors' recode in
##  10_make_descriptive_table.R: 1 "High School or Less", 2 "Vocational School", 3 "2 Year
##  University", 4 "4 Year University", 5 "Graduate School"; 99 -> NA; English, since no
##  Japanese wording of this five-option version is deposited), cov_city_size (Q211, codes as
##  above), cov_duration_sec (the export's "Duration (in seconds)", the whole survey),
##  cov_finished. Attribute order fixed (F.<t>.<k> attribute-name fields constant).
##
##Both: task = Qualtrics task index, profile 1 = Candidate A. Tasks with no vote answer are
##dropped. PII in survey 2's raw export (IP address, GPS latitude/longitude, panel tokens p/rrq/k,
##3-digit postcode Q221, free-text Q189) is dropped; ResponseIds re-keyed.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) {  # drop Qualtrics header rows 2-3 (question text, ImportId) as records, not lines
  x <- fread(file.path(raw, f), colClasses = "character", encoding = "UTF-8")
  stopifnot(grepl("ImportId", x[[1]][2]))
  x[-(1:2)]
}
pick <- function(s, outs, t, p) {
  o <- data.table(choice_tmp = rep(NA_integer_, nrow(s)))
  for (nm in names(outs)) o[, (nm) := { v <- s[[outs[[nm]][t]]]; fifelse(v %in% c("1", "2"), as.integer(v == as.character(p)), NA_integer_) }]
  o[, choice_tmp := NULL]; o
}
## ---- survey 1
s <- rd("main_survey_final.csv")
s[, id := seq_len(.N)]
an1 <- c("university", "high_school", "job", "time_on_job", "incumbency", "father_job", "policy_position", "last_name", "gender")
o1 <- list(choice = c("Q26", "Q167", "Q172", "Q177", "Q182", "Q186", "Q189", "Q213"),
           choice_benefit_me = c("Q108_1", "Q169_1", "Q174_1", "Q179_1", "Q184_1", "Q187_1", "Q190_1", "Q214_1"),
           choice_benefit_prefecture = c("Q108_2", "Q169_2", "Q174_2", "Q179_2", "Q184_2", "Q187_2", "Q190_2", "Q214_2"),
           choice_benefit_japan = c("Q108_3", "Q169_3", "Q174_3", "Q179_3", "Q184_3", "Q187_3", "Q190_3", "Q214_3"))
tok <- function(x) trimws(gsub("\\$\\{e://Field/([a-z_]+)\\}", "[\\1]", x))
rows <- list()
for (t in 1:8) for (p in 1:2) {
  d <- data.table(id = s$id, task = t, profile = p, pick(s, o1, t, p))
  for (k in 1:9) d[, paste0("attr_", an1[k]) := tok(s[[sprintf("F-%d-%d-%d", t, p, k)]])]
  rows[[length(rows) + 1L]] <- d
}
d1 <- rbindlist(rows)[!is.na(choice)]
stopifnot(d1[, all(.SD != ""), .SDcols = patterns("^attr_")], !grepl("\\$|\\{|\\n", unlist(d1[, .SD, .SDcols = patterns("^attr_")])))
num <- function(x) suppressWarnings(as.integer(x))
lab <- function(x, l) unname(l[x])
pty <- c("1" = "自由民主党", "2" = "立憲民主党", "3" = "国民民主党", "4" = "公明党", "5" = "日本共産党", "6" = "日本維新の会",
         "7" = "社会民主党", "8" = "れいわ新選組", "9" = "その他の政治団体", "10" = "どの政党でもない", "99" = "わからない")
gen <- c("0" = "male", "1" = "female", "98" = "other")
ed1 <- c("1" = "小学校・中学校", "2" = "高等学校", "3" = "専修学校（専門学校）", "4" = "短大・高専", "5" = "大学", "6" = "大学院")
ed2 <- c("1" = "High School or Less", "2" = "Vocational School", "3" = "2 Year University", "4" = "4 Year University",
         "5" = "Graduate School")
stopifnot(all(s$Q37 %in% c(names(pty), "")), all(s$Q27 %in% c(names(gen), "99", "")), all(s$Q31_1 %in% c(names(ed1), "99", "")))
cv <- s[, .(id, cov_prefecture_code = num(Q35_1), cov_ideology = num(Q36_1), cov_party_id = lab(Q37, pty), cov_gender = lab(Q27, gen),
            cov_birth_year = num(Q28), cov_education = lab(Q31_1, ed1), cov_city_size = num(Q216), cov_duration_sec = num(duration),
            cov_finished = num(finished))]
d1 <- merge(d1, cv, by = "id")
for (v in names(o1)) stopifnot(d1[, sum(get(v)), .(id, task)][, all(V1 == 1, na.rm = TRUE)])
stopifnot(d1[, .N, .(id, task)][, all(N == 2)])
setcolorder(d1, c("id", "task", "profile", names(o1)))
setorder(d1, id, task, profile)
fwrite(d1, file.path(out, "gagnon_2025_local_candidates.csv"))
## ---- survey 2
s <- rd("follow_up.csv")
s[, id := seq_len(.N)]
o2 <- list(choice = c("Q20", "Q167", "Q172"))
iss <- c("business_attraction", "tourism", "public_works", "government_debt", "diplomacy", "pensions")
for (j in 1:6) o2[[paste0("choice_", iss[j])]] <- sprintf("Q%d_%d", 224:226, j)
o2$choice_prefecture_issues <- c("Q227", "Q228", "Q229")
fill <- function(x, s) {
  for (f in c("respondent_prefecture", "outside_prefecture", "university_local", "university_outside", "todai_kyodai"))
    x <- mapply(function(xx, val) gsub(paste0("${e://Field/", f, "}"), val, xx, fixed = TRUE), x, s[[f]], USE.NAMES = FALSE)
  trimws(gsub("\n", "", x))
}
for (t in 1:3) stopifnot(identical(sapply(1:4, function(k) paste(setdiff(unique(s[[sprintf("F.%d.%d", t, k)]]), ""), collapse = "|")),
                                     c("last_name", "local_status", "party", "time_on_job")))
rows <- list()
for (t in 1:3) for (p in 1:2) {
  d <- data.table(id = s$id, task = t, profile = p, pick(s, o2, t, p),
                  attr_last_name = s[[sprintf("F.%d.%d.1", t, p)]], attr_first_name = s[[sprintf("task_%d_profile_%d_name", t, p)]],
                  attr_local_status = fill(s[[sprintf("F.%d.%d.2", t, p)]], s), attr_party = s[[sprintf("F.%d.%d.3", t, p)]],
                  attr_time_on_job = s[[sprintf("F.%d.%d.4", t, p)]], pref = s$respondent_prefecture)
  rows[[length(rows) + 1L]] <- d
}
d2 <- rbindlist(rows)[!is.na(choice)]
stopifnot(d2[pref == "", uniqueN(id)] == 2)
d2 <- d2[pref != ""][, pref := NULL]
stopifnot(d2[, all(.SD != ""), .SDcols = patterns("^attr_")], !grepl("\\$|\\{", d2$attr_local_status), d2[, uniqueN(attr_local_status)] > 3)
stopifnot(all(s$Q42 %in% c(names(pty), "")), all(s$Q22 %in% c(names(gen), "99", "")), all(s$Q223 %in% c(names(ed2), "99", "")))
cv <- s[, .(id, cov_prefecture = respondent_prefecture, cov_party_id = lab(Q42, pty), cov_gender = lab(Q22, gen), cov_birth_year = num(Q24),
            cov_education = lab(Q223, ed2), cov_city_size = num(Q211), cov_duration_sec = num(Duration..in.seconds.), cov_finished = num(Finished))]
d2 <- merge(d2, cv, by = "id")
for (v in names(o2)) stopifnot(d2[, sum(get(v)), .(id, task)][, all(V1 == 1, na.rm = TRUE)])
stopifnot(d2[, .N, .(id, task)][, all(N == 2)])
setcolorder(d2, c("id", "task", "profile", names(o2)))
setorder(d2, id, task, profile)
fwrite(d2, file.path(out, "gagnon_2025_local_status.csv"))
