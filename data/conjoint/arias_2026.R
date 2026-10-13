##Local policymakers' support for climate plans: paired conjoint with ratings, US
##Arias, S. B., & Schwartz, J. A. (2026). Think globally, act locally: The determinants of local policy makers'
##support for climate policy. Perspectives on Politics (First View). https://doi.org/10.1017/S1537592726106070
##Replication data: Harvard Dataverse doi:10.7910/DVN/4OHGNA, CC0 1.0. File read: cjt_data_policymakers.tab
##(saved as d.tab; comma-separated despite the extension), with Perspectives_Replication.R and Read.Me.rtf read
##as text. Usage: Rscript arias_2026.R <dir holding d.tab> <output dir>
##
##573 elected US local policymakers (mayors, county executives, council members; CivicPulse panel; paper N = 573),
##up to 4 tasks of 2 hypothetical local climate plans = 4,204 profiles / 2,102 tasks (the paper reports "over 2,100
##paired-choice tasks"); 481 respondents have all 4 tasks (36, 26 and 30 have 1, 2 and 3). 7 attributes: type of property tax, higher energy
##efficiency standards for, economic relief, party endorsement, international participants, plan begins in,
##cost-benefit projection. Levels are the displayed text in the file. The file also records each attribute's row
##position (<attribute>.rowpos, 1-7): attrpos_ columns. The file is sorted by task and profile, not by respondent.
##Outcomes (the deposit has no questionnaire; wording from the article's description):
##  choice = `selected`, which of the two plans the respondent prefers ("choose which plan they prefer"); forced
##           choice, no opt-out (exactly one selected per task).
##  rating = `rank_outcome`, 1-5, each plan rated individually on a five-point support scale (article:
##           "rate each plan individually on a five-point scale"; 5 = strongly support, 4 = somewhat support per the
##           article's dichotomization; the labels of 1-3 are not stated; the selected plan has the higher score in
##           the data). 18 profiles have no rating (NA kept). The column name says "rank" but it is a rating.
##Covariates: cov_survey_weight = wt2 (the weight used in the replication code, defined for all 573), cov_gov_type
##(municipality / county / township), cov_state (state abbreviation), cov_party_id_code (PARTISANSHIP5 as recorded: 1-5
##without value labels in the deposit; 1,2 map to the authors' Republican bin and 4,5 to the Democratic bin),
##cov_gender_code (GENDER_num 1/2, unlabelled). Dropped: Response.ID (panel id; re-keyed), derived bins,
##the screener items, local demographic terciles, other weights, free items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "d.tab"))
x[, id := as.integer(factor(Response.ID))]
at <- c("Type of Property Tax" = "property_tax", "Higher Energy Efficiency Standards For" = "efficiency_standards", "Economic Relief" = "economic_relief",
        "Party Endorsement" = "party_endorsement", "International Participants" = "international_participants", "Plan Begins In" = "plan_begins_in",
        "Cost benefit Projection" = "cost_benefit")
rp <- c("Type of Property Tax" = "Type.of.Property.Tax.rowpos", "Higher Energy Efficiency Standards For" = "Higher.Energy.Efficiency.Standards.For.rowpos",
        "Economic Relief" = "Economic.Relief.rowpos", "Party Endorsement" = "Party.Endorsement.rowpos", "International Participants" = "International.Participants.rowpos",
        "Plan Begins In" = "Plan.Begins.In.rowpos", "Cost benefit Projection" = "Cost.benefit.Projection.rowpos")
d <- data.table(id = x$id, task = as.integer(x$task), profile = as.integer(x$profile), choice = as.integer(x$selected), rating = as.integer(x$rank_outcome))
for (nm in names(at)) { d[[paste0("attr_", at[nm])]] <- trimws(x[[nm]]); d[[paste0("attrpos_", at[nm])]] <- as.integer(x[[rp[nm]]]) }
d[, cov_survey_weight := x$wt2][, cov_gov_type := x$Gov_type][, cov_state := x$State_abb]
d[, cov_party_id_code := as.integer(x$PARTISANSHIP5)][, cov_gender_code := as.integer(x$GENDER_num)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, all(rating %in% c(1:5, NA))], uniqueN(d$id) == 573, nrow(d) == 4204)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "arias_2026_local_climate_plans.csv"))
