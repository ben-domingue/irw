##Trade-agreement conjoints (Spain, Poland, United Kingdom) from
##Dür, A., Hee, S., & Huber, R. A. (2025). A fair deal: Inequity aversion and individual
##attitudes toward trade agreements. The Review of International Organizations.
##https://doi.org/10.1007/s11558-025-09597-0 (open access, CC BY 4.0; design facts below are
##from its Section 3-5, Tables 1 and 3 and footnotes 4-7, 16-17)
##Replication data: Harvard Dataverse doi:10.7910/DVN/TBTCPB, CC0 1.0, no restricted files.
##Files read: exp1.RDS, respondent.RDS (Study 1, Spain + Poland); GB_exp2.rds,
##GB_respondent.rds (Study 2, UK). Not used: GB_exp1.rds (a list experiment, not a conjoint),
##all_codings.RDS (codings of open answers). Authors' study1.R / study2.R / README.Rmd read as text.
##Usage: Rscript dur_2025.R <raw dir> <output dir>
##
##Both surveys administered by bilendi; Study 1 in Poland and Spain in 2022 (3,000 per country,
##quotas on age, gender, region, income), Study 2 in Great Britain in 2023 (2,128, quotas on
##age, region, gender). Each respondent saw 5 pairs of hypothetical trade agreements (round
##1-5 = task, side A/B = profile 1/2), chose one and rated both. Outcomes, both studies:
##  choice: which agreement the respondent prefers (forced, exactly one per task; the article
##          paraphrases "choose between ... two hypothetical trade agreements"; the deposit has
##          no questionnaire, so wording is a paraphrase)
##  rating: 1-7, stored as in the source; Study 1 value labels 1 "muy en contra" .. 7 "muy a
##          favor" (the Spanish labels ship for both countries), Study 2 1 "strongly oppose" ..
##          7 "strongly favour". 93% (Study 1) and 89% (Study 2) of choices agree with ratings
##          (article fn 4, 16); kept as answered.
##THREE TABLES. Study 1 is split by country although the authors pool it with a country
##control: the displayed attribute text differs (amounts in euro in Spain and in zloty x5 in
##Poland, fn 7; "The average citizen in Spain/Poland"). Study 2 has a different attribute set.
##  dur_2025_trade_spain, dur_2025_trade_poland (Study 1). Attributes, as an ENGLISH rendering
##  of the article's Table 1 example (respondents saw Spanish or Polish, which is not
##  deposited): attr_gain_personal ("You personally": "gain €130 per year from the agreement" /
##  "lose €50 per year from the agreement"), attr_gain_citizen ("The average citizen in
##  Spain": "gains ..."/"loses ..."), attr_gain_foreign ("The average citizen in the other
##  country"), attr_partner_size ("The agreement is signed with a": small economy / large
##  economy), attr_trade_volume ("Spain and the other country currently trade": source codes
##  small / large shown as "little" / "a lot", as in Table 1), attr_implementation ("The
##  agreement will be implemented in": 2023 / 2027). Amounts in the source are euro values
##  -100..300 in steps of 10; for Poland the text shows 5 x the value in zloty (fn 7: "we
##  indicated the monetary values in zloty, and multiplied the values by 5"), rendered here as
##  "gain 650 zloty per year from the agreement" (the Polish wording and currency spelling are
##  not deposited). Restriction: no agreement with losses on all three payoffs, and a pair was
##  redrawn when A and B had identical payoffs (article p. 13; the authors' `weight` offsets the
##  restriction and is not kept). The three payoffs formed one block whose internal order was
##  randomized, and the block and the other three attributes were randomized in order (Table 1
##  note); whether per task or per respondent is not stated, and the order was not recorded.
##  dur_2025_trade_uk (Study 2): attr_partner_size ("The agreement is signed with a...": large
##  economy / small economy), attr_trade_volume ("Great Britain and the other country currently
##  trade...": a lot / little), attr_gain_personal ("Your personal gains are...": small /
##  medium / large), attr_gain_citizen_relative ("The average citizen in Great Britain
##  gains...": source less / same / more shown as "less than you" / "about the same" / "more
##  than you", Table 3 and its note), attr_implementation (2024 / 2028). English as displayed.
##  Order of the five attributes randomized (payoffs kept together), not recorded; pairs
##  identical on the two payoffs were redrawn.
##Covariates, Study 1 (respondent.RDS): cov_gender (Female/Male/Other -> female/male/other),
##cov_age (years), cov_region (text), cov_education (edu text as stored, English categories),
##cov_employment (employ_raw text), cov_hhsize (QHouseholdSize, 10 = "10 o más"),
##cov_income_code (QIncome code 1-10; the shipped labels are Spanish euro brackets, kept as
##codes because the Polish brackets are not given), cov_pol_interest (QInterest 1 "Nada
##interesado" .. 10 "Muy interesado"), cov_id_neighbor / cov_id_region / cov_id_country /
##cov_id_eu (QIdentity closeness, 1 "En absoluto cercana/o" .. 4 "Muy cercana/o"), cov_lrecon
##(economic left-right 0-10 as stored), cov_loi (the panel's length-of-interview field, unit not
##stated). Study 2 (GB_respondent.rds): cov_egotropic, cov_sociotropic, cov_fair, cov_equal
##(agreement text, Strongly disagree .. Strongly agree; the statements are in the article's
##Section 6 battery), cov_income_improve / cov_income_worsen (how much a £300 gain / loss would
##change living conditions, answer text).
##Dropped: expid (design draw id), the authors' derived scales and dummies (NatChauvinism,
##socTrust, intTrust, polTrust, NatInt, uni, employ, income_cat, recode_employ), nuts1, the
##authors' design weight. Respondent ids "ES_166" etc. re-keyed to integers within each table;
##UK ids kept. No survey weight is deposited.
##N: Spain 2,999 and Poland 2,999 respondents in exp1 (the article says 3,000 each;
##ES_2027 and PL_2218 are in respondent.RDS without conjoint rows); UK 2,128, matching the
##article (10,640 choices, 21,280 ratings). Spot check: OLS of UK choice and rating on the five
##attributes reproduces the article's Table 4 exactly (choice: medium 0.14, large 0.21, same
##0.17, more 0.02, small partner -0.04, little trade -0.07, 2028 -0.14, intercept 0.44; rating:
##0.23, 0.35, 0.34, 0.03, -0.03, -0.13, -0.19, 4.33).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
## ---- Study 1
s <- as.data.table(readRDS(file.path(raw, "exp1.RDS")))
r <- as.data.table(readRDS(file.path(raw, "respondent.RDS")))
stopifnot(s[, .N, .(id, round)][, all(N == 2)], s[, sum(choice), .(id, round)][, all(V1 == 1)],
          !anyNA(s$rating), all(s$side %in% c("A", "B")),
          all(c(s$individual, s$societal, s$foreign) %in% seq(-100, 300, 10)),
          s[individual < 0 & societal < 0 & foreign < 0, .N] == 0)
