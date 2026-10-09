##UK energy-policy conjoint from
##Beiser-McGrath, L. F. (2024). Energy policy preferences in times of crisis: Evidence from
##survey experiments in the UK. Journal of Political Institutions and Political Economy, 5(4),
##555-579. https://doi.org/10.1561/113.00000111
##Replication data: Harvard Dataverse doi:10.7910/DVN/RUNQHV, CC0 1.0, no restricted files.
##File read: replication_data/data/jpipe_data.csv (inside replication_data.zip). The deposit has
##no codebook; outcome wording, attribute list and sample come from the article (accepted
##version, LSE Research Online eprint 126124, Section 3 and Table 1); the authors' analysis.R
##was read as text.
##Usage: Rscript beisermcgrath_2024.R <dir holding jpipe_data.csv> <output dir>
##
##1,180 UK respondents (Lucid, Qualtrics, 15-17 August 2022, quotas on age, nation, education,
##sex). Each evaluated 5 pairs of hypothetical energy policies (source `profile` = "1a".."5b":
##task 1-5, a = profile 1, b = profile 2), 5 attributes: Energy Source (7 levels), Funding (5),
##Import Restrictions (3), Subsidies (6), Support Scheme (4). Level text is the source text
##with its attribute-name prefix removed (the deposit's *_f columns), which matches article
##Table 1 except "Pensioners" (Table 1 has "Pensioner"); stored as in the data.
##Outcomes:
##  choice = "Which policy do you prefer?" (article), forced: exactly one per pair (checked).
##  rating = "How much do you support or oppose <Policy A/B>?" (article), 1-5. The deposit has
##           no value labels; 4-5 = support follows the authors' suppvsopp recode (rate 4-5 -> 1,
##           1-2 -> 0, 3 -> NA) and the article's fn. 10 (1 = Strongly/Somewhat Support,
##           0 = Strongly/Somewhat Oppose), so 1 = strongly oppose, 5 = strongly support.
##Framing experiment before the conjoint (respondent-level, randomized): trial_frame =
##Control / Economy / Security (article p. 15 gives the texts).
##Randomization: the article does not describe restrictions, level probabilities or attribute
##order. No repeated task.
##Covariates: cov_age_group (age band text), cov_gender (Female/Male -> female/male),
##cov_nation (England/Scotland/Wales/NorthernIreland), cov_educ_categ (the authors' 3-band
##recode LowEduc/MidEduc/HighEduc, not the questionnaire's categories, so not cov_education),
##cov_party_id ("Which political party do you feel closest to politically?", answer text),
##cov_brexit_vote ("In the referendum on membership of the EU in 2016, what did you vote
##for?", text), cov_ukr_intervention_support (the only stored form of "To what extent do you
##support or oppose UK intervention in the Russia-Ukraine conflict?": the authors' recode,
##1 = strongly/somewhat support, 0 otherwise; article fn. 4).
##Dropped: Qualtrics ResponseId (ids re-keyed to integers in source order); the derived outcome
##recodes suppvsall/suppvsopp; *_lab short labels and *_f duplicates; economy_treat/
##security_treat dummies; pid_f; the four cost-of-living binaries (energy_last12_bin,
##energy_next12_bin, costs_last12_bin, costs_next12_bin) and their composites costs /
##energy_insecurity, because the article names only two cost-of-living items and the deposit
##does not say which question each pair of columns holds. No survey weight.
##N: the deposit has 1,180 respondents, and the authors' Table 1 models use all of them
##(7,603 non-neutral profile ratings = 11,800 rows minus 4,197 ratings of 3). The article says
##"I initially started with a sample of 1180 respondents ... 149 respondents are removed who
##fail an attention check", which reads as if 1,031 were analysed; the deposit has no
##attention-check column. Flagged, not resolved.
##Spot check: lm of the authors' suppvsopp (rating 4-5 vs 1-2) on trial_frame reproduces
##Table 1 col. 1 (Security +0.031, Economy -0.004, N = 7,603).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "jpipe_data.csv"), encoding = "UTF-8")
stopifnot(s[, .N, ResponseId][, all(N == 10)], all(grepl("^[1-5][ab]$", s$profile)))
ids <- unique(s$ResponseId)
d <- data.table(id = match(s$ResponseId, ids), task = as.integer(substr(s$profile, 1, 1)),
                profile = fifelse(substr(s$profile, 2, 2) == "a", 1L, 2L),
                choice = as.integer(s$choice), rating = as.integer(s$rate))
strip <- function(x, p) { stopifnot(all(startsWith(x, p))); substring(x, nchar(p) + 1L) }
d[, `:=`(attr_energy_source = strip(s$energy, "energy"), attr_funding = strip(s$funding, "funding"),
         attr_import_restrictions = strip(s$imports, "imports"), attr_subsidies = strip(s$subsidies, "subsidies"),
         attr_support_scheme = strip(s$support, "support"))]
stopifnot(d$attr_energy_source == s$energy_f, d$attr_funding == s$funding_f, d$attr_import_restrictions == s$imports_f,
          d$attr_subsidies == s$subsidies_f, d$attr_support_scheme == s$support_f)
d[, trial_frame := s$energyframe_treat]
stopifnot(all(s$sex %in% c("Female", "Male")))
d[, `:=`(cov_age_group = s$age_categ, cov_gender = tolower(s$sex), cov_nation = s$country, cov_educ_categ = s$educ_categ,
         cov_party_id = s$pid, cov_brexit_vote = s$brexit, cov_ukr_intervention_support = as.integer(s$russia_supp))]
stopifnot(all(d$rating %in% 1:5), d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "beisermcgrath_2024_energy_policy.csv"))
