##Danish local-candidate conjoint from
##Nyholt, N. (2024). Why do voters prefer local candidates? Evidence from a Danish conjoint
##survey experiment. Political Behavior, 46, 2313-2332. https://doi.org/10.1007/s11109-024-09919-9
##Replication data: Harvard Dataverse doi:10.7910/DVN/TM6R4J, CC0 1.0, no restricted files.
##File read: survey_data.dta (Dataverse "original format" download of survey_data.tab). Level text
##and question wording are the Stata variable/value labels (Danish); the authors' transformations.R
##(read as text) gives their English level names and the "no information" coding.
##Usage: Rscript nyholt_2024.R <raw dir> <output dir>
##
##1,021 YouGov Denmark panel respondents (quotas on gender, age, region, education), 5 tasks of
##two hypothetical Folketing candidates (Kandidat A = profile 1, B = profile 2), 7 attributes
##presented as sentences of a vignette. Task/profile come from the column names (conj<t>_*_a/b).
##Outcomes (both asked about every pair):
##  rating: "Kandidat A"/"Kandidat B" items; the article words it "How likely is it that you would
##    vote for Candidate A [B]?". Source codes 1 = Meget sandsynligt .. 5 = Meget usandsynligt,
##    6 = Ved ikke. REVERSED here to 1 = very unlikely .. 5 = very likely (as in the article);
##    Ved ikke set missing.
##  choice: "Hvilken kandidat foretrækker du?" Kandidat A / Kandidat B / Ved ikke. OPT-OUT: "Ved
##    ikke" (1,801 of 5,105 tasks, source code 3; the article reports up to 1,175 dyads lost to "don't know" after its exclusions) has choice = 0 on both profiles.
##Attributes (Danish label text): gender (mand/kvinde), age, occupation, party, descriptive
##localism, behavioral localism, symbolic localism. Behavioral and symbolic localism were omitted
##for a random subsample of profiles (source level 1, label "1"; authors: "No behavioral/symbolic
##information"): stored as "(not shown)". CAVEAT: the deposit's value labels are cut at 80
##characters, so descriptive level 2, behavioral level 4 and symbolic levels 2-4 are truncated
##prefixes of the displayed sentence (levels stay distinct; the full text is in the article's
##Table 1 / Appendix G, not read). Age: the deposit has the randomized band (27-33/34-49/50-63/
##64-74) and an exact age within it (verified nested); attr_age stores the exact age; which form
##was printed is not documented in the deposit.
##Randomization: localism attributes uniform; gender, age, occupation, party drawn from the 2019
##Folketing candidates' marginal distribution (article), i.e. non-uniform weights.
##trial_prime: respondent-level arm (1 = Prime, 2 = No prime, source `Prime`).
##Covariates (source numeric codes; labels in the .dta, Danish): cov_gender 1=Kvinde 2=Mand;
##cov_age years; cov_region 1-5; cov_education (9-category profile_education, 9 = won't say);
##cov_education3; cov_personal_income / cov_household_income (4 = don't know/won't say);
##cov_urban 1-6; cov_occupation (occupation2); cov_house_type; cov_vote_intention (FT_next);
##cov_partisanship1-4 (party ID items); cov_local1-3 (local identity items, 977 = Ved ikke);
##cov_total_time (seconds; the authors drop respondents under 180 s, +15 s with the prime: 242
##respondents, article); cov_survey_weight (`weight`, used in the authors' cj() calls).
##Dropped: page timings, employee job title, work-status dummies, the category age band.
##All 1,021 respondents are kept (the article's 1,021 before the inattention exclusion).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "survey_data.dta"))
lab <- function(x) { l <- attr(x, "labels"); v <- as.integer(zap_labels(x)); stopifnot(all(v %in% l)); unname(names(l)[match(v, l)]) }
res <- list()
for (t in 1:5) for (p in c("a", "b")) {
  g <- function(v) k[[sprintf("conj%d_%s_%s", t, v, p)]]
  age_band <- as.integer(zap_labels(g("age"))); age <- as.integer(g("age_int"))
  stopifnot(all(age_band == findInterval(age, c(0, 34, 50, 64))))
  fc <- as.integer(zap_labels(k[[sprintf("conj%d_fc", t)]])); sup <- as.integer(zap_labels(k[[sprintf("conj%d_sup_%d", t, match(p, c("a", "b")))]]))
  stopifnot(all(fc %in% 1:3), all(sup %in% 1:6))
  d <- data.table(id = as.integer(k$id), task = t, profile = match(p, c("a", "b")),
                  choice = as.integer(fc == match(p, c("a", "b"))), rating = ifelse(sup == 6L, NA_integer_, 6L - sup),
                  attr_gender = lab(g("gender")), attr_age = as.character(age), attr_occupation = lab(g("occupation")),
                  attr_party = lab(g("partisanship")), attr_descriptive_localism = lab(g("descriptive_localism")),
                  attr_behavioral_localism = lab(g("behavioral_localism")), attr_symbolic_localism = lab(g("symbolic_localism")))
  res[[length(res) + 1]] <- d
}
d <- rbindlist(res)
for (v in c("attr_behavioral_localism", "attr_symbolic_localism")) d[get(v) == "1", (v) := "(not shown)"]
d[, attr_descriptive_localism := sub("^ +", "", attr_descriptive_localism)]
for (v in grep("^attr_", names(d), value = TRUE)) d[, (v) := trimws(get(v))]
cv <- c(Prime = "trial_prime", gender = "cov_gender", age_recoded = "cov_age", region = "cov_region", profile_education = "cov_education",
        education_3split = "cov_education3", personal_income_recoded = "cov_personal_income",
        household_income_recoded = "cov_household_income", urban = "cov_urban", occupation2 = "cov_occupation",
        house_type = "cov_house_type", FT_next = "cov_vote_intention", partisanship1 = "cov_partisanship1",
        partisanship2 = "cov_partisanship2", partisanship3 = "cov_partisanship3", partisanship4 = "cov_partisanship4",
        local1 = "cov_local1", local2 = "cov_local2", local3 = "cov_local3")
r <- data.table(id = as.integer(k$id))
for (v in names(cv)) r[, (cv[[v]]) := as.integer(zap_labels(k[[v]]))]
r[, cov_total_time := as.numeric(k$Tot_time)][, cov_survey_weight := as.numeric(k$weight)]
stopifnot(!anyDuplicated(r$id))
d <- merge(d, r, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", "trial_prime"))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], uniqueN(d$id) == 1021)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nyholt_2024_local_candidates.csv"))
