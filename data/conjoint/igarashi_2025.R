##Discrimination-judgement factorial vignette experiment (Japan, human respondents) from
##Igarashi, A., Kano, Y., & Miwa, H. (2025). ChatGPT versus humans in judging discriminatory
##scenarios: experimental evidence from a Japanese context. Humanities and Social Sciences
##Communications, 12, 1776. https://doi.org/10.1057/s41599-025-06054-6
##Replication data: Harvard Dataverse doi:10.7910/DVN/PTON99, CC0 1.0. Files read: human_data.tab
##(Dataverse "original format" download, human_data.csv) and codebook.pdf (codes of Q.x, rating.x,
##C, gender, edu, pref). The ChatGPT output files (GPT_4_data etc.) are not human responses and are
##not used.
##Usage: Rscript igarashi_2025.R <dir holding human_data.csv> <output dir>
##
##4,000 Japanese residents aged 18-69 (Lucid Marketplace, 18-22 Jan 2024, quotas on gender x age,
##education, region; those failing an instructional manipulation check were screened out before the
##experiment). Each read 4 single vignettes (tasks 1-4, profile = 1) about a hypothetical 25-year-old
##"A"/"B"/"C"/"D" who was rejected for a job (public sphere) or treated coldly in a board game club
##(private sphere), and rated it. 40 possible scenarios = 4 targets x 2 group status x 5
##sphere/mechanism. Each target (gender, nationality, sexuality, education) appeared exactly once per
##respondent in random order; status and sphere/mechanism were "independently randomised" (article,
##Data and methods + footnote 12). Q.x (task x) is the authors' scenario code 1-40 (codebook).
##Outcome: rating = rating.x, how likely the described scenario was to be considered discriminatory,
##6-point, 1 "Almost certainly not discriminatory" ... 6 "Almost certainly discriminatory" (codebook;
##higher = more discriminatory). Exact Japanese question wording is in the article's Supplementary
##Information A (not read); the wording stored is the article's paraphrase. No missing ratings.
##Attribute text. Respondents saw Japanese prose; the deposit holds only the scenario code. The
##attr_ columns hold the article's English translation of the bracketed phrases inserted into the
##vignette templates (article Tables 1 and 2, "Randomised phrases"), filled in from the code:
##  attr_sphere       which template: "rejected job application at a private company" (public) or
##                    "treated coldly in a board game club" (private) -- a label for the template,
##                    not displayed text; the template wording is in the article.
##  attr_nationality  [a] Japanese / Chinese
##  attr_gender       [b] male / female
##  attr_university   [c] a university / the University of Tokyo (UTokyo) / a newly established
##                    private university (NEPU)
##  attr_disclosure   [d] (public) or [f] (private) phrase about living with a partner of the
##                    opposite/same sex; shown only in sexuality scenarios, else "(not shown)"
##  attr_reason       [e] with [g]/[h]/[i] substituted (public: taste-based, stereotype, statistical,
##                    customer needs); private: "the person generally dislikes [g]" (template text)
##The authors' design factors (codebook/analysis code labels) are kept as trial_target (gender,
##nationality, sexuality, education), trial_status (advantaged/disadvantaged; replication_code_main.R
##L120-123 coding) and trial_mechanism (taste-based, stereotypical, statistical, customer needs,
##private). The between-respondent instruction arm C (definition of discrimination: None, Minimal,
##Detailed; codebook) is trial_definition.
##Restrictions: YES by design. Target drawn without repetition across the 4 tasks; the displayed
##phrases are fixed functions of target x status (e.g. "Chinese" only in a disadvantaged nationality
##scenario, the disclosure phrase only in sexuality scenarios); the private sphere has no mechanism.
##Covariates (codebook): cov_gender (1 Man = male, 2 Woman = female, 3 Non-binary/third gender =
##other, 4 Prefer not to say = NA), cov_age (years), cov_education (edu, the codebook's English text;
##the Japanese answer text is not deposited), cov_prefecture (pref, codebook English name).
##Dropped: the open-ended reason texts text.1-text.4 (free text). No survey weight in the deposit.
##No platform IDs in the file; id = row number of human_data.csv (as the authors' code does).
##Count check: 4,000 respondents x 4 = 16,000 ratings, as in the article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
h <- fread(file.path(raw, "human_data.csv"), encoding = "UTF-8")
stopifnot(nrow(h) == 4000)
h[, id := .I]
L <- rbindlist(lapply(1:4, function(t) h[, .(id, task = t, Q = get(paste0("Q.", t)), rating = get(paste0("rating.", t)),
                                              C, gender, age, edu, pref)]))
