##Factorial vignette on political vigilantism in Ghana from
##Amoah, J. (2026). Rationalizing political violence: A survey experiment on political vigilantism in Ghana.
##(Replication data, preregistered survey experiment; the article DOI is not given in the deposit.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/HZOFLW, CC0 1.0. Files read: vigilantism_data.tab
##("original format" = the Qualtrics CSV), Verified_Vigilantism_Code_Final.R read as text (not run).
##Usage: Rscript amoah_2026.R <dir holding vigilantism_data.csv> <output dir>
##
##Qualtrics export, 2,603 social-media users in Ghana (2,192 with a recorded vignette arm). The first two data
##rows are header rows (question text, ImportId) and are removed; the narrative texts are in the header row.
##One vignette per respondent ("snippet of correspondence from our interview with members of a political vigilante
##group in Ghana"), 5 arms (treatment_assignment): placebo, t1..t4. The authors' code (lines 575-655) gives the arm
##meaning: t1 = NPP-affiliated group snatching ballot boxes, t2 = NDC snatching, t3 = NPP protecting, t4 = NDC protecting.
##Two attributes (2x2 plus a placebo arm that gives neither):
##  attr_vigilante_party: "New Patriotic Party (NPP)" / "National Democratic Congress (NDC)" ("a political party
##     contacted them for electoral purposes" in the placebo arm: the party is not shown -> "(not shown)")
##  attr_vigilante_action: the action bundled with the electoral area's record, as in the narrative: "snatch ballot
##     boxes (area with a reputation for peaceful elections)" / "protect ballot boxes (area with a reputation for
##     electoral malpractices)". Action and context are one factor (they never vary separately).
##     Placebo arm: the group "did not tell us their designated mandate": "(not shown)".
##Attribute text is a shortened form of the narrative's wording (full sentences in the deposit's header row).
##Outcomes (ratings, authors' numeric codes from the code file, case-insensitive: Qualtrics writes "Strongly agree"
##and "Strongly Agree"):
##  rating_justified: "To what extent do you agree or disagree with the statement: Given the context described above,
##     the actions of the vigilante group are justified or reasonable." 1 Strongly disagree ... 5 Strongly agree
##  rating_undermined_credibility: "... the actions of the vigilante group undermined the credibility of the election?" 1-5
##  rating_threat_democracy: "... the actions of the vigilante group described in the above narrative threaten Ghana's
##     democracy?" 1-5
##  rating_would_participate: "Given the actions of the vigilante group ..., would you be willing to participate in such
##     activities or encourage a close friend or relative to do so?" 0 No, I won't; 1 Maybe; 2 Yes, I will
##  rating_sign_petition: "Would you be willing to sign a petition calling for all political parties to disband their
##     affiliated political vigilante groups?" 0 No, I won't; 1 Maybe; 2 Yes, I will
##  rating_join_demonstration: "...take part in a public demonstration calling for all political parties to disband
##     their associated vigilante groups?" 0/1/2 as above
##Respondents with a recorded arm and at least one outcome are kept. Missing outcomes (late dropout) stay NA.
##Covariates (answer text as stored): cov_gender (Male/Female; blank = NA), cov_age_group, cov_party_id (party closest
##to the respondent's values: NPP, NDC or "Independent/Others"; leaners are not merged), cov_education, cov_income
##(monthly income band in GHS).
##Dropped: PII/identifier columns RecordedDate, ResponseId, RecipientLastName/FirstName/Email, ExternalReference (all
##Recipient* and ExternalReference cells are empty in the data rows), consent, free text (exp_justify, religion other),
##religion, employment, financial status, institutional trust items, party strength, election-integrity items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "vigilantism_data.csv"), colClasses = "character", na.strings = NULL)
setnames(k, trimws(names(k))); k <- k[-(1:2)]
stopifnot(all(k$RecipientEmail == "" & k$RecipientLastName == "" & k$ExternalReference == ""))
k <- k[treatment_assignment %in% c("placebo", "t1", "t2", "t3", "t4")]
lk <- function(x) match(tolower(trimws(x)), c("strongly disagree", "disagree", "neither agree nor disagree", "agree", "strongly agree"))
yn <- function(x) match(trimws(x), c("No, I won't", "Maybe", "Yes, I will")) - 1L
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
  rating_justified = lk(k$justify), rating_undermined_credibility = lk(k$elect_credibility),
  rating_threat_democracy = lk(k$threat_democracy), rating_would_participate = yn(k$will_paticipate),
  rating_sign_petition = yn(k$petition), rating_join_demonstration = yn(k$demonstration))
ta <- k$treatment_assignment
np <- "(not shown)"
d[, attr_vigilante_party := c(placebo = np, t1 = "New Patriotic Party (NPP)", t2 = "National Democratic Congress (NDC)",
                              t3 = "New Patriotic Party (NPP)", t4 = "National Democratic Congress (NDC)")[ta]]
d[, attr_vigilante_action := c(placebo = np,
   t1 = "snatch ballot boxes (area with a reputation for peaceful elections)", t2 = "snatch ballot boxes (area with a reputation for peaceful elections)",
   t3 = "protect ballot boxes (area with a reputation for electoral malpractices)", t4 = "protect ballot boxes (area with a reputation for electoral malpractices)")[ta]]
nz <- function(x) ifelse(trimws(x) == "", NA_character_, trimws(x))
d[, cov_gender := c(Male = "male", Female = "female")[nz(k$gender)]]
d[, cov_age_group := nz(k$age)][, cov_party_id := nz(k$party)][, cov_education := nz(k$education)][, cov_income := nz(k$income)]
rc <- grep("^rating_", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..rc])) > 0]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "amoah_2026_vigilantism.csv"))
