##Terrorism / surveillance factorial vignette (Germany) from
##Jäger, F. (2023). Security vs. civil liberties: How citizens cope with threat, restriction,
##and ideology. Frontiers in Political Science, 4, 1006711. https://doi.org/10.3389/fpos.2022.1006711
##Replication data: Harvard Dataverse doi:10.7910/DVN/2ZOPHQ, CC0 1.0, no restricted files.
##File read: security_vs_civil_liberties_data.RData (one data.frame `data`, loaded into its own
##environment). Read as text, not run: security_vs_civil_liberties_replication_file.Rmd. Design and
##wording from the article (Section 3, open access XML) and the OSF preregistration
##(https://osf.io/7rs5v, questions q6, q7, q14, q15).
##Usage: Rscript jager_2023.R <raw dir> <output dir>
##
##2,045 German respondents (Bilendi & respondi access panel, June 2022, quotas on sex, age and
##education; attention-check failures already removed by the author), as in the article (N = 2,045).
##Each read ONE text vignette (4 x 3 x 3 x 3 full factorial between subjects, 108 vignettes, one per
##respondent assigned "randomly ... with equal probability", prereg q7), so task = 1 and profile = 1.
##Article example (manipulated parts in brackets): "Imagine that a terrorist attack conducted by
##[a right-wing group] takes place. An explosion occurs, injuring several people. [There is a serious
##danger for citizens like you, your family and friends.] To ensure that attacks like this are
##prevented in the future, politicians from [The Greens] want to increase surveillance measures.
##[These measures shall target every citizen in the country.] The measure includes the monitoring of
##telephone calls, letter mail, e-mails, and social media accounts, as well as chats on cell phones or
##smartphones." Each dimension has a control level in which "the attribute was not specified or
##mentioned" (article 3.2): stored as "(not shown)".
##Attribute text: the deposit holds only the author's short factor labels; the respondents' (German)
##wording of every level is not deposited and the article quotes only one vignette. Levels are
##therefore the author's labels, lightly cleaned: attr_motivation Islamist / right_wing ->
##"right-wing" / radical_climate -> "climate-radical" (the article's words); attr_threat "threat"
##(article: "There is a serious danger for citizens like you, your family and friends.") / "no threat";
##attr_party policy_from_AfD -> "AfD", policy_from_Greens -> "The Greens"; attr_target "dragnet"
##(article: "These measures shall target every citizen in the country.") / "targeted" (prereg:
##"suspicious groups and individuals"; the fielded wording is not deposited).
##Outcomes (all 1-10, stored raw, higher = more of the named quantity). Wording from the
##preregistration q15 (English, pre-fielding) so marked paraphrase; mapping of variables to
##questions from the author's Rmd (manipulation-check section names):
##  rating           vig_ter_policy: "To which degree do you support the surveillance measure?"
##                   1 do not support it at all - 10 strongly support it. Main outcome.
##  rating_efficacy  vig_ter_efficacy: "Do you feel this policy would be effective to reduce future
##                   terrorist attacks?" 1 not effective at all - 10 very effective.
##  rating_restrict  vig_ter_goal (Rmd: "Targeted has an effect on feeling restricted"): "Do you feel
##                   the surveillance measure would restrict you, your friends or family?"
##  rating_concern_personal vig_ter_percep1 (Rmd: concern_personal): concern about oneself or a
##                   family member being the victim of a terrorist attack in the future.
##  rating_concern_society  vig_ter_percep2 (Rmd: concern_social): concern that there will be a
##                   terrorist attack on German soil in the future.
##No choice, so no opt-out. Every respondent has the main outcome; the other four have 68-80 NA.
##Covariates kept with source names and codings (0-10 or 1-10 scales as stored): environment1-3,
##extremism1-2, fearfulness1-2, propensity_violence_1-4, party_pref_<party> (1 strong aversion - 10
##strong inclination, article 3.3), left_right, t_fear_soc_prior (pre-treatment societal fear).
##cov_vote_intention = party_pref factor text (vote intention, not party ID; "Not_allowed" = not
##eligible to vote). cov_gender from `female` (male -> male, female -> female, divers -> other).
##cov_age (years), cov_age_group (age_cat text), cov_educ_cat (author's low/medium/high grouping; not
##the survey's answer text, so not cov_education), cov_duration_sec (Qualtrics "Duration (in
##seconds)", whole survey). Dropped: t_fear_soc_post (post-treatment repeat of the fear item).
##No survey weight (article: "No weights were applied").
##Spot check (lm of rating on the four factors, CR SE by id, printed below) reproduces the article
##text exactly: dragnet -0.57, targeted (article: "targeted at suspect individuals or groups") 0.66,
##The Greens -0.49, AfD -0.91, each vs control.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "security_vs_civil_liberties_data.RData"), envir = e)
s <- as.data.table(e$data)
stopifnot(nrow(s) == 2045, uniqueN(s$id) == 2045, !anyNA(s$vig_ter_policy))
lv <- function(x, map) { x <- as.character(x); r <- unname(map[x]); stopifnot(!anyNA(r)); r }
ns <- "(not shown)"
d <- s[, .(id = as.integer(id), task = 1L, profile = 1L,
           rating = as.integer(vig_ter_policy), rating_efficacy = as.integer(vig_ter_efficacy),
           rating_restrict = as.integer(vig_ter_goal), rating_concern_personal = as.integer(vig_ter_percep1),
           rating_concern_society = as.integer(vig_ter_percep2),
           attr_motivation = lv(vig_t_motivation, c(control_motivation = ns, Islamist = "Islamist", right_wing = "right-wing", radical_climate = "climate-radical")),
           attr_threat = lv(vig_t_threat, c(control_threat = ns, threat = "threat", `no threat` = "no threat")),
           attr_party = lv(vig_t_party, c(control_party = ns, policy_from_AfD = "AfD", policy_from_Greens = "The Greens")),
           attr_target = lv(vig_t_target, c(control_policy = ns, dragnet = "dragnet", targeted = "targeted")))]
covs <- c("environment1", "environment2", "environment3", "extremism1", "extremism2", "fearfulness1", "fearfulness2",
          paste0("propensity_violence_", 1:4), paste0("party_pref_", c("CDUCSU", "SPD", "FDP", "Greens", "Left", "AfD")),
          "left_right", "t_fear_soc_prior")
for (v in covs) { stopifnot(all(s[[v]] == round(s[[v]]), na.rm = TRUE)); d[, paste0("cov_", v) := as.integer(s[[v]])] }
d[, cov_vote_intention := as.character(s$party_pref)]
stopifnot(all(as.character(s$female) %in% c("male", "female", "divers", NA)))
d[, cov_gender := c(male = "male", female = "female", divers = "other")[as.character(s$female)]]
d[, cov_age := as.integer(s$age)][, cov_age_group := s$age_cat][, cov_educ_cat := s$educ_cat]
d[, cov_duration_sec := as.integer(s$Duration..in.seconds.)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jager_2023_security_liberties.csv"))
if (requireNamespace("sandwich", quietly = TRUE)) {
  m <- lm(rating ~ attr_threat + attr_target + attr_motivation + attr_party, data = d)
  print(cbind(coef(m), sqrt(diag(sandwich::vcovCL(m, cluster = d$id)))))
}
