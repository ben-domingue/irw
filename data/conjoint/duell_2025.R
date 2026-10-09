##New-party response vignettes (14 EU countries) from
##Duell, D., & Kaftan, L. (2025). Voices of the party base: How supporters want established
##parties to respond to new parties. European Political Science Review.
##https://doi.org/10.1017/S1475676525100625
##Replication data: Harvard Dataverse doi:10.7910/DVN/SNEYXG, CC0 1.0, no restricted files.
##File read: voicesOfThePartyBase.csv. Also read as text: replicationFile_voicesOfThePartyBase.R
##(authors' cregg models and labels). Design facts from the article text (vignette tables are
##images there and were not read).
##Usage: Rscript duell_2025.R <raw dir> <output dir>
##
##19,775 respondents (Dynata online panels, July-August 2021, ~1,400 per country, quotas on
##age x gender, education, region) in AT, DE, DK, ES, FR, GR, HU, IE, IT, NL, PL, PT, RO, SE.
##Introduction: "We would now like to show you four hypothetical situations in which a new
##party would like to run in the next election to the [National Parliament]." Each vignette
##(task 1-4 = the source's `vignette` v1-v4; single profile, profile = 1) describes a new party
##that makes an attack statement and a policy demand, and the response of the respondent's
##first-ranked party (its name filled in; kept as cov_party_first_ranked). Three randomized
##attributes; the displayed text (14 languages) is NOT deposited, so levels are:
##  attr_attack: the authors' labels "populist" (established elites act against the people's
##    wishes) / "anti-government".
##  attr_policy_demand: the article's English description of the demand, mapped from the
##    authors' codes (direction verified against the authors' `congruence` variable, which
##    marks a respondent whose own position equals the demand as "same extreme position"):
##    climate pro = "measures should be taken so that the country becomes climate neutral as
##    early as 2025", climate con = "climate protection measures should be stopped immediately",
##    digittax pro = "large internet companies should have to pay an additional digital tax",
##    digittax con = "large internet companies should not pay taxes in the EU", immi vote pro =
##    "foreigners living in the country should be allowed to vote in any election in that
##    country", immi vote con = "foreigners living in the country should not be allowed to vote",
##    freedom pro = "fundamental rights should never be restricted in a pandemic", freedom con =
##    "fundamental rights should always be restricted in a pandemic to protect health"
##    (paraphrases). The article says one vignette per policy area, but topics repeat within
##    respondents in the data (only 1,822 respondents saw all four); stored as deposited.
##  attr_party_response: the authors' labels (united_detail): ignore, accommodative,
##    adversarial (unified), "accommodative + ignore", "adversarial + accommodative",
##    "adversarial + ignore" (party divided between the two). The authors' `united` is derived.
##Outcome: rating = how much the respondent likes the described response, 1 (do not like at
##all) - 7 (like a lot) (paraphrase from the authors' axis label; wording not deposited).
##Vignettes with no rating (6) or no recorded attack type (populism missing, 33) are omitted;
##66 respondents have only 3 vignettes in the deposit.
##No randomization restriction documented; level shares near-equal (ignore 1/3, each unified 1/6,
##each divided ~1/9: response probably drawn as united/divided/ignore first, observed).
##Respondent id = the source's id_num (the Qualtrics ResponseId `id` is dropped).
##Covariates: cov_age (years; values that are not whole numbers 16-100 set NA), cov_gender
##(gender 0 = male, 1 = female, 2 = other: the authors' script labels 0 Male, 1 Female,
##2 "Neither"; 0/1 agree with their ageGender labels), cov_country,
##cov_region (region_text), cov_work_status, cov_turnout (text as stored), cov_lr (left-right
##self-placement 0-10 as stored), cov_policy_climate/immigration/tech/freedom (the respondent's
##own position on the four demands, text as stored), cov_party_first_ranked (party_chosen),
##cov_party_family (authors' family of that party), cov_edu_code, cov_size_locality_code
##(codes; no mapping deposited). Dropped: ResponseId, populism battery items (wording not
##deposited) and the authors' indices/medians/splits, party_ident_pre/post (codes undocumented),
##cabinet_party, party_dissent, congruence, education/ageGender/region recodes.
##N: 19,775 respondents and 79,034 vignettes, as in the article. No weight deposited.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "voicesOfThePartyBase.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 79034, uniqueN(s$id_num) == 19775, s[, uniqueN(id_num), id][, all(V1 == 1)])
pol <- c("climate pro" = "measures should be taken so that the country becomes climate neutral as early as 2025",
         "climate con" = "climate protection measures should be stopped immediately",
         "digittax pro" = "large internet companies should have to pay an additional digital tax",
         "digittax con" = "large internet companies should not pay taxes in the EU",
         "immi vote pro" = "foreigners living in the country should be allowed to vote in any election in that country",
         "immi vote con" = "foreigners living in the country should not be allowed to vote",
         "freedom pro" = "fundamental rights should never be restricted in a pandemic",
         "freedom con" = "fundamental rights should always be restricted in a pandemic to protect health")
# direction check: the respondent's own position matching the demand is the authors' "same extreme position"
own <- c(climate = "policy_climate", digittax = "policy_tech", "immi vote" = "policy_immigration", freedom = "policy_freedom")
match_pos <- c("climate pro" = "take more measures", "climate con" = "stop measures", "digittax pro" = "pay additional taxes",
               "digittax con" = "not pay taxes", "immi vote pro" = "allowed to vote", "immi vote con" = "not allowed to vote",
               "freedom pro" = "never restrict", "freedom con" = "always restrict")
s[, ownpos := NA_character_]
for (k in names(own)) s[startsWith(policy, k), ownpos := get(own[[k]])]
stopifnot(s[, all((ownpos == match_pos[policy]) == (congruence == "same extreme position"))])
stopifnot(all(s$policy %in% names(pol)), all(s$vignette %in% paste0("v", 1:4)), s[, !anyDuplicated(vignette), id_num]$V1)
s <- s[!is.na(outcome) & !is.na(populism) & populism != ""]
stopifnot(all(s$outcome %in% 1:7), all(s$gender %in% 0:2))
stopifnot(s[gender == 1, all(startsWith(ageGender, "female"))], s[gender == 0, all(startsWith(ageGender, "male"))])
age <- as.numeric(s$age); age[!(age == round(age) & age >= 16 & age <= 100)] <- NA
d <- s[, .(id = as.integer(id_num), task = as.integer(sub("v", "", vignette)), profile = 1L, rating = as.integer(outcome),
           attr_attack = as.character(populism), attr_policy_demand = unname(pol[policy]),
           attr_party_response = as.character(united_detail))]
d[, `:=`(cov_age = as.integer(age), cov_gender = c("male", "female", "other")[s$gender + 1L], cov_country = s$country,
         cov_region = s$region_text, cov_work_status = s$work_status, cov_turnout = s$turnout, cov_lr = as.integer(s$lr),
         cov_policy_climate = s$policy_climate, cov_policy_immigration = s$policy_immigration, cov_policy_tech = s$policy_tech,
         cov_policy_freedom = s$policy_freedom, cov_party_first_ranked = s$party_chosen, cov_party_family = s$party_family,
         cov_edu_code = as.integer(s$edu), cov_size_locality_code = as.integer(s$size_locality))]
for (v in names(d)[sapply(d, is.character)]) d[get(v) == "", (v) := NA]
stopifnot(!anyNA(d[, .(attr_attack, attr_policy_demand, attr_party_response)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "duell_2025_party_responses.csv"))
