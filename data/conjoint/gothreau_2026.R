##Twenty-country candidate-gender conjoint from
##Gothreau, C., & Laustsen, L. (2026). Women and left-wing citizens prefer women candidates:
##Testing consistency and psychological processes across twenty diverse countries. Public Opinion
##Quarterly, 90(SI), 989-1016. https://doi.org/10.1093/poq/nfag045
##Replication data: Harvard Dataverse doi:10.7910/DVN/UEVNRJ, CC0 1.0, no restricted files.
##File read: WIDE_Full_Launch_DV.dta (one row per respondent; Stata variable and value labels).
##The 689 MB LONG_Full_Launch_DV.dta is derived from it and not read. Read Me.pdf and the
##authors' R scripts (read as text, not run) for the recodes; design facts from the article.
##Usage: Rscript gothreau_2026.R <raw dir> <output dir>
##
##14,369 respondents (article N) from YouGov panels (Japan NRC; Kenya, Nigeria, Lithuania,
##Ukraine CINT; South Africa KLA) in 20 countries, Nov 2022-Feb 2024. 45 have no conjoint data
##(all attribute and vote columns empty) and are dropped: 14,324. ONE TABLE with cov_country:
##the authors pool all countries (country fixed effects, with by-country estimates) and the
##deposit stores one English label set for every country. Respondents saw the instrument in
##their country's language; attr_ text is the English label (label_language en).
##Fieldings (trial_wave): "main" (19 countries Feb-May 2023, plus the 518-person US soft launch,
##FirstUS = 1); "us_wave2" (2,656 US respondents, Nov-Dec 2023, FirstUS = 0); "followup_2024"
##(Germany 504, Indonesia 509, Turkey 509, Feb 2024). The article: attribute order was fixed by
##a programming error except in the US wave 2 and the 2024 follow-ups, which randomized it
##(trial_attr_order = the source attr_order string, e.g. "[3, 1, 5, 7, 4, 2, 6]", recorded for
##those respondents only; its mapping to attributes is not documented, so no attrpos_ columns).
##trial_office: "national" / "local" (Splitsample_conj; the prompt piped in "the (lower house of
##the) national legislature" or "a municipal or local office"); blank for US wave 2, which had no
##office split.
##Design: 7 tasks of 2 candidates (Q1_taskeen<t>: Candidate 1/2 .. 13/14 -> task 1-7, profile
##1-2). The article body says seven rounds; its appendix says six (data have seven).
##Outcome: choice = "Which candidate would you support?" (article), forced, no opt-out.
##Attributes (Stata value labels; ENGLISH text): gender Male/Female; age 30, 31, 32, 45, 46, 47,
##65, 66, 67 (the authors bin to 30-32/45-47/65-67); political experience 0 Years / 1 Year /
##2 Years / 4 Years / 5 Years / 10 Or More Years (source codes 1-2 both "0 Years", 7-8 both
##"10 Or More Years", so those levels had double weight; the authors bin to 0/1-2/4-5/10+);
##children 0-4; ideology Left Wing/Moderate/Right Wing; occupation Lawyer or Legal Field /
##Business or Finance (each two source codes, double weight) / Teacher / Public Servant; origin
##"Born and Raised" / "Immigrated" (the authors' wording: the stored label names one country,
##India, but respondents saw their own country; ~86% born and raised).
##Covariates: cov_country; cov_female 1 = Female 2 = Male (source `female`); cov_age; cov_highered
##0/1; cov_dominant_ethnicity 0/1; cov_left_right 0 = Left .. 10 = Right, 97 = prefer not to say
##(respideologyx1; missing in US wave 2); cov_attention_check 1 = passed; cov_factcheck_passed
##(local/national manipulation check, missing where not asked); cov_asi_benevolent1-4,
##cov_asi_hostile1-4 (ambivalent sexism items, codes as deposited); cov_masculine, cov_feminine
##(Contgender_1/2, 0-10 self-rated masculinity/femininity); cov_survey_weight (`weight`).
##Spot check: weighted LPM of choice on all attributes + country fixed effects gives female
##+0.030, the article's pooled +3.0 points. N = 14,369 matches the article before the 45 empty rows.
##Dropped: free-text fields (qEnd survey comments, `comments`, partyid_open, the bot-check
##write-in), page timings, end time, the many country-specific region/education/income/vote
##variables, the authors' derived scales and dummies (ASIsummary, SDO/RWA summaries, Vote1-14,
##conservative, agerec, ...).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "WIDE_Full_Launch_DV.dta"))
lab <- function(x) { l <- attr(x, "labels"); v <- as.integer(zap_labels(x)); stopifnot(all(v %in% l)); unname(names(l)[match(v, l)]) }
keep <- !is.na(k$Q1_taskeen1)
stopifnot(sum(keep) == 14324)
k <- k[keep, ]
n <- nrow(k)
wave <- ifelse(k$country == "U.S.", ifelse(k$FirstUS == 1, "main", "us_wave2"), ifelse(k$attributerand == 1, "followup_2024", "main"))
stopifnot(!anyNA(wave))
res <- list()
for (t in 1:7) for (p in 1:2) {
  j <- 2 * (t - 1) + p
  v <- as.integer(zap_labels(k[[paste0("Q1_taskeen", t)]])); stopifnot(all(v %in% 1:2))
  g <- function(s) lab(k[[paste0(s, "_", j)]])
  d <- data.table(id = seq_len(n), task = t, profile = p, choice = as.integer(v == p),
                  attr_gender = g("Gender"), attr_age = g("Age"), attr_experience = g("Experience"), attr_children = g("Children"),
                  attr_ideology = g("Ideology"), attr_occupation = g("Occupation"),
                  attr_origin = c("Born and Raised", "Immigrated")[as.integer(zap_labels(k[[paste0("Origin_", j)]]))])
  res[[length(res) + 1]] <- d
}
d <- rbindlist(res)
stopifnot(!anyNA(d))
office <- c("national", "local")[as.integer(zap_labels(k$Splitsample_conj))]
r <- data.table(id = seq_len(n), trial_wave = wave, trial_office = office,
                trial_attr_order = ifelse(k$attr_order %in% c("", NA), NA_character_, k$attr_order),
                cov_country = k$country, cov_female = as.integer(zap_labels(k$female)), cov_age = as.integer(k$age),
                cov_highered = as.integer(zap_labels(k$highered)), cov_dominant_ethnicity = as.integer(zap_labels(k$domethnicity)),
                cov_left_right = as.integer(zap_labels(k$respideologyx1)), cov_attention_check = as.integer(k$attcheck),
                cov_factcheck_passed = as.integer(k$passedfactcheck))
for (i in 1:4) { r[, paste0("cov_asi_benevolent", i) := as.integer(zap_labels(k[[paste0("ASIbenev", i)]]))]
                 r[, paste0("cov_asi_hostile", i) := as.integer(zap_labels(k[[paste0("ASIhostile", i)]]))] }
r[, cov_masculine := as.integer(zap_labels(k$Contgender_1))][, cov_feminine := as.integer(zap_labels(k$Contgender_2))]
r[, cov_survey_weight := as.numeric(k$weight)]
stopifnot(r[trial_wave != "us_wave2", !anyNA(trial_office)], r[trial_wave == "us_wave2", all(is.na(trial_office))])
d <- merge(d, r, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "trial_wave", "trial_office", "trial_attr_order"))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gothreau_2026_women_candidates.csv"))
