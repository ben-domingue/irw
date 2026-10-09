##Rebel-MP factorial vignettes (France, Germany, Italy, UK; main study) from
##Duell, D., Kaftan, L., Proksch, S.-O., Slapin, J., & Wratil, C. (2024). The rhyme and reason of
##rebel support: Exploring European voters' attitudes toward dissident MPs. Political Science
##Research and Methods, 12(2), 301-317 (online 2023). https://doi.org/10.1017/psrm.2023.26
##Replication data: Harvard Dataverse doi:10.7910/DVN/MWTZBD, CC0 1.0, no restricted files, no
##terms. Files read: data_rhymeAndReason.csv (main study; saved as main.csv) and
##codebook_rhymeAndReason.pdf (dataMaid summary: variable names and observed values). Design,
##wording and level meanings from the article (section 3, Tables 1-3; open access).
##The follow-up UK experiment (data_rhymeAndReasonExt*.csv, Dynata 2021, a different design with
##reminder treatments) is not built here.
##Usage: Rscript duell_2023.R <dir holding main.csv> <output dir>
##
##14,000 YouGov respondents, early 2020, 3,500 per country (cov_country; the authors pool the
##countries in their AMCEs, so one table). Each read five vignettes (task = `vignette`, the display
##position: it reproduces the authors' rand5_order for every respondent), one per bill/policy area,
##each describing one MP (profile = 1). Vignette-level attributes, "uniformly randomized at the
##vignette level" (article), stored as the authors' English labels (respondents saw French,
##German, Italian or English text; the full wording is in the article's appendix B.3.3, not read):
##  attr_policy_issue  Spending and taxes / EU competence / Ties to EU / Regulations / Immigration
##                     (each respondent sees all five, in random order)
##  attr_vote_outcome  Adopted / Rejected   ("Members of Parliament (MPs) [adopted/rejected] ...")
##  attr_pivotality    One vote majority / A large majority ("... by [one vote / a vast majority]")
##  attr_mp_gender     Female MP / Male MP
##  attr_mp_party      Government / Opposition ("... belongs to a party that is currently in ...")
##  attr_mp_vote       the MP's vote vs party leadership, authors' labels: "voted for the bill,
##                     whereas party leadership voted against the bill" (rebel) etc.; the source
##                     label "voted against the bill and [GENDER2] party leadership voted against
##                     the bill" has its pronoun placeholder removed to match the other three
##  attr_mp_tenure     First term / Third term
##Respondent-level information arms (Table 3; 7 versions, trial_info_version = the authors'
##`treatment`: Baseline, With voter, Against voter, With public, Against public, With
##voter-Against public, Against voter-With public), which decide whether two further vignette
##elements are shown:
##  attr_bill_direction  the displayed direction of the bill (directiontext, e.g. "increases social
##                       spending by increasing taxes"; "[country]" kept as in the source) or
##                       "(not shown)" in versions without direction information. In the versions
##                       with it, the direction was chosen relative to the respondent's own stated
##                       preference (aligned / opposed), so it is not independent of cov_pref_*.
##  attr_public_support  "The majority of the public was for the bill" / "... against the bill"
##                       (Table 2 wording, from `public`) or "(not shown)".
##Outcomes (article section 3), 7-point, stored as in the source:
##  rating_represented = feel.represented "How well do you feel represented by this MP?"
##                       1 Not at all .. 7 Very well
##  rating_like_mp     = like.this.mp "Do you agree or disagree with the following statement: Every
##                       [nationality] MP should be like this MP." 1 Strongly disagree .. 7 Strongly agree
##  rating_trait_<t>   = after the LAST vignette only: "Which of the following character traits
##                       would you say describes the MP best? Please choose up to 3 of them",
##                       1 = chosen, 0 = not (14 traits). The source repeats the answers on all
##                       five rows; here they sit on task 5 (the MP they refer to), NA on tasks 1-4.
##No opt-out (ratings). No missing outcomes.
##Covariates: cov_country; cov_gender (genderRespondent Female/Male -> female/male); cov_age (years);
##cov_education_code (education 1-7: the codebook gives no labels); cov_pref_<issue> (the respondent's
##stated preference before the vignettes, *_pos 1/2 mapped to the article's Table 1 options;
##verified: code 1 + the bill's option-1 direction = "In line with respondent's preference" in the
##authors' `direction`); cov_vote_choice (voteChoice text; a vote intention, not party id; "I prefer
##not to answer" -> NA). Dropped: q15_other (free text), unlabelled items (urban_rural, q12, q13_5,
##q15, q17_*, q20_*, salience *_sal_s, trustGovernment, interestPolitics), the authors' derived
##variables (type, treatment.group, direction, behavior.*, rebel, position.num, outcome2, gender2,
##treat, authoritarian, populist, rand5), timing. No survey weight in the deposit; no attention
##check; no repeated task.
##N = 14,000 respondents / 70,000 vignettes, as in the article. Spot check (OLS, SE clustered by
##id): rebel vs non-rebel MP +0.063 (0.014) on rating_like_mp and -0.025 (0.014) on
##rating_represented; "honest" chosen 6.5 points more often for a rebel (task 5) -- the article's
##pattern (voters like rebels and credit them with traits, but do not feel better represented).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "main.csv"), encoding = "UTF-8", na.strings = c("NA", "", "__NA__"))
stopifnot(nrow(s) == 70000, s[, .N, resid][, all(N == 5)], s[, uniqueN(vignette), resid][, all(V1 == 5)])
# vignette = display position: bill index (Table 1 order) at position k equals rand5_order[k]
bix <- c("Spending and taxes" = 1L, "EU competence" = 2L, "Ties to EU" = 3L, "Regulations" = 4L, "Immigration" = 5L)
ord <- lapply(strsplit(gsub("[][ ]", "", s$rand5_order), ","), as.integer)
stopifnot(all(mapply(function(o, v, b) o[v] == b, ord, s$vignette, bix[s$bill])))
d <- data.table(id = as.integer(s$resid), task = as.integer(s$vignette), profile = 1L,
                rating_represented = as.integer(s$feel.represented), rating_like_mp = as.integer(s$like.this.mp),
                attr_policy_issue = s$bill, attr_vote_outcome = s$outcome, attr_pivotality = s$margin, attr_mp_gender = s$genderMP,
                attr_mp_party = s$party, attr_mp_vote = sub("[GENDER2] ", "", s$position, fixed = TRUE), attr_mp_tenure = s$term,
                attr_bill_direction = fifelse(is.na(s$directiontext), "(not shown)", s$directiontext),
                attr_public_support = fifelse(is.na(s$public), "(not shown)",
                                              c("Public for bill" = "The majority of the public was for the bill",
                                                "Public against bill" = "The majority of the public was against the bill")[s$public]),
                trial_info_version = s$treatment)
