##Audience-cost factorial vignette experiments (US president gender x foreign leader gender x
##party x crisis action) from
##Schwartz, J. A., & Blair, C. W. (2020). Do women make more credible threats? Gender stereotypes,
##audience costs, and crisis bargaining. International Organization, 74(4), 872-895.
##https://doi.org/10.1017/S0020818320000223
##Replication data: Harvard Dataverse doi:10.7910/DVN/LRP3SZ, CC0 1.0. Files read: TESS.tab,
##mTurk.tab, with TESS Codebook.pdf and mTurk Codebook.pdf (code meanings). Vignette text and
##question wording from the article's supplementary appendix (Cambridge sup001, pp. A.4-A.6 TESS,
##A.21-A.23 mTurk). Analysis R code read as text only.
##Usage: Rscript schwartz_2020.R <dir holding the two .tab files> <output dir>
##
##Two tables, one per sample (separate fieldings with slightly different vignette text; the
##article's main study is the pre-registered TESS survey, the mTurk survey an exploratory pilot
##reported in the appendix): schwartz_2020_audience_costs_tess (N = 2,342) and
##schwartz_2020_audience_costs_mturk (N = 1,607). One vignette per respondent (task = 1,
##profile = 1), "1 of 24 scenarios, equal assignment probability; names randomized" (TESS: blocked
##on respondent party ID; mTurk: party quota). Template (TESS): "A country sends its military to
##take over a neighboring country. The attacking country is controlled by a [female/male] leader.
##The [Republican/Democratic] U.S. President, [Erica/Eric, Stephanie/Steven] Smith, says [the United
##States will stay out of the conflict | that if the attack continues, the US military will push out
##the invaders]. The attacking country continues to invade. In the end, ... Smith [decides not to
##send troops | does not send troops | orders the military to engage], and the attacking country
##gains 20% of the contested territory [, and the US experiences zero casualties]." A bulleted
##summary repeats it.
##Attributes (text inserted into the template):
##  attr_opponent_gender  = FemaleOpp: female / male
##  attr_president_party  = DemocratUS (TESS) / PartyUS (mTurk): Republican / Democratic
##  attr_president_name   = the name shown: FemaleUS picks the gender, MaleName/FemaleName (TESS:
##                          0 Eric / 1 Steven, 0 Erica / 1 Stephanie) or male/female (mTurk, text)
##                          pick the name; "Erica Smith" etc. Gender is carried only by the name.
##  attr_action           = StayOut / NotEngage / Engage, as a short version of the displayed text:
##    "says the US will stay out; does not send troops", "threatens to push out the invaders; does
##    not send troops", "threatens to push out the invaders; sends troops (zero US casualties)".
##Outcomes:
##  rating = Disapproval, TESS "To what extent do you disapprove or approve of how the US President
##           handled the situation?", mTurk "What are your views about how the US President handled
##           the situation?"; 7 points, stored as the codebooks code it: 1 = Strongly approve,
##           7 = Strongly disapprove (higher = MORE disapproval; not reversed). The response row
##           was displayed from Strongly Disapprove to Strongly Approve.
##  rating_regime = RegimeConfounding / RegimeConf, post-treatment estimate of how democratic the
##           attacking country is, -10 least to 10 most democratic.
##  rating_nonwhite = NonWhiteConfounding / NonWhiteConf, the respondent's guess of the president's
##           race recoded by the authors to 1 = non-White, 0 = White (the raw race answer is not in TESS).
##Covariates keep the codebook codes: cov_gender (Gender: 0 Male = male, 1 Female = female),
##cov_party_id7_code (PartyID, 1 Strong Republican ... 7 Strong Democrat; only the ends labelled),
##cov_ideology (1 extremely/very conservative ... 7 liberal), attention checks as
##cov_attention_pass_<k> (TESS 1 president name, 2 attacker's sex, 3 president's party; mTurk 1 name,
##2 sex), sexism / militant-assertiveness / chauvinism / trust items, cov_sexism_order (0 asked
##pre-, 1 post-treatment); TESS cov_age4, cov_age7, cov_education5, cov_income6 (codebook categories
##have typos, so codes kept); mTurk cov_age (years), cov_education5.
##Dropped: the open-ended "four words" answers Q4_1-Q4_4 (free text), all derived dummies
##(StayOut..., MM_*..., DisapprovalBinary, aggregate attention scores, race dummies other than
##NonWhite; the mTurk raw race guess RaceConf is dropped too, NonWhiteConf is kept for parity with
##TESS) and TESS CaseId (re-keyed to 1..N after sorting by CaseId). mTurk PartyID holds only codes
##1-6 (as deposited). 4 TESS respondents have no Disapproval: 3 keep their row (other ratings
##present), 1 with all three outcomes missing is omitted (2,341 rows). No survey weight in TESS.tab.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
act <- c("says the US will stay out; does not send troops",
         "threatens to push out the invaders; does not send troops",
         "threatens to push out the invaders; sends troops (zero US casualties)")
