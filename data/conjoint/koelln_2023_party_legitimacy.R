##Party legitimacy vignette (Denmark): ideology x democratic behaviour of a fictitious party, from
##Kolln, A.-K. (2023). When do citizens consider political parties legitimate? British Journal of Political Science, 54(1), 110-128.
##https://doi.org/10.1017/S0007123423000364 (online 2023, print 2024; metadata from Crossref)
##Replication data: Harvard Dataverse doi:10.7910/DVN/Y7EIEC, CC0 1.0. Files read: PartyLeg_exp.csv (datafile 7127124; 4,423 rows =
##4,423 respondents, Denmark), codebook_partylegitimacy.pdf (7127120), Readme.pdf (7127121) and PartyLeg_Study2.R as text.
##Not used: PartyLeg_crosssec.csv (cross-sectional survey of real parties, not an experiment), PartyLeg_pilot.csv (pilot with different
##outcomes, no legitimacy outcome).
##Usage: Rscript koelln_2023_party_legitimacy.R <dir with the file; optional 3rd arg = file name, default PartyLeg_exp.csv> <output dir>
##
##Design: between-subject survey experiment; each respondent read ONE (news-article) description of a fictitious Danish party
##(the Readme calls it the survey experiment with 4,423 respondents; the pilot mentions "articles"). Factors (treat_ideol x treat_demo):
##  ideology:           centre, centre-left, centre-right, left-wing, right-wing  (5 levels)
##  democratic stance:  pro-democratic, anti-democratic  (2 levels)
##  The 10 cells are fully crossed (~395-411 respondents each) and a separate CONTROL group (410) got neither piece of information;
##  in the file both treat_ideol and treat_demo are the string "control" for them: coded here "(not shown)" for both attributes
##  (inference: the codebook says only "control"; the deposit does not hold the displayed text).
##Level text is the authors' treatment labels, NOT the displayed wording (the stimulus text is not deposited): same convention as
##levis_2026_carbon_messenger. 1 task x 1 profile per respondent; id = file row order (the file has a respondent id `caseid`, a panel
##identifier from Gallup, which is dropped and re-keyed).
##Outcomes (rating_*; the item wording is not in the deposit, only the codebook's names and ranges; all paraphrase):
##  rating_same_rights, rating_discuss_proposals, rating_accept_decisions: the three legitimacy items (need to grant the party the same
##    rights, need to discuss its proposals, need to accept its decisions), stored 0-1 (the codebook gives "Numeric 0-1"; the values are
##    k/6, so a rescaled 7-point item; higher = more legitimacy). Leg_01 (their mean index) is derived and dropped.
##  rating_democratic_practices (PercDemnorm): 1 "challenges current democratic practices" - 7 "endorses current democratic practices".
##  rating_threat (threat): 1 "it will pose a real threat to democracy if in power" - 7 "it will definitely not pose a threat"
##    (the codebook calls it reversed coding: higher = LESS threat).
##  rating_ideology (PercIdeol): perceived ideological position, "1 right wing, 2 centre right, 3 centre, 4 centre left, 5 left wing"
##    (reversed coding: higher = further left).
##  Missing outcome values are NA (item non-response / not asked): rows are kept when at least one outcome is present.
##No opt-out; no covariates in the file (the experimental file has none). No weights. Randomization restrictions: none documented.
##Respondent count: file 4,423 = the Readme's 4,423 (the paper's figure is not checked here). Rows kept = respondents with any outcome.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- if (length(a) >= 3) a[3] else "PartyLeg_exp.csv"
d <- fread(file.path(raw, f), encoding = "UTF-8")
stopifnot(nrow(d) == 4423, uniqueN(d$caseid) == 4423)
oc <- c("Leg_SameRights", "Leg_DiscussProposals", "Leg_AcceptDecisions", "PercDemnorm", "threat", "PercIdeol")
t <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating_same_rights = d$Leg_SameRights, rating_discuss_proposals = d$Leg_DiscussProposals,
  rating_accept_decisions = d$Leg_AcceptDecisions, rating_democratic_practices = as.integer(d$PercDemnorm),
  rating_threat = as.integer(d$threat), rating_ideology = as.integer(d$PercIdeol),
  attr_ideology = ifelse(d$treat_ideol == "control", "(not shown)", d$treat_ideol),
  attr_democratic_stance = ifelse(d$treat_demo == "control", "(not shown)", d$treat_demo))
stopifnot(all((t$attr_ideology == "(not shown)") == (t$attr_democratic_stance == "(not shown)")))
t <- t[rowSums(!is.na(t[, .SD, .SDcols = patterns("^rating_")])) > 0]
fwrite(t, file.path(out, "koelln_2023_party_legitimacy.csv"))
