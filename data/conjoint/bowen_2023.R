##Nuclear vs conventional strike-choice conjoint (US) from
##Bowen, T., Goldfien, M. A., & Graham, M. H. (2023). Public opinion and nuclear use: Evidence
##from factorial experiments. The Journal of Politics, 85(1), 345-350.
##https://doi.org/10.1086/720329
##Replication data: Harvard Dataverse doi:10.7910/DVN/JZ4WG4, CC0 1.0, no restricted files.
##File read: BGG_mainstudy_choiceExperiment.csv. Codebook: BGG_readme.txt (variable list); the
##authors' ReplicationScript_BGG.R read as text, not run. No questionnaire is deposited and the
##article/appendix were not reachable, so outcome wording and the displayed level text are NOT
##known: the levels are the file's short labels (e.g. "90 percent", military casualties
##"High"/"Low"/"No", allies "Most"/"Few", civilian casualties "10"/"100"/"1000", environmental
##damage "Minimal"/"Moderate"/"Severe"), with the readme's attribute definitions.
##Usage: Rscript bowen_2023.R <dir holding BGG_mainstudy_choiceExperiment.csv> <output dir>
##
##Main study: 2,162 US respondents (survey weights in the file; vendor not documented in the
##deposit), 12 pairs of hypothetical military strikes ("Option 1" / "Option 2"), 6 attributes:
##strike type (Nuclear / Conventional), chance of destroying the target, military casualties,
##how many allies approve, civilian casualties, environmental damage. One row per pair in the
##source (s1_* = first option presented, s2_* = second); task = choiceNum, profile 1 = s1.
##Outcome: choice = which option was chosen (`choice` "Option 1"/"Option 2"); forced choice in
##the data (exactly one chosen when answered). 1,439 unanswered pairs are omitted; 84
##respondents answered none, so the table has 2,078 respondents.
##Spot check: none reproducible from the deposit (results files are not included); weighted
##choice shares: nuclear option chosen 36% in realistic pairs, 43% of nuclear profiles in fully
##randomized pairs.
##RANDOMIZATION RESTRICTED in half the tasks, recorded in trial_randomization (the source's
##Randomization): "Realistic" pairs (choices 1-6 for 2,145 respondents) always put a nuclear
##strike as Option 1 against a conventional Option 2 and fix how many military advantages and
##disadvantages the nuclear option has (readme nukeAdv, numDisadv); "Conjoint" pairs (choices
##7-12; and 2-6 for 17 respondents who have no choice 1) are fully randomized. The authors
##analyse the realistic block (Table 2) and the fully randomized block (AMCEs, Fig. D.7)
##separately; one table here, split by trial_randomization.
##Dropped: the authors' derived pair codings (adv_*, disadv_*, nukeAdv, numDisadv, types,
##mil_adv, disadv_index), the numeric *_N copies of covariates, `education` (copy of educ) and
##`ethnicity` (raw race question, free-text "other" entries appear in it; `race` kept).
##Covariates: cov_survey_weight (weight), age, gender, educ, race, hispanic, party ID, region,
##income bracket (hhi), employment, political interest/discussion/advice, the foreign-policy
##goal importance and use-of-force items (text answers), mobile, and the respondent's arms in the
##separate vignette experiment (s_num: nuclear-success treatment; d_num: destructiveness
##treatment). The PILOT conjoint (BGG_pilot_conjoint_diffs_clean.csv) is NOT built: it stores
##each pair twice with the nuclear strike moved to the first slot, so which option was shown
##first is not recoverable, and its covariates are unlabelled codes.
##Reserved covariates (BGG_readme.txt variable list; the file stores answer text): cov_age =
##age (years); cov_gender = gender "Female"/"Male" lowercased to female/male; cov_education =
##educ as stored ("Did not complete high school" .. "Graduate or professional degree", "None of
##the above"); cov_party_id7 = political_party ("respondent's partisan affiliation") as stored:
##the 7-point scale (Strong / Not very strong Democrat, Independent Democrat, Independent -
##neither, Independent Republican, Not very strong / Strong Republican) plus an "Other" branch
##(Other - leaning Democrat / Other - neither / Other - leaning Republican), 10 values.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "BGG_mainstudy_choiceExperiment.csv"))
stopifnot(uniqueN(s$id) == 2162, s[, .N, .(id, choiceNum)][, all(N == 1)])
s <- s[!is.na(choice)]
stopifnot(s[, all(choice %in% c("Option 1", "Option 2"))], s[, all(chosen == (choice == "Option 1"))])
att <- function(p) s[, .(attr_strike_type = get(paste0(p, "_strike")), attr_chance_of_success = get(paste0(p, "_chance")),
                         attr_military_casualties = get(paste0(p, "_mil")), attr_allies_approve = get(paste0(p, "_ally")),
                         attr_civilian_casualties = as.character(get(paste0(p, "_civ"))), attr_environmental_damage = get(paste0(p, "_env")))]
cv <- s[, .(cov_survey_weight = weight, cov_age = as.integer(age), cov_gender = tolower(gender), cov_education = educ, cov_race = race,
            cov_hispanic = hispanic, cov_party_id7 = political_party, cov_region = region, cov_income = hhi, cov_employment = employ,
            cov_pol_interest = pol_interest, cov_pol_discuss = pol_discuss, cov_pol_advice = pol_advice,
            cov_goal_defend_allies = foreign_defendAllies, cov_goal_energy_supply = foreign_energySupply,
            cov_goal_help_un = foreign_helpUN, cov_goal_prevent_nukes = foreign_preventNuke,
            cov_goal_prevent_terror = foreign_preventTerror, cov_goal_promote_democracy = foreign_promoteDem,
            cov_goal_promote_human_rights = foreign_promoteHR, cov_goal_free_trade = foreign_trade,
            cov_force_terrorist_camp = military_destroyTerrorist, cov_force_help_un = military_helpUN,
            cov_force_oil = military_oil, cov_force_democracy = military_promoteDem,
            cov_force_protect_allies = military_protectAllies, cov_force_stop_genocide = military_stopGenocide,
            cov_mobile = as.integer(mobile), cov_vignette_success_treat = as.integer(s_num),
            cov_vignette_destruct_treat = as.integer(d_num))]
base <- s[, .(id = as.integer(id), task = as.integer(choiceNum), trial_randomization = Randomization)]
d <- rbind(cbind(base, profile = 1L, choice = as.integer(s$choice == "Option 1"), att("s1"), cv),
           cbind(base, profile = 2L, choice = as.integer(s$choice == "Option 2"), att("s2"), cv))
setcolorder(d, c("id", "task", "profile", "choice"))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[trial_randomization == "Realistic" & profile == 1, all(attr_strike_type == "Nuclear")],
          d[trial_randomization == "Realistic" & profile == 2, all(attr_strike_type == "Conventional")])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bowen_2023_nuclear_strikes.csv"))