money <- function(v, cty, third) {
  amt <- if (cty == "ES") paste0("€", abs(v)) else paste(abs(v) * 5, "zloty")
  verb <- if (third) ifelse(v < 0, "loses", "gains") else ifelse(v < 0, "lose", "gain")
  paste(verb, amt, "per year from the agreement")
}
lab <- function(x) { y <- as.integer(unclass(x)); attributes(y) <- NULL; y }
for (cty in c("ES", "PL")) {
  x <- s[country == cty]; rr <- r[match(x$id, r$id)]
  stopifnot(!anyNA(rr$id))
  d <- x[, .(id = match(id, unique(sort(id))), task = as.integer(round), profile = match(side, c("A", "B")),
             choice = as.integer(choice), rating = lab(rating),
             attr_gain_personal = money(individual, cty, FALSE),
             attr_gain_citizen = money(societal, cty, TRUE),
             attr_gain_foreign = money(foreign, cty, TRUE),
             attr_partner_size = as.character(partner_size),
             attr_trade_volume = c(small = "little", large = "a lot")[as.character(trade_volume)],
             attr_implementation = as.character(implementation))]
  stopifnot(!anyNA(d$attr_trade_volume), all(d$rating %in% 1:7))
  d[, `:=`(cov_gender = c(Female = "female", Male = "male", Other = "other")[as.character(rr$gender)],
           cov_age = as.integer(rr$age), cov_region = as.character(rr$region),
           cov_education = as.character(rr$edu), cov_employment = as.character(rr$employ_raw),
           cov_hhsize = lab(rr$hhsize), cov_income_code = lab(rr$income), cov_pol_interest = lab(rr$polInterest),
           cov_id_neighbor = lab(rr$id_neighbor), cov_id_region = lab(rr$id_region),
           cov_id_country = lab(rr$id_country), cov_id_eu = lab(rr$id_EU),
           cov_lrecon = as.numeric(rr$lrecon), cov_loi = as.numeric(rr$loi))]
  stopifnot(!anyNA(d$cov_gender))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("dur_2025_trade_", c(ES = "spain", PL = "poland")[cty], ".csv")))
}
## ---- Study 2 (UK)
g <- as.data.table(readRDS(file.path(raw, "GB_exp2.rds")))
gr <- as.data.table(readRDS(file.path(raw, "GB_respondent.rds")))
stopifnot(g[, .N, .(id, round)][, all(N == 2)], g[, sum(choice), .(id, round)][, all(V1 == 1)], uniqueN(g$id) == 2128)
rr <- gr[match(g$id, gr$id)]; stopifnot(!anyNA(rr$id))
d <- g[, .(id = as.integer(id), task = as.integer(round), profile = match(side, c("A", "B")),
           choice = as.integer(choice), rating = lab(rating),
           attr_partner_size = as.character(partner_size), attr_trade_volume = as.character(trade_volume),
           attr_gain_personal = as.character(ind),
           attr_gain_citizen_relative = c(less = "less than you", same = "about the same", more = "more than you")[as.character(soc)],
           attr_implementation = as.character(year))]
stopifnot(!anyNA(d$attr_gain_citizen_relative), all(d$rating %in% 1:7))
for (v in c("egotropic", "sociotropic", "fair", "equal", "income_improve", "income_worsen")) d[, paste0("cov_", v) := as.character(rr[[v]])]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dur_2025_trade_uk.csv"))
