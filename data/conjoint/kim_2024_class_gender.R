##Candidate class x gender paired conjoints (US and UK) from
##Kim, J. H., & Kweon, Y. (2024). Double penalty? How candidate class and gender influence voter
##evaluations. Research & Politics, 11(1). https://doi.org/10.1177/20531680241226511
##Replication data: Harvard Dataverse doi:10.7910/DVN/EWQKH3, CC0 1.0, no restricted files.
##Files read: Working-Class+Women+Conjoint_October+13,+2021_13.12.csv (US raw Qualtrics export,
##saved as us.csv) and Working-Class+Women+Conjoint+-+UK_February+9,+2022_03.16.tab (original csv,
##saved as uk.csv), each with the question-text and ImportId header rows; Readme.txt. The authors'
##US_analysis_Submission.R, UK_analysis_Submission.R and "appendix code.R" read as text, not run.
##Usage: Rscript kim_2024_class_gender.R <raw dir> <output dir>
##
##TWO TABLES (separate samples, analysed separately by the authors, US and UK wording differs):
##  kim_2024_class_gender_us: Lucid US sample, October 2021; 865 respondents answered the conjoint.
##  kim_2024_class_gender_uk: Prolific UK sample, February 2022; 975 respondents.
##(The appendix summary tables count 939 US / 992 UK attention-check passers, the denominator of
##the whole survey; respondents who saw no conjoint or answered none of it have no rows here.)
##Design: 3 tasks, each two hypothetical candidates (US: candidates in the respondent's party's
##congressional primary; respondents who chose Democrat saw blocks Q5-Q7 "Democratic Party's
##congressional primary", Republicans blocks Q8-Q10; independents/others were routed by the forced
##lean Q3.4; trial_primary = Democratic / Republican) or MPs (UK: "MPs from your party"). Five
##attributes from the Qualtrics conjoint export F-<task>-<attr> (attribute name in row position)
##and F-<task>-<profile>-<attr> (level, as displayed): Gender (Female/Male), Age (30/40/50/60),
##Education (High school graduate / College graduate [US] or University graduate [UK] /
##Post-graduate (Master or Doctoral degree)), Former Occupation (Janitor / Retail clerk / Lawyer /
##Business entrepreneur), Years in Politics (0/1/3/8). Attribute row order randomized once per
##respondent (identical across a respondent's tasks; attrpos_ = row 1-5). Task = F index, which the
##authors' read.qualtrics calls pair with Q5/Q6/Q7 (Q8/Q9/Q10) in order. Profile 1 = "Candidate/MP 1".
##Outcomes, all picks of one of the two profiles (no opt-out offered; a skipped item is NA on both
##profiles). US wording ("candidates"); UK uses "Based on the limited information above, which of
##the two MPs ...":
##  choice                  Q.3 "Based on the profiles above, which of the two candidates would you be
##                          more likely to support in this [Democratic/Republican] Party's congressional
##                          primary?" (UK: "would you prefer to have as your MP?")
##  choice_relate           Q.4 "... which of the two candidates can you relate to more?"
##  choice_represent_<grp>  Q.5_1-5 "... which of the two candidates do you think will better represent
##                          the following constituents?" women / low_income / whites / minorities /
##                          immigrants
##  choice_advocate_<issue> Q.6_1-7 "... which of the two candidates do you think will do a better job
##                          advocating for the following issues?" economy / welfare / family /
##                          gender_equality / racial_equality / health / education
##  choice_top_issue        Q.7 "You chose [issue] as the most important policy issue to you. Based on the
##                          profiles above, which of the two candidates do you think will do a better job
##                          advocating for that issue?" (the authors' "competency" outcome)
##Codes 1/2 = candidate 1/2; in the UK export the represent items are coded 1/4 (Qualtrics recode),
##4 = MP 2: checked against the advocate items (e.g. represent-women 4 goes with gender-equality 2 in
##403 of 481 tasks). The authors analyse only choice (Q.3) and choice_top_issue (Q.7).
##Covariates (codes, no codebook in the deposit unless stated): cov_party_id_code (Q3.1; US options
##asked as Democrat, Republican, independent, or what), cov_party_lean_code (US Q3.4),
##cov_top_issue_code (Q4.1), cov_education (US Q11.3 mapped by the authors' appendix code: 1 less than
##high school, 2 high school, 3 some college, 6 college, 7 graduate degree; UK cov_education_code),
##cov_gender_code (Q11.6; 3 = Other per the export's "Other - Text" column; 1/2 order not documented),
##cov_age (US: the panel's age variable; UK: Q11.15_1 typed age, kept only for whole numbers 18-100),
##cov_interest (Q11.5_1, 1-7).
##PII in the deposit, DROPPED: IP addresses, location latitude/longitude, Lucid rid and ZIP code (US),
##Prolific IDs (UK Q124), free-text occupation/job position and all *_TEXT fields; ResponseIds re-keyed
##to integers in file order. Also dropped: the authors' derived Pink-Collar / Working-Class flags,
##the remaining survey items (economic perceptions, spending, ...), Lucid demographic codes other
##than age. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c(Gender = "gender", Age = "age", Education = "education", "Former Occupation" = "occupation",
           "Years in Politics" = "years_in_politics")