stopifnot(all(L$Q %in% 1:40), all(L$rating %in% 1:6))
L[, target := c("gender", "nationality", "sexuality", "education")[(Q - 1L) %/% 10L + 1L]]
stopifnot(L[, uniqueN(target), id][, all(V1 == 4)])
L[, status := fifelse(target %in% c("gender", "education"), fifelse(Q %% 2L == 1L, "advantaged", "disadvantaged"),
                      fifelse(Q %% 2L == 0L, "disadvantaged", "advantaged"))]
L[, mech := c("taste-based", "taste-based", "stereotypical", "stereotypical", "statistical", "statistical",
              "customer needs", "customer needs", "private", "private")[(Q - 1L) %% 10L + 1L]]
# article Table 1: phrases [a] [b] [c] [d] [f] [g] [h] [i] by target x status
T1 <- data.table(
  target = rep(c("gender", "nationality", "sexuality", "education"), each = 2),
  status = rep(c("advantaged", "disadvantaged"), 4),
  a = c("Japanese", "Japanese", "Japanese", "Chinese", "Japanese", "Japanese", "Japanese", "Japanese"),
  b = c("male", "female", "male", "male", "male", "male", "male", "male"),
  c = c(rep("a university", 6), "the University of Tokyo (UTokyo)", "a newly established private university (NEPU)"),
  d = c(rep(NA, 4), "while he had told the hiring manager that he was living with a partner of the opposite sex during the interview,",
        "while he had told the hiring manager that he was living with a partner of the same sex during the interview,", NA, NA),
  f = c(rep(NA, 4), "is open about living with a partner of the opposite sex and", "is open about living with a partner of the same sex and", NA, NA),
  g = c("men", "women", "Japanese", "Chinese", "heterosexuals", "homosexuals", "those who graduated from the UTokyo", "those who graduated from an NEPU"),
  hh = c("women", "men", "those of other nationalities", "those of other nationalities", "homosexuals", "heterosexuals",
         "those who graduated from other universities", "those who graduated from other universities"),
  i = c("female", "male", "non-Japanese", "non-Chinese", "homosexual", "heterosexual", "non-UTokyo-graduate", "non-NEPU-graduate"))
L <- merge(L, T1, by = c("target", "status"), all.x = TRUE)
stopifnot(!anyNA(L$a))
L[, reason := fcase(
  mech == "taste-based", paste("the hiring manager generally disliked", g),
  mech == "stereotypical", paste("the hiring manager believed that", g, "tend to perform worse than", hh, "in the workplace"),
  mech == "statistical", paste("the company's employee performance statistics showed that", g, "tend to perform worse than", hh,
                               "in the workplace, and the hiring manager made the decision based on those statistics"),
  mech == "customer needs", paste("the job opening was for a staff member to assist", i, "customers, and the company prioritised", i,
                                  "applicants to meet the needs of its customers"),
  mech == "private", paste("the person generally dislikes", g))]
L[, disclosure := fifelse(target != "sexuality", "(not shown)", fifelse(mech == "private", f, d))]
preflab <- c("Aichi", "Akita", "Aomori", "Chiba", "Ehime", "Fukui", "Fukuoka", "Fukushima", "Gifu", "Gunma", "Hiroshima", "Hokkaido",
          "Hyogo", "Ibaraki", "Ishikawa", "Iwate", "Kagawa", "Kagoshima", "Kanagawa", "Kochi", "Kumamoto", "Kyoto", "Mie", "Miyagi",
          "Miyazaki", "Nagano", "Nagasaki", "Nara", "Niigata", "Oita", "Okayama", "Okinawa", "Osaka", "Saga", "Saitama", "Shiga",
          "Shimane", "Shizuoka", "Tochigi", "Tokushima", "Tokyo", "Tottori", "Toyama", "Wakayama", "Yamagata", "Yamaguchi", "Yamanashi")
edulab <- c("Junior high school", "High school", "Technical college", "Vocational school", "Junior college", "University",
         "Graduate school (Master's course)", "Graduate school (Doctoral course)")
stopifnot(all(L$gender %in% 1:4), all(L$edu %in% 1:8), all(L$pref %in% 1:47), all(L$C %in% 1:3))
d <- L[, .(id, task = as.integer(task), profile = 1L, rating = as.integer(rating),
           attr_sphere = fifelse(mech == "private", "treated coldly in a board game club", "rejected job application at a private company"),
           attr_nationality = a, attr_gender = b, attr_university = c, attr_disclosure = disclosure, attr_reason = reason,
           trial_target = target, trial_status = status, trial_mechanism = mech,
           trial_definition = c("None", "Minimal", "Detailed")[C],
           cov_gender = c("male", "female", "other", NA)[gender], cov_age = as.integer(age),
           cov_education = edulab[edu], cov_prefecture = preflab[pref])]
stopifnot(nrow(d) == 16000, !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "igarashi_2025_discrimination_judgement.csv"))
