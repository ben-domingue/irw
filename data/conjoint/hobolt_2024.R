##Controversial-candidate conjoint (England) from
##Hobolt, S. B., & Osnabrügge, M. (2024). Countering authoritarian behavior in democracies.
##Political Behavior, 47(2), 781-800. https://doi.org/10.1007/s11109-024-09971-5 (open access)
##Replication data: Harvard Dataverse doi:10.7910/DVN/EBSUNP, CC0 1.0, no restricted files.
##File read: data_analysis.dta (Dataverse "original format" download; one row per profile,
##40,120 rows). README.docx and the three analysis scripts were read as text.
##Usage: Rscript hobolt_2024.R <dir holding the .dta> <output dir>
##
##4,012 English adults (Deltapoll, Dynata panel, February 2021; the article's N), 5 tasks of 2
##hypothetical parliamentary candidates, each involved in a controversy, 6 attributes.
##Level text: the article's Table 1 (the displayed features); the .dta value labels are
##shortened versions of the same text and are mapped one to one (e.g. "Argued that a politician
##constitutes a threat" -> "Argued that a politician from a different party constitutes a threat
##to Britain"; "Claimed GBP 20,000 as parliamentary expenses" -> "Claimed £20,000 as parliamentary
##expenses for private purposes").
##task = `round` (1-5); profile = `panel` (left = 1, right = 2).
##Attribute order varied randomly, except that the reacting actor always appears directly above
##the reaction (article fn 7); the order is not recorded. Restrictions: none documented; the
##controversy x reaction cells are balanced.
##Outcomes ("After receiving information on two candidates, respondents choose one candidate and
##rate both", article p. 7; exact wording not in the deposit or article):
##  choice = `chosen`, forced choice (every task has exactly one chosen profile).
##  rating = 7-point rating of each candidate. The deposit only has the authors' 0-1 rescaling
##    (`rating2` = 0, 1/6, ..., 1); stored back on 1-7 as rating2 * 6 + 1. Direction: chosen
##    candidates average 4.0, unchosen 2.8, so higher = more favourable; anchor labels unknown.
##Covariates: cov_age (years); cov_threat_* = Q32-Q39, "how far respondents perceive the
##controversies as a threat for democracy", 1 = no threat to 10 = serious threat, 97 = don't
##know (kept as coded), for the eight controversies (item mapping from the comments in
##3-further_analysis.R).
##Dropped: ID (re-keyed 1..n), pair_id, the authors' attribute dummies (threat_britain ...
##minister), the dichotomised attitude scales (party_identity, pluralism, authoritarianism,
##democracy: "low/high" splits), and the respondent dummies gender_respondent,
##think_conservative, high_school, high_income (derived; their coding is undocumented).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "data_analysis.dta"))))
contro <- c("Argued that a politician from a different party constitutes a threat to Britain",
            "Argued that the government may ignore courts in times of crisis",
            "Argued that the government may rule without consulting Parliament in times of crisis",
            "Argued that the government should exclude certain journalists from press briefings",
            "Claimed £20,000 as parliamentary expenses for private purposes",
            "Encouraged online harassment of a politician from a different party",
            "Had an extramarital affair with a parliamentary assistant",
            "Ignored multiple messages from constituents")
actor <- c("Multiple MPs from another party", "Multiple MPs from the candidate's own party")
action <- c("Called for the candidate to be expelled from the parliamentary party on the grounds that the candidate's behavior was damaging to democracy",
            "Criticized the candidate's behavior for damaging democracy",
            "Defended the candidate's behavior",
            "Did not react to the candidate's behavior",
            "Refused to work with the candidate on the grounds that the candidate's behavior was damaging to democracy")
stopifnot(s$panel %in% c("left", "right"))
d <- data.table(id = frank(s$ID, ties.method = "dense"), task = as.integer(s$round),
                profile = ifelse(s$panel == "left", 1L, 2L), choice = as.integer(s$chosen),
                rating = as.integer(round(s$rating2 * 6 + 1)),
                attr_controversy = contro[s$Controversy], attr_reaction_actor = actor[s$ReactionxActor],
                attr_reaction = action[s$ReactionxAction], attr_gender = c("Female", "Male")[s$Gender],
                attr_party = c("Conservative", "Labour")[s$Party], attr_minister = c("No", "Yes")[s$Minister],
                cov_age = as.integer(s$age))
th <- c(Q32 = "courts", Q33 = "parliament", Q34 = "threat_britain", Q35 = "online_harassment",
        Q36 = "exclude_journalists", Q37 = "expenses", Q38 = "affair", Q39 = "ignored_messages")
for (q in names(th)) d[, paste0("cov_threat_", th[[q]]) := as.integer(s[[q]])]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, .N, .(id, task)][, all(N == 2)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7),
          all(abs(s$rating2 * 6 - round(s$rating2 * 6)) < 1e-6))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hobolt_2024_authoritarian_reactions.csv"))
