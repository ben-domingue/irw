##Abstention option in conjoint experiments on energy policy (Switzerland) from
##Brückmann, G., & Stadelmann-Steffen, I. (2025/26). Impacts of allowing respondents to abstain from binary choice in
##conjoint experiments on energy policy acceptance. SocArXiv preprint 10.31235/osf.io/kr64j_v2 (v2, 2026-02-23).
##Replication data: Harvard Dataverse doi:10.7910/DVN/UFGBBM, CC BY 4.0. File read: data_full_for_replication_nov2025.RData
##(loaded into its own environment; objects data_full, Baseline, my_labels), 02-01_Data_Cleaning_Mainfile.R and
##02-02_Variable_Coding.R, 02_MainAnalysis.R and README.md (read as text).
##Usage: Rscript bruckmann_2025.R <dir holding data_full_for_replication_nov2025.RData> <output dir>
##
##Swiss online survey (Qualtrics, fielded from August 2022 in German, French, Italian and English): each respondent
##compared 5 pairs of solar-photovoltaic-module projects ("Project A" / "Project B"), 5 attributes: location (Farm,
##Community building, Traffic infrastructure, Skiing area, Large consumer roof), reimbursement (6 levels),
##purchase (6 levels), module price in CHF (200/250/300/350, stored as the number), provider (6 levels). Level text is the
##English label stored in the file (the respondents saw their own language; label_language en).
##Between-respondent arm trial_arm: "Abst. poss." (respondents could abstain from choosing) or "Binary choice" (forced
##choice), column tap_dummy_factor; the same attributes and the authors pool both arms. Same tasks carry
##  choice: Project A / Project B / (abstained). Profile 1 = Project A, profile 2 = Project B (data_bin.rds codes
##    choice0 = 0 on project 1 when "Project B" was chosen). Abstention (3,380 tasks in the full file, only in the
##    abstention arm) = choice 0 on both profiles (a real opt-out). The wording is NOT in the deposit.
##  rating: acceptance rating of each project, `accept0`, integers 1-5, higher = more accepted (the authors call 1 the
##    lowest rating; chosen projects average 4.1 vs 3.3 for the rejected ones; anchor labels not in the deposit).
##Respondents: all 4,466 in the file are kept (Ben 2026-11-10: authors' sample exclusions are not applied). The authors'
##analysis sample (preprint section 3.4; 02-01 lines 1-4) drops speeders below the 10th percentile of durationinseconds
##(1,206 s), completions over 3,600 s, and respondents who said they would buy more than 300 modules (none here);
##reproduce it with cov_duration_sec. N check: the SocArXiv preprint (10.31235/osf.io/kr64j_v2) reports 4,466 participants
##from a registry sample of 13,500 invited, and a final analysis sample of 2,927 (the deposit's own cleaning yields 2,980).
##Attribute order randomized between respondents, constant within (preprint 3.3), not saved: attr_order respondent.
##Covariates: cov_gender (female/male; non-binary -> other), cov_age_group (agecat text as stored), cov_education (educ
##text: Secondary I / Secondary II / Tertiary), cov_income (household income band text), cov_left_right (leri text),
##cov_language (userlanguage), cov_duration_sec. No survey weight in the file.
##PII FOUND and dropped: IP address, latitude/longitude, recipient (placeholder) name/email, external reference, the
##Qualtrics response id, browser/OS strings; userid is re-keyed to an integer id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "data_full_for_replication_nov2025.RData"), envir = e)
d <- as.data.table(e$data_full)
stopifnot(d[, uniqueN(userid)] == 4466, d[, .N, .(userid, conjoint)][, all(N == 2)])
d[, ch := fifelse(is.na(choice), 0L, as.integer((choice == "Project A") == (project == 1)))]
d[, id := as.integer(factor(userid))]
stopifnot(d[, sum(ch), .(id, conjoint)][, all(V1 <= 1)], d[tap_dummy_factor == "Binary choice", sum(ch), .(id, conjoint)][, all(V1 == 1)],
          d[, all(accept0 %in% 1:5)])
ch <- function(x) as.character(x)
o <- d[, .(id, task = as.integer(conjoint), profile = as.integer(project), choice = ch, rating = as.integer(accept0),
           attr_location = ch(location), attr_reimbursement = ch(reimburse), attr_purchase = ch(purchase),
           attr_price_chf = ch(price), attr_provider = ch(provider),
           cov_gender = c(female = "female", male = "male", `non-binary (as an umbrella term)` = "other")[ch(gender)],
           cov_age_group = ch(agecat), cov_education = ch(educ), cov_income = ch(income), cov_left_right = ch(leri),
           cov_language = ch(userlanguage), cov_duration_sec = as.integer(durationinseconds),
           trial_arm = ch(tap_dummy_factor))]
stopifnot(!anyNA(o[, .(attr_location, attr_reimbursement, attr_purchase, attr_price_chf, attr_provider, choice, rating)]))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "bruckmann_2025_solar_abstention.csv"))
