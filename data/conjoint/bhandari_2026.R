##Business-deal conjoint (Morocco) from
##Bhandari, A., & York, E. (2026). Political connections, patronage, and consumer attitudes: The
##non-electoral consequences of clientelism. World Development (forthcoming; no DOI found in
##Crossref on 2026-10-08).
##Replication data: Harvard Dataverse doi:10.7910/DVN/QHXQTH, CC BY 4.0 (deposit LICENSE + README),
##no restricted files, no terms.
##Files read: conjoint_anonymous.rds, fullsurvey_anonymous.rds. Also read as text: README.md,
##data-dictionary.md (the codebook: question wording, level text, coding), 01_clean.R,
##02_main_results.R. No questionnaire is deposited.
##Usage: Rscript bhandari_2026.R <raw dir> <output dir>
##
##Online survey in Morocco, 2021, recruited through Facebook (data dictionary). 3,170 survey
##respondents; 2,008 answered at least one conjoint task (attrition: 2,008 / 1,760 / 1,543 / 1,399
##answered rounds 1-4). Each saw 4 rounds (task) of 2 "deal" profiles (profile 1-2). Product type was
##a bank account in rounds 1-2 and a TV deal in rounds 3-4 for EVERY respondent in the data (the
##dictionary says the order was randomized between respondents; the data show no such variation),
##stored as trial_product (Bank / TV).
##Attributes, as stored (the authors' English labels; display language and wording not deposited):
##owner (Businessman / Councillor / Party official), hq (Local / National), cost (Lower than average /
##Average / Higher than average), party (Party you didn't support / Party you supported), behavior
##(Didn't give gift / Gave gift; the authors relabel these "Didn't offer gift" / "Offered gift" for
##their figures). The dictionary calls party "vacuous for the Businessman level", but a party level is
##stored for every Businessman profile; whether it was shown to respondents is not documented, so
##it is kept as stored (FOR BEN: may need "(not shown)" if the questionnaire says otherwise).
##No source documents restrictions, probabilities or attribute order; all level pairs occur.
##Outcomes (dictionary wording):
##  choice        "Which deal are you more likely to choose?" Options Deal 1 / Deal 2 (TV rounds) or
##                Bank account 1 / Bank account 2 (bank rounds), Both, Neither. choice = 1 on the
##                profile picked; "Both" and "Neither" are coded 0 on both profiles (the authors'
##                chose_deal codes Both as 1 on both, which a choice column cannot hold). The raw
##                answer is kept in trial_choice_response so Both can be recovered. opt_out = yes.
##  choice_wrong  "Which deal is more likely to go wrong?" same options and coding (raw answer in
##                trial_wrong_response; Both 2,412 / Neither 3,534 profile rows).
##  rating        trust (slider 0-10, "stated trust in this profile's deal, 0 (none) to 10 (full)";
##                dictionary paraphrase), as stored.
##Dropped: 10,548 rows of respondents who never reached the conjoint (no attributes, no outcome) and
##696 tasks (1,392 rows) shown but not answered; the Qualtrics ResponseId (re-keyed to integers);
##the authors' derived variables (chose_deal/will_go_wrong recodes, imputations, moderator factors);
##consent/eligibility screeners (all "Yes" among the kept respondents); the phone-credit framing
##experiment (telecom_choice*), a separate experiment.
##Covariates (fullsurvey_anonymous.rds, asked AFTER the conjoint, so NA for respondents who left
##earlier; "Prefer not to answer" -> NA): cov_gender (Female/Male -> female/male), cov_birth_year
##(year_born; "Before 1940" -> NA, n = 0 among kept), cov_education (highest_degree text),
##cov_language_home, cov_income (monthly_hh_income band text), cov_employment, cov_voted_2016,
##cov_plan_to_vote, cov_vote_party (party voted / would vote for; a vote, not party ID),
##cov_gift_for_vote (gift_or_donation: ever received a gift in exchange for a vote),
##cov_connections_self (cxn_self_assess_1, 0-10), cov_mp_access (phone_mp: has direct phone access to
##a member of parliament), cov_family_connections (checkbox
##combination of family members' political roles, comma-joined; NA = block not reached or none
##ticked, as in the source), cov_trust_government / _parliament / _parties / _council and
##cov_corruption (answer text), cov_region (region name; numeric codes in the source are unlabelled
##and set to NA, as the authors exclude them too). No survey weight.
##N: 2,008 answering respondents, 13,420 profile rows = the Observations of the authors' deposited
##02_main_regression_output.tex. Spot check: the authors' AMCE model (chose_deal, i.e. Both counted as
##chosen, on the five attributes) on this table reproduces every coefficient and SE of that table
##(Councillor -0.050, Party official -0.088, Gave gift -0.100, Party you supported 0.041, ...), except
##that the two cost rows appear with their labels swapped in the authors' table (Higher -0.018 and
##Lower -0.008 here, from the stored level text; their table prints -0.008 for Higher).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "conjoint_anonymous.rds")))
s <- as.data.table(readRDS(file.path(raw, "fullsurvey_anonymous.rds")))
x <- x[!is.na(choice)]
stopifnot(!anyNA(x[, .(owner, hq, cost, party, behavior, wrong, trust)]), x[, .N, .(ResponseId, round)][, all(N == 2)],
          x[, uniqueN(type), .(ResponseId, round)][, all(V1 == 1)])
