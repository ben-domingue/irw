##COVID-19 vaccination-combination conjoint (Japan), two samples, from
##Ohmura, H. (2022). Analysis of social combinations of COVID-19 vaccination: Evidence from a
##conjoint analysis. PLOS ONE, 17(1), e0261426. https://doi.org/10.1371/journal.pone.0261426
##Replication data: Harvard Dataverse doi:10.7910/DVN/YU7CC1, CC0 1.0, no restricted files, no
##terms. Files read: covid19_normal.csv (Yahoo! Crowdsourcing sample; Dataverse original format)
##and covid19_lucid.csv (Lucid sample; Qualtrics legacy export whose first data row holds the
##question text in Shift-JIS/CP932, decoded here). The author's covid_conjoint.R,
##covid_conjoint_yahoo.R and covid_conjoint_lucid.R were read as text (attribute list); the
##article (open access) gives the design. covid_cj.csv (actually an .xlsx: the author's
##cjoint::read.qualtrics output after na.omit) is not used.
##Usage: Rscript ohmura_2022.R <dir holding the two csv files> <output dir>
##
##Design (article, "Design of the conjoint analysis"): respondents first pick a "familiar
##presence" (older family member, younger family member, friend, colleague, neighbour, spouse,
##significant other) and keep it in mind; then 5 paired tasks, each profile a "situation" with 3
##attributes, each with the same 3 levels: myself, familiar (the familiar presence) and society
##(society as a whole) x vaccinate / do not vaccinate now, vaccinate later / not vaccinate.
##Conjoint Survey Design Tool + Qualtrics; Qualtrics F-<task>-<profile>-<row> fields give the
##level text and F-<task>-<row> the attribute in each row, so task, profile and attribute row
##position are RECORDED. Attribute order is randomized once per respondent (identical across a
##respondent's 5 tasks, checked) -> attrpos_*. Level text: the export holds the author's English
##strings ("vaccinate", "not vaccinate", "wait and see"; "wait and see" = the article's "Do not
##vaccinate now, vaccinate later"); respondents saw Japanese (article: questionnaire "presented
##in Japanese"). The author seems to have replaced Japanese strings with English throughout the
##export (the question text itself reads "...最もfamiliarは..."), so these are the author's
##labels, not displayed text.
##Outcome: choice, forced choice between the two situations. Wording (Lucid question-text row,
##verbatim; "Choice 1"/"Choice 2" as exported): "以下に2つの選択肢を挙げさせていただきます。
##あなたにとって、以下の2つの状況のうちどちらが望ましいですか。 Choice 1とChoice 2のうち、どちらか一つを
##お選びください。" ("Two options are listed below. For you, which of the following two
##situations is more desirable? Please choose one of Choice 1 and Choice 2.", translated). YCS
##Q20.1-Q20.5 / Lucid Q11.1-Q11.5, coded 1/2 = profile chosen. No opt-out.
##Separate tables per sample (separate fieldings, analysed separately in the article):
##  ohmura_2022_covid_vaccination_ycs: Yahoo! Crowdsourcing, 14-16 March 2021; article 2,975
##    participants; the file has 2,971 rows, 37 without conjoint fields (dropped) -> 2,934.
##  ohmura_2022_covid_vaccination_lucid: Lucid, 26-28 March 2021; article 1,024; the file has
##    1,222 respondents, 198 without conjoint fields (dropped) -> 1,024 (matches).
##Tasks with no answer are dropped (rows with no outcome are omitted; YCS 232-336 per task), so
##YCS keeps 2,848 respondents with at least one answered task.
##Covariates: cov_familiar_entity (the familiar presence picked: YCS Q19.1, Lucid Q10, text as
##exported, e.g. "older familiar"/"older family"), cov_age (YCS Q2.2 / Lucid `age`, the
##free-entry age "in half-width digits": kept only when it is a whole number 18-110; other entries -- 0,
##full birth dates such as 19750618, other digit strings and text -- are set to NA, so no date of birth is stored), cov_gender_code (YCS Q2.1 / Lucid `gender`) and
##cov_education_code (Q2.4): codes kept, as no deposited source maps them. Prefecture (Q2.3) and
##the free-text Q2.6_11_TEXT are not kept.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(s, resp, fam, gen, age, name) {
  s <- s[get("F-1-1") != "" & !is.na(get("F-1-1"))]
  stopifnot(s[, all(get("F-1-1") == get("F-5-1") & get("F-1-2") == get("F-5-2"))])
  d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
    o <- data.table(src = s$ID, task = t, profile = p, ch = as.integer(s[[resp[t]]]))
    for (k in 1:3) {
      an <- s[[sprintf("F-%d-%d", t, k)]]; lv <- s[[sprintf("F-%d-%d-%d", t, p, k)]]
      for (at in c("myself", "familiar", "society")) {
        o[an == at, paste0("attr_", at) := lv[an == at]]
        o[an == at, paste0("attrpos_", at) := k]
      }
    }
    o[, cov_familiar_entity := fifelse(s[[fam]] == "", NA_character_, s[[fam]])]
    o[, cov_age := { a <- suppressWarnings(as.integer(ifelse(grepl("^[0-9]{1,3}$", s[[age]]), s[[age]], NA))); fifelse(!is.na(a) & a >= 18 & a <= 110, a, NA_integer_) }]
    o[, cov_gender_code := suppressWarnings(as.integer(s[[gen]]))]
    o[, cov_education_code := suppressWarnings(as.integer(s$Q2.4))]
    o
  }))))
  d <- d[!is.na(ch)]
  stopifnot(all(d$ch %in% 1:2), d[, .N, .(src, task)][, all(N == 2)],
            d[, !anyNA(.SD), .SDcols = patterns("^attr")], d[, all(attr_myself %in% c("vaccinate", "not vaccinate", "wait and see"))])
  d[, choice := as.integer(ch == profile)]
  d[, id := as.integer(src)]
  setcolorder(d, c("id", "task", "profile", "choice"))
  d[, c("src", "ch") := NULL]
  setorder(d, id, task, profile)
  cat(name, nrow(d), uniqueN(d$id), "\n")
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
y <- fread(file.path(raw, "covid19_normal.csv"), colClasses = "character")
stopifnot(nrow(y) == 2971)
build(y, paste0("Q20.", 1:5), "Q19.1", "Q2.1", "Q2.2", "ohmura_2022_covid_vaccination_ycs")
l <- fread(file.path(raw, "covid19_lucid.csv"), colClasses = "character")
l <- l[-1]  # question-text row
stopifnot(nrow(l) == 1222)
build(l, paste0("Q11.", 1:5), "Q10", "gender", "age", "ohmura_2022_covid_vaccination_lucid")
