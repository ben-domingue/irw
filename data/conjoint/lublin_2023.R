##Two candidate experiments from the 2021 online survey in
##Lublin, D., & Wright, M. (2023). Diversity matters: The election of Asian Americans to U.S. state and federal
##legislatures. American Political Science Review. https://doi.org/10.1017/S0003055423000242
##Replication data: Harvard Dataverse doi:10.7910/DVN/NYOXTE, CC0 1.0. Files read: 2021 Online Survey.tab (the Stata
##original with value labels, saved as s.dta), Survey Analyses Code.do and Supplementary Materials.pdf (Table 8: vignette
##wording and randomization logic) as text. The observational legislator files are not used.
##Usage: Rscript lublin_2023.R <dir holding s.dta> <output dir>
##
##2,503 US adults (online panel quota sample, 2021: 502 White, 501 Black, 1,000 Asian, 500 Hispanic). Two experiments:
##(1) lublin_2023_candidate_vignette: ONE text vignette per respondent of "Michael [surname]", a congressional
##  candidate; factors = ethnic identity bundle (9 levels: Chinese, Indian, Filipino, Japanese, Korean, Vietnamese,
##  English, Nigerian, Mexican; surname, parents' country of origin, ethnic roots and pan-ethnic identity move together,
##  "not allowed to vary independently", Suppl. Table 8) x career background (2). Outcomes (strongly disagree 0 ...
##  strongly agree 4; "Don't know" 98 set to NA, not a rating): rating_understands_issues "[Michael S.] is the kind of
##  candidate that understands the political issues that matter to me.", rating_represent_well "If he won, Michael S.
##  would represent my district well in Congress.", rating_more_like_him "I would like to see more people like Michael S.
##  in Congress." (Suppl. Table 8). The ethnicity draw is CONDITIONAL on the respondent's group (Asian respondents: same
##  origin / different Asian origin / White, Black or Latino candidate; non-Asian respondents: same ethnicity / Asian /
##  different ethnicity candidate; stored as trial_ethnicity_assignment from the deposit's picker labels), so the level
##  shares depend on the respondent: restrictions = yes. Level text for the displayed vignette is taken from Suppl.
##  Table 8 (the deposit stores codes with short value labels).
##(2) lublin_2023_candidate_pairs: 5 head-to-head comparisons (pairs A-E) of two candidates with 7 attributes (ethnicity,
##  career, gender, incumbency, prior elected office, party, political views); choice = which candidate the
##  respondent prefers, with a "No Preference" answer (9) = opt-out (both profiles 0). Question wording is only a
##  truncated variable label in the deposit ("Now, imagine that the two candidates below are running against ...":
##  paraphrase). Candidate 1X = profile 1 = "Candidate A" and 2X = profile 2 = "Candidate B" is INFERRED from the
##  answer labels (Candidate A=1, Candidate B=0) -> profile_source inferred. Ethnicity levels are the deposit's value
##  labels ("Chinese-American" ...), drawn conditionally on the respondent's group as above; other attributes use the
##  value labels. Attribute order is not documented. OBSERVED restrictions (no source states them): every pair has one
##  Democrat and one Republican and one incumbent and one challenger; political views never pair Liberal-Liberal or
##  Conservative-Conservative (Moderate is about half of all profiles).
##Covariates (both tables): cov_gender (survey labels Male/Female/Non-binary -> male/female/other), cov_age (typed
##years), cov_education (answer text), cov_party_id7 (7-point party id text; "Other" and "No preference" kept as
##answer text), cov_respondent_ethnicity (quota group), cov_asian_origin (Asian respondents only, answer text).
##PII FOUND: panelist ID (QPID, hashed string; dropped), other panel/vendor fields dropped. Dropped: income, religion,
##importance and derived index/dummy variables, "Aggregates" files.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "s.dta")))
stopifnot(nrow(x) == 2503)
lab <- function(v) { l <- attr(x[[v]], "labels"); function(z) names(l)[match(as.numeric(z), l)] }
cv <- data.table(cov_gender = c(`Male` = "male", `Female` = "female", `Non-binary` = "other")[lab("QGENDER")(x$QGENDER)],
  cov_age = as.integer(x$QAGE), cov_education = lab("QEDUCATION")(x$QEDUCATION),
  cov_party_id7 = lab("QPOLITICAL_PARTY_PREFERENCE")(x$QPOLITICAL_PARTY_PREFERENCE),
  cov_respondent_ethnicity = lab("QETHNICITY_QUOTA")(x$QETHNICITY_QUOTA), cov_asian_origin = lab("QASIAN_ORIGIN")(x$QASIAN_ORIGIN))