items <- c("3" = "choice", "4" = "choice_relate", "5_1" = "choice_represent_women", "5_2" = "choice_represent_low_income",
           "5_3" = "choice_represent_whites", "5_4" = "choice_represent_minorities", "5_5" = "choice_represent_immigrants",
           "6_1" = "choice_advocate_economy", "6_2" = "choice_advocate_welfare", "6_3" = "choice_advocate_family",
           "6_4" = "choice_advocate_gender_equality", "6_5" = "choice_advocate_racial_equality",
           "6_6" = "choice_advocate_health", "6_7" = "choice_advocate_education", "7" = "choice_top_issue")
build <- function(r, blocks, uk) {
  r <- r[-(1:2)]
  r[, id := .I]
  L <- list()
  for (bl in names(blocks)) for (t in 1:3) {
    q <- blocks[[bl]][t]
    ans <- as.data.table(lapply(names(items), function(i) r[[paste0("Q", q, ".", i)]]))
    setnames(ans, items)
    has <- ans[, rowSums(.SD != "") > 0]
    if (!any(has)) next
    for (p in 1:2) {
      d <- data.table(id = r$id[has], task = t, profile = p, trial_primary = bl)
      for (it in items) {
        v <- ans[[it]][has]
        stopifnot(v %in% c("", "1", "2", "4"))
        if (!uk) stopifnot(v %in% c("", "1", "2"))
        v2 <- ifelse(v == "", NA_integer_, as.integer(v %in% c(if (p == 1) "1" else c("2", "4"))))
        d[, (it) := v2]
      }
      for (k in 1:5) {
        nm <- r[[paste0("F-", t, "-", k)]][has]; lv <- r[[paste0("F-", t, "-", p, "-", k)]][has]
        stopifnot(nm %in% names(attrs), lv != "")
        for (an in names(attrs)) {
          w <- nm == an
          if (k == 1) { d[, paste0("attr_", attrs[an]) := NA_character_]; d[, paste0("attrpos_", attrs[an]) := NA_integer_] }
          d[w, paste0("attr_", attrs[an]) := lv[w]]; d[w, paste0("attrpos_", attrs[an]) := k]
        }
      }
      L[[length(L) + 1]] <- d
    }
  }
  d <- rbindlist(L)
  stopifnot(!anyNA(d[, grep("^attr", names(d)), with = FALSE]), d[, .N, .(id, task)][, all(N == 2)],
            d[, .N, .(id, task, profile)][, all(N == 1)])
  for (it in items) stopifnot(d[, .(s = sum(get(it))), .(id, task)][, all(is.na(s) | s == 1)])
  # attribute order fixed within respondent
  stopifnot(d[, uniqueN(paste(attrpos_gender, attrpos_age, attrpos_education, attrpos_occupation, attrpos_years_in_politics)), id][, all(V1 == 1)])
  int <- function(x) suppressWarnings(as.integer(x))
  cv <- r[, .(id, cov_party_id_code = int(Q3.1), cov_top_issue_code = int(Q4.1), cov_gender_code = int(Q11.6),
              cov_interest = int(Q11.5_1))]
  if (!uk) {
    cv[, cov_party_lean_code := int(r$Q3.4)]
    ed <- c("1" = "less than high school", "2" = "high school", "3" = "some college", "6" = "college", "7" = "graduate degree")
    stopifnot(r$Q11.3 %in% c("", names(ed)))
    cv[, cov_education := unname(ed[r$Q11.3])]
    cv[, cov_age := int(r$age)]
  } else {
    cv[, cov_education_code := int(r$Q11.3)]
    ag <- int(r$Q11.15_1)
    cv[, cov_age := ifelse(!is.na(ag) & ag >= 18 & ag <= 100, ag, NA_integer_)]
  }
  d <- merge(d, cv, by = "id")
  if (uk) d[, trial_primary := NULL]
  d[, id := match(id, sort(unique(id)))]
  setorder(d, id, task, profile)
  d
}
us <- fread(file.path(raw, "us.csv"), colClasses = "character", header = TRUE, encoding = "UTF-8")
uk <- fread(file.path(raw, "uk.csv"), colClasses = "character", header = TRUE, encoding = "UTF-8")
dus <- build(us, list(Democratic = 5:7, Republican = 8:10), FALSE)
duk <- build(uk, list(MP = 5:7), TRUE)
stopifnot(uniqueN(dus$id) == 865L, uniqueN(duk$id) == 975L)
fwrite(dus, file.path(out, "kim_2024_class_gender_us.csv"))
fwrite(duk, file.path(out, "kim_2024_class_gender_uk.csv"))
