##Solar net-metering donation-program conjoint (US) from
##Gazmararian, A. F., & Tingley, D. (2024). Reimagining net metering: A polycentric model for
##equitable solar adoption in the United States. Energy Research & Social Science, 108, 103374.
##https://doi.org/10.1016/j.erss.2023.103374
##Replication data: Harvard Dataverse doi:10.7910/DVN/7FCGPA. Dataverse licence CC0 1.0, no
##restricted files, no terms. BUT the deposit's README.md says the package is "provided under the
##MIT License ... free for academic, educational, and research purposes ... For any commercial
##use or adaptation of the materials, please contact the author for permission." Carried as
##CC BY-NC 4.0 (stricter reading, as for 10.5683/sp3/a55jz8); Ben to confirm.
##Files read: natsurvey_conjoint.rds (data/qualtrics/). Wording and level definitions from
##PolycentricSpring2023_Codebook.docx (Qualtrics survey export); attribute names from the
##authors' analyze_conjoint.R (read as text, not run).
##Usage: Rscript gazmararian_2024_net_metering.R <raw dir> <output dir>
##
##2,006 US respondents (Qualtrics panel, spring 2023, English), 4 rounds of 2 solar donation
##programs ("Program A" = profile 1, "Program B" = profile 2), 6 attributes; task/profile are the
##source's task / profile (A/B) columns, which agree with the Rd_<t>_<A|B>_<attribute> columns
##(checked). The deposit is already long (8 rows per respondent). Not a different paper from
##gazmararian_2024.R (that is the Energy Policy just-transition conjoint, doi:10.7910/DVN/FC9X6H).
##Outcomes (codebook, block "Conjoint"):
##  choice  = "Please read the descriptions of the two programs carefully. Then pick which one you
##            like best and say how much of your profit from solar you would choose to donate under
##            each program. ... Which program do you prefer?" Program A / Program B; forced, no
##            opt-out (exactly one chosen per task, checked).
##  rating  = donate: "What percent (from 0 to 100) of your yearly solar profits would you choose to
##            donate under each program?" free-typed number per program, stored as typed (0-100;
##            a few fractional entries such as 0.01 or 0.224 are kept; they may be proportions).
##Attributes (level text as stored = Qualtrics conjoint display text): Federal Tax Credits for Solar
##Installation (0%/22%/26%/30%), Target Community (Any / Low-income / Black, Brown, and
##Indigenous / Coal, oil, and gas producing / Rural), Additional Solar Tax Credits for Donation
##Recipient (No credit / 10% tax credit), Your Average Yearly Solar Profits ($300-$900),
##Community Member Participation (0-30%), Solar Project Type (5 types). No restrictions or
##probabilities are documented; attribute order not recorded. A fifth round (choice5) exists in
##the raw Qualtrics columns for 21 respondents only; the codebook shows 4 rounds and the authors'
##long file has 4, so it is ignored.
##Covariates (answer text from the data, wording from the codebook): cov_gender (sex "What sex
##were you assigned at birth?" Male/Female), cov_age (years, as recorded), cov_education
##(highested), cov_party_id (PolParty "Generally speaking, do you think of yourself as a ...?";
##trailing tabs stripped; "Other (please specify)" kept, its text dropped), cov_hispanic 0/1,
##cov_race (Qualtrics multi-select text), cov_ideology, cov_income, cov_employment, cov_home,
##cov_rural, cov_state, cov_buy_solar_self (buyself), cov_trust_fed/power/local/general, cov_altruism
##and cov_risk (0-9 as stored), cov_read_* (the six True/False/Not sure comprehension questions on
##the attribute definitions, answered before the tasks), cov_duration_sec (Q_TotalDuration,
##whole survey). Respondents failing attention checks or speeding were screened out by Qualtrics
##(codebook EndSurvey branches), so no attention column.
##Dropped: Qualtrics ResponseId (re-keyed), IP/email/name/lat-long (masked "*******" in the
##deposit), zip, qualtricsZip, County (PII: postcodes and counties), panel ids (rid, RISN,
##transaction_id, SVID), timing/click columns, free text, the other experiments' items and
##treatment flags, and the authors' derived variables (female, college, *_bin, *_num, n_right,
##pid3, ...). No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
g <- as.data.table(readRDS(file.path(raw, "natsurvey_conjoint.rds")))
stopifnot(g[, .N, ResponseId][, all(N == 8)], all(g$profile %in% c("A", "B")), all(g$task %in% 1:4))
for (t in 1:4) for (p in c("A", "B")) {
  x <- g[task == t & profile == p]
  stopifnot(all(x$target_ == x[[sprintf("Rd_%d_%s_Target.Community", t, p)]]),
            all(x$projtyp_ == x[[sprintf("Rd_%d_%s_Solar.Project.Type", t, p)]]))
}
g[, idn := as.integer(factor(ResponseId, levels = unique(ResponseId)))]
d <- data.table(id = g$idn, task = as.integer(g$task), profile = match(g$profile, c("A", "B")),
                choice = as.integer(g$selected), rating = as.numeric(g$donate))
stopifnot(all(d$choice == (substr(g$choice, 9, 9) == g$profile)), d[, sum(choice), .(id, task)][, all(V1 == 1)],
          all(!is.na(d$rating)), all(d$rating >= 0 & d$rating <= 100))
att <- c(credits_ = "federal_tax_credit", target_ = "target_community", addcredit_ = "additional_tax_credit",
         avgprofit_ = "average_yearly_profit", partic_ = "community_participation", projtyp_ = "project_type")
for (v in names(att)) { x <- as.character(g[[v]]); stopifnot(!anyNA(x), all(x != "")); d[, paste0("attr_", att[[v]]) := x] }
cl <- function(x) { x <- trimws(gsub("\t", "", as.character(x))); x[x %in% c("", "NA")] <- NA; x }
stopifnot(all(g$sex %in% c("Male", "Female")))
d[, cov_gender := tolower(g$sex)]
d[, cov_age := as.integer(g$age)]
d[, cov_education := cl(g$highested)]
d[, cov_party_id := cl(g$PolParty)]
cv <- c(hispanic = "hispanic", race = "race", Ideo = "ideology", Income = "income", Employment = "employment",
        home = "home", rural = "rural", state = "state", buyself = "buy_solar_self", trustfed = "trust_fed",
        trustpower = "trust_power", trustlocal = "trust_local", trustgen = "trust_general", altruism = "altruism",
        risk = "risk", ReadCredit = "read_credit", ReadCommunity = "read_community", ReadAdd = "read_additional",
        ReadProfits = "read_profits", ReadPart = "read_participation", ReadType = "read_type")
for (v in names(cv)) d[, paste0("cov_", cv[[v]]) := if (is.numeric(g[[v]])) g[[v]] else cl(g[[v]])]
d[, cov_duration_sec := as.integer(g$Q_TotalDuration)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gazmararian_2024_net_metering.csv"))