stopifnot(all(d$rating_represented %in% 1:7), all(d$rating_like_mp %in% 1:7), uniqueN(d$attr_mp_vote) == 4)
# direction / public shown exactly in the versions that carry them (Table 3)
stopifnot(d[attr_bill_direction != "(not shown)", all(trial_info_version %in% c("With voter", "Against voter", "With voter-Against public", "Against voter-With public"))],
          d[attr_public_support != "(not shown)", all(trial_info_version %in% c("With public", "Against public", "With voter-Against public", "Against voter-With public"))])
tr <- c("independent", "loyal.to.party", "honest", "strong.convictions", "defends.interest.voters", "willing.to.compromise", "untrustworthy",
        "selfish", "disrespectful", "decisive", "irresponsible", "cowardly", "unreliable", "stupid")
for (t in tr) {
  stopifnot(s[, uniqueN(get(t)), resid][, all(V1 == 1)], all(s[[t]] %in% 0:1))
  d[, paste0("rating_trait_", gsub(".", "_", t, fixed = TRUE)) := fifelse(task == 5L, as.integer(s[[t]]), NA_integer_)]
}
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
pref <- list(social = c("Increase social spending by increasing taxes.", "Decrease social spending in order to cut taxes."),
             eu1 = c("Increase the number of areas in which the EU can make policy.", "Decrease the number of areas in which the EU can make policy."),
             eu2 = c("Strengthen [country]'s ties to the EU.", "Weaken [country]'s ties to the EU."),
             climate = c("Establish new environmental regulations, imposing costs on businesses, but helping the fight against climate change.",
                         "Remove existing environmental regulations, helping businesses generate economic growth, but hindering the fight against climate change."),
             immigration = c("Make it easier for foreigners to immigrate to [country].", "Make it harder for foreigners to immigrate to [country]."))
nmp <- c(social = "social_spending", eu1 = "eu_competences", eu2 = "eu_ties", climate = "climate", immigration = "immigration")
# code 1 = Table 1 option 1: check against the authors' direction flag
x <- s[!is.na(direction)]
x[, pos := fcase(bill == "Spending and taxes", social_pos, bill == "EU competence", eu1_pos, bill == "Ties to EU", eu2_pos,
                 bill == "Regulations", climate_pos, bill == "Immigration", immigration_pos)]
x[, opt1 := directiontext %like% "^(increases social|increases the number|strengthens|establishes|makes it easier)"]
stopifnot(x[, all((direction %like% "^In line") == ((pos == 1) == opt1))])
d[, `:=`(cov_country = s$country, cov_gender = tolower(s$genderRespondent), cov_age = as.integer(s$age), cov_education_code = as.integer(s$education))]
for (p in names(pref)) { v <- s[[paste0(p, "_pos")]]; stopifnot(all(v %in% 1:2)); d[, paste0("cov_pref_", nmp[[p]]) := pref[[p]][v]] }
d[, cov_vote_choice := fifelse(s$voteChoice %in% c("I prefer not to answer"), NA_character_, s$voteChoice)]
stopifnot(all(d$cov_gender %in% c("female", "male")))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "duell_2023_rebel_mps.csv"))