core <- function(x, party, mname, fname) {
  stopifnot(x[, all(StayOut + NotEngage + Engage == 1L)], all(party %in% 0:1), all(x$FemaleUS %in% 0:1))
  d <- data.table(task = 1L, profile = 1L, rating = as.integer(x$Disapproval))
  d[, attr_opponent_gender := c("male", "female")[x$FemaleOpp + 1L]]
  d[, attr_president_party := c("Republican", "Democratic")[party + 1L]]
  d[, attr_president_name := paste(fifelse(x$FemaleUS == 1L, fname, mname), "Smith")]
  d[, attr_action := act[x[, StayOut + 2L * NotEngage + 3L * Engage]]]
  d[, cov_gender := c("male", "female")[x$Gender + 1L]]
  d
}
## TESS
t <- fread(file.path(raw, "TESS.tab"))
setorder(t, CaseId)
d <- core(t, t$DemocratUS, c("Eric", "Steven")[t$MaleName + 1L], c("Erica", "Stephanie")[t$FemaleName + 1L])
d[, `:=`(rating_regime = as.integer(t$RegimeConfounding), rating_nonwhite = as.integer(t$NonWhiteConfounding))]
d[, id := seq_len(.N)]
cv <- c(party_id7_code = "PartyID", ideology = "Ideology", age4 = "Age4", age7 = "Age7", white = "White", black = "Black",
        hispanic = "Hispanic", asian = "Asian", education5 = "Education5", income6 = "Income6", sexism_order = "SexismOrder",
        hostile_sexism_1 = "HostileSexism1", hostile_sexism_2 = "HostileSexism2", hostile_sexism_3 = "HostileSexism3",
        hostile_sexism_4 = "HostileSexism4", benevolent_sexism_1 = "BenevolentSexism1", benevolent_sexism_2 = "BenevolentSexism2",
        benevolent_sexism_3 = "BenevolentSexism3", benevolent_sexism_4 = "BenevolentSexism4", mil_assert_1 = "MilAssert1",
        mil_assert_2 = "MilAssert2", mil_assert_3 = "MilAssert3", attention_pass_1 = "AttentionCheck1",
        attention_pass_2 = "AttentionCheck2", attention_pass_3 = "AttentionCheck3")
for (v in names(cv)) d[, paste0("cov_", v) := as.integer(t[[cv[[v]]]])]
d <- d[!(is.na(rating) & is.na(rating_regime) & is.na(rating_nonwhite))]
setcolorder(d, "id"); setorder(d, id, task, profile)
stopifnot(nrow(d) == 2341L)
fwrite(d, file.path(out, "schwartz_2020_audience_costs_tess.csv"))
## mTurk (no respondent id: id = row number)
m <- fread(file.path(raw, "mTurk.tab"))
stopifnot(all(m$male %in% c("Eric", "Steven")), all(m$female %in% c("Erica", "Stephanie")))
d <- core(m, m$PartyUS, m$male, m$female)
d[, `:=`(rating_regime = as.integer(m$RegimeConf), rating_nonwhite = as.integer(m$NonWhiteConf))]
d[, id := seq_len(.N)]
cv <- c(party_id7_code = "PartyID", ideology = "Ideology", age = "Age", education5 = "Education", sexism_order = "SexismOrder",
        sexism_rescued = "SexismRescued", sexism_demands = "SexismDemands", sexism_complain = "SexismComplain",
        sexism_purity = "SexismPurity", mil_strength = "Strength", mil_war = "War", mil_force = "Force",
        chauvinism_superior = "Superior", chauvinism_ashamed = "Ashamed", trust = "Trust",
        attention_pass_1 = "AttentionUS", attention_pass_2 = "AttentionOpp")
for (v in names(cv)) d[, paste0("cov_", v) := as.integer(m[[cv[[v]]]])]
d <- d[!(is.na(rating) & is.na(rating_regime) & is.na(rating_nonwhite))]
setcolorder(d, "id"); setorder(d, id, task, profile)
stopifnot(nrow(d) == 1607L)
fwrite(d, file.path(out, "schwartz_2020_audience_costs_mturk.csv"))