pick <- function(resp, prof) { stopifnot(all(resp %in% c("Deal 1", "Deal 2", "Bank account 1", "Bank account 2", "Both", "Neither")))
  as.integer(resp %in% c("Deal 1", "Bank account 1") & prof == 1 | resp %in% c("Deal 2", "Bank account 2") & prof == 2) }
ids <- unique(x$ResponseId)
d <- data.table(id = match(x$ResponseId, ids), task = as.integer(x$round), profile = as.integer(x$profile),
                choice = pick(x$choice, x$profile), choice_wrong = pick(x$wrong, x$profile), rating = as.integer(x$trust),
                attr_owner = as.character(x$owner), attr_hq = as.character(x$hq), attr_cost = as.character(x$cost),
                attr_party = as.character(x$party), attr_behavior = as.character(x$behavior),
                trial_product = x$type, trial_choice_response = x$choice, trial_wrong_response = x$wrong)
stopifnot(all(d$rating %in% 0:10), d[, .(a = sum(choice), b = sum(choice_wrong)), .(id, task)][, all(a <= 1 & b <= 1)],
          all(x$chose_deal == pmax(d$choice, x$choice == "Both")))
s <- s[match(x$ResponseId, s$ResponseId)]
na <- function(v) fifelse(v %in% "Prefer not to answer", NA_character_, v)
by <- suppressWarnings(as.integer(s$year_born))
d[, `:=`(cov_gender = c(Female = "female", Male = "male")[na(s$gender)], cov_birth_year = by,
         cov_education = na(s$highest_degree), cov_language_home = na(s$language_at_home),
         cov_income = na(s$monthly_hh_income), cov_employment = na(s$employment_status),
         cov_voted_2016 = na(s$voted_2016), cov_plan_to_vote = na(s$plan_to_vote), cov_vote_party = na(s$vote_party),
         cov_gift_for_vote = na(s$gift_or_donation), cov_connections_self = as.integer(s$cxn_self_assess_1),
         cov_mp_access = na(s$phone_mp), cov_family_connections = s$cxns_family,
         cov_trust_government = na(s$trust_government_1), cov_trust_parliament = na(s$trust_government_2),
         cov_trust_parties = na(s$trust_government_3), cov_trust_council = na(s$trust_government_4),
         cov_corruption = na(s$corruption),
         cov_region = fifelse(grepl("^[0-9]+$", s$region_province_1), NA_character_, na(s$region_province_1)))]
d[, cov_gender := unname(cov_gender)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bhandari_2026_clientelism_consumers.csv"))
cat(nrow(d), uniqueN(d$id), "\n")