cv[cov_asian_origin == "Other, specify: QASIAN_ORIGIN_7_OTH", cov_asian_origin := "Other"]
cv[!(cov_age >= 18 & cov_age <= 100), cov_age := NA_integer_]
## (1) vignette
eth <- data.table(code = 1:9,
  txt = c("Huang; parents immigrated from China; Chinese roots; Asian-American identity",
          "Patel; parents immigrated from India; Indian roots; Asian-American identity",
          "Reyes; parents immigrated from The Philippines; Filipino roots; Asian-American identity",
          "Tanaka; parents immigrated from Japan; Japanese roots; Asian-American identity",
          "Park; parents immigrated from Korea; Korean roots; Asian-American identity",
          "Pham; parents immigrated from Vietnam; Vietnamese roots; Asian-American identity",
          "Smith; parents immigrated from England; English roots; Anglo-American identity",
          "Jones; parents immigrated from Nigeria; Nigerian roots; African-American identity",
          "Ramirez; parents immigrated from Mexico; Mexican roots; Hispanic-American identity"))
bg <- c("worked for several years as a community organizer after graduating. He has spent the last three years on his local city council, devoting most of his energy toward protecting workers' rights and raising the minimum wage",
        "worked for several years running his family's restaurant after graduating. He has spent the last three years on his local city council, devoting most of his energy toward reducing regulations on small business in order to create jobs")
stopifnot(all(as.numeric(x$QCANDETH) %in% 1:9), all(as.numeric(x$QCANDBACKGROUND) %in% 1:2))
chk <- as.numeric(x$QCANDSURNAME) == as.numeric(x$QCANDETH); stopifnot(all(chk))
dk <- function(z) { z <- as.numeric(z); z[z == 98] <- NA; z }
v <- cbind(data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L,
  rating_understands_issues = dk(x$QVIGRESPRUNDERSTANDSISSUES), rating_represent_well = dk(x$QVIGRESPRIFWON),
  rating_more_like_him = dk(x$QVIGRESPRMOREPEOPLE),
  attr_ethnic_identity = eth$txt[as.numeric(x$QCANDETH)], attr_career_background = bg[as.numeric(x$QCANDBACKGROUND)]), cv,
  data.table(trial_ethnicity_assignment = lab("QCANDETH_PICKER")(x$QCANDETH_PICKER)))
v[, rating := rating_understands_issues]; v[, rating_understands_issues := NULL]  # rating = the "understands issues" item
setcolorder(v, c("id", "task", "profile", "rating"))
v <- v[!(is.na(rating) & is.na(rating_represent_well) & is.na(rating_more_like_him))]
setorder(v, id, task, profile)
fwrite(v, file.path(out, "lublin_2023_candidate_vignette.csv"))
## (2) pairs
P <- list()
for (k in 1:5) { L <- LETTERS[k]
  pref <- as.numeric(x[[paste0("QCANDPREF", L)]])
  for (p in 1:2) {
    g <- function(stem) x[[paste0(stem, p, L)]]
    ch <- fifelse(pref == 9, 0L, fifelse(pref == ifelse(p == 1, 1, 0), 1L, 0L))
    P[[length(P) + 1]] <- data.table(id = seq_len(nrow(x)), task = k, profile = p, choice = ch,
      attr_ethnicity = lab(paste0("QETHBACK", p, L))(g("QETHBACK")),
      attr_career = lab(paste0("QCAREERBACK", p, L))(g("QCAREERBACK")),
      attr_gender = lab(paste0("QGENDER", p, L))(g("QGENDER")),
      attr_incumbency = lab(paste0("QINCUMB", p, L))(g("QINCUMB")),
      attr_prior_elected_office = lab(paste0("QEXPERIENCE", p, L))(g("QEXPERIENCE")),
      attr_party = lab(paste0("QPARTY", p, L))(g("QPARTY")),
      attr_political_views = lab(paste0("QPOLVIEWS", p, L))(g("QPOLVIEWS")))
  } }
P <- rbindlist(P)
stopifnot(!anyNA(P), P[, sum(choice), .(id, task)][, all(V1 <= 1)])
P <- merge(P, cbind(data.table(id = seq_len(nrow(x))), cv), by = "id")
setorder(P, id, task, profile)
fwrite(P, file.path(out, "lublin_2023_candidate_pairs.csv"))
cat(nrow(v), uniqueN(v$id), nrow(P), uniqueN(P$id), "\n")
