##Voting-rights conjoint (United States) from
##Hultin Rosenberg, J., & Wejryd, J. (2022). Attitudes toward competing voting-right
##requirements: Evidence from a conjoint experiment. Electoral Studies, 77, 102470.
##https://doi.org/10.1016/j.electstud.2022.102470
##Replication data: Harvard Dataverse doi:10.7910/DVN/EPH0FI, CC0 1.0, no restricted files.
##File read: "Replication data for Attitudes toward Voting-Rights Requirements, long.dta"
##(Dataverse "original format" download of the long .tab, saved as long.dta). The authors'
##three do-files were read as text. The article (Elsevier, CC BY) could not be fetched from
##here, so question wording, sample source and design rules are NOT taken from it.
##Usage: Rscript hultinrosenberg_2022.R <raw dir> <output dir>
##
##US citizens (Qualtrics panel, fielded 2018 per the StartDate field; all 980
##good completers report US citizenship). Each respondent saw 6 pairs of hypothetical
##persons (profilenumber = task*10 + profile, e.g. 31 = pair 3, profile 1), chose one and rated
##each. Outcomes:
##  choice = the authors' `chosen` (1 if choicepair<t> names this profile). 22-43 respondents
##           per pair left the choice empty; on those tasks choice is NA on both profiles
##           while ratings are kept. Question wording not deposited; the authors' do-files treat
##           it as preferring which of the two should have voting rights (paraphrase).
##  rating = ratingprofile, 1-7 as stored; the authors code 5-7 as embracing and 1-3 as
##           rejecting the profile's franchise (desc.do `allowyes`/`allowno`). Wording and
##           anchors not deposited. 29 profile rows have no rating (NA).
##Attributes: level text = the authors' Stata value labels in the long file (profilecitizenship,
##profileborn, profileedu, profilegender, profiletaxpayer, profileresidence), e.g.
##"Pays income taxes in the US", "Lived in Europe the last 15 years", "Tourist in the US".
##These are the authors' labels; whether they match the displayed wording word for word is
##not verifiable from the deposit. Attribute order, level probabilities and restrictions are
##not documented (see design record).
##All level pairs occur and shares are near-equal (1/2 or 1/5). Spot check (article not
##available to compare): LPM of choice gives US citizen +0.36, no income taxes -0.20, lived in
##the US 15 years +0.22 vs lived in Europe 15 years.
##Sample: the long file has 999 respondents; the authors analyse only Qualtrics "good
##completers" (gc == "1", their `use` == 1): 980, the wide file's N. The 19 others are dropped.
##Covariates (wide-file value labels): cov_age (years), cov_gender (genderrespondent 0 Male ->
##male, 1 Female -> female), cov_education (educationrespondent label text), cov_employment
##(label text), cov_household_income (label text), cov_us_born (usbornrespondent 0/1, 1 = US
##born), cov_importance_democracy (as stored, 1-7, unlabelled), cov_duration_sec (Qualtrics
##"Duration (in seconds)", whole survey).
##Dropped: Qualtrics ResponseId (re-keyed to integers in sorted order), start/end/recorded
##timestamps, commentsonsurvey (FREE TEXT), uscitizenrespondent (constant), the authors'
##derived variables (age2, agegr, dichdemocracy, conflict flags, allowyes/allowno, profile
##dummies, residentyesprofile). No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
l <- read_dta(file.path(raw, "long.dta"))
lab <- function(v) as.character(as_factor(l[[v]], levels = "labels"))
s <- data.table(rid = l$ResponseId, use = as.integer(l$use), pn = as.integer(l$profilenumber),
                chosen = as.integer(l$chosen), rating = as.integer(l$ratingprofile))
cp <- as.data.table(lapply(paste0("choicepair", 1:6), function(v) as.integer(l[[v]])))
s[, task := pn %/% 10L][, profile := pn %% 10L]
s[, cpair := as.matrix(cp)[cbind(seq_len(.N), task)]]
s[is.na(cpair), chosen := NA_integer_]
for (v in c("citizenship", "born", "edu", "gender", "taxpayer", "residence")) s[, paste0("attr_", v) := lab(paste0("profile", v))]
s[, `:=`(cov_age = as.integer(l$age), cov_gender = c("male", "female")[as.integer(l$genderrespondent) + 1L],
         cov_education = lab("educationrespondent"), cov_employment = lab("employment"),
         cov_household_income = lab("householdincome"), cov_us_born = as.integer(l$usbornrespondent),
         cov_importance_democracy = as.integer(l$importanceofdemocracy),
         cov_duration_sec = as.numeric(l$Durationinseconds))]
s <- s[use == 1]
stopifnot(uniqueN(s$rid) == 980, s[, .N, rid][, all(N == 12)], all(s$task %in% 1:6), all(s$profile %in% 1:2),
          s[!is.na(chosen), sum(chosen), .(rid, task)][, all(V1 == 1)], !anyNA(s[, .SD, .SDcols = patterns("^attr_")]))
s <- s[!(is.na(chosen) & is.na(rating))]
s[, id := match(rid, sort(unique(rid)))]
d <- s[, c("id", "task", "profile", "chosen", "rating", grep("^(attr|cov)_", names(s), value = TRUE)), with = FALSE]
setnames(d, "chosen", "choice")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hultinrosenberg_2022_voting_rights.csv"))
