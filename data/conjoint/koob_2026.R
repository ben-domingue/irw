##Protest-dimensions conjoint (South Africa) from
##Koob, S. A., & Justesen, M. K. (2026). Fighting for a better life: Protests and public
##opinion in South Africa. Comparative Political Studies. https://doi.org/10.1177/00104140261418611
##Replication data: Harvard Dataverse doi:10.7910/DVN/A0C0IE, CC0 1.0. Files read (each one
##data.frame, loaded into its own environment):
##  Rdataframe_sa_protest_conjoint_outcome_protest_sympathy.RData   (sa_protest_conjoint_out1)
##  Rdataframe_sa_protest_conjoint_outcome_policy_support.RData     (sa_protest_conjoint_out2)
##  Rdataframe_sa_protest_conjoint_outcome_protest_public_disorder.RData (sa_protest_conjoint_out4)
##  Rdataframe_sa_protest_conjoint_outcome_policy_deservingness.RData   (sa_protest_conjoint_out5)
##  Rdataframe_sa_protest_conjoint_diagnotstics.RData (same rows as out1 plus `Vignette`)
##Also read as text: Script3_..._Conjoint Analysis.R (the authors' analysis, not run). The
##article is paywalled and was not read; no codebook or questionnaire is deposited.
##Usage: Rscript koob_2026.R <dir holding the five .RData files> <output dir>
##
##1,591 South African respondents (online survey; panel and dates not in the deposit), 3 tasks
##x 2 hypothetical service-delivery protests, 6 attributes. Task and profile are recorded
##(cjoint-style long frames). The four outcome frames hold identical rows (respondent, task,
##profile, attributes; checked) and differ only in `selected`, so they are ONE table with four
##choice columns. Each is a forced choice: exactly one protest chosen per task (checked).
##Outcome wording is NOT in the deposit; the names below are the authors' file and script
##labels ("Outcome 'Protest sympathy'" etc.), so design_outcomes questions are paraphrases:
##  choice_sympathy     (out1, Figure 4a): the protest the respondent sympathizes with more
##  choice_policy       (out2, Figure 4b): the protest whose demands the respondent supports
##  choice_disorder     (out4): the protest seen as more of a public disorder (agrees with
##                      choice_sympathy on only 30% of profiles, so it points the other way)
##  choice_deserving    (out5): the protesters seen as more deserving
##(no out3 is deposited). Direction of each is "1 = this protest picked for the named
##property"; the exact question text should be checked against the article's appendix.
##Attributes: the Qualtrics conjoint labels are sentence stems, so the profile was a short text
##(stems: "There are around ...", "... protesting against ...", "They blame ...", "The protest
##involves ...", "The protest had lasted for ...", "... and the police ..."); levels are the
##displayed text as stored (e.g. "500 protesters", "lack of clean water", "the ward
##councillor", "road blocks", "7 days", "dissolve the protest by force"). The recorded row
##positions are constant (1-6 in the order above) for every respondent: fixed attribute order,
##so no attrpos_ columns. Restrictions not documented; every pair of levels occurs; level shares
##look uniform.
##Covariates: cov_vignette_arm (`Vignette`, Q4.1-Q4.5: which arm of the paper's earlier
##image-vignette experiment the respondent was assigned; constant within respondent; the
##authors check that the conjoint estimates do not differ by it, Appendix Figure D2),
##cov_q3_1_code and cov_race_code (Q3.1 and Q3.2 as stored, CODES; no labels in the deposit;
##the authors' recode `black` marks Q3.2 = 1 as "Black" and all other codes as "Other").
##Dropped: Response.ID (Qualtrics ResponseId, re-keyed to integers in file order), respondent
##and respondentIndex (row indices), the derived `black`, the *.rowpos columns (constant).
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ld <- function(f) { e <- new.env(); load(file.path(raw, f), envir = e); stopifnot(length(ls(e)) == 1); as.data.table(e[[ls(e)]]) }
p <- "Rdataframe_sa_protest_conjoint_"
o <- list(sympathy = ld(paste0(p, "outcome_protest_sympathy.RData")), policy = ld(paste0(p, "outcome_policy_support.RData")),
          disorder = ld(paste0(p, "outcome_protest_public_disorder.RData")), deserving = ld(paste0(p, "outcome_policy_deservingness.RData")))
g <- ld(paste0(p, "diagnotstics.RData"))
s <- o$sympathy
at <- c("Participants", "Grievance", "Blame", "Tactics", "Duration", "Police")
for (k in names(o)) stopifnot(identical(as.character(o[[k]]$Response.ID), as.character(s$Response.ID)),
                              all(o[[k]]$task == s$task), all(o[[k]]$profile == s$profile),
                              all(sapply(at, function(v) all(as.character(o[[k]][[v]]) == as.character(s[[v]])))))
stopifnot(identical(as.character(g$Response.ID), as.character(s$Response.ID)), all(g$task == s$task), all(g$profile == s$profile),
          all(g$selected == s$selected))
rp <- grep("rowpos", names(s), value = TRUE)
stopifnot(all(sapply(rp, function(v) uniqueN(s[[v]]) == 1)))
d <- data.table(id = match(s$Response.ID, unique(s$Response.ID)), task = as.integer(s$task), profile = as.integer(s$profile))
for (k in names(o)) d[, paste0("choice_", k) := as.integer(o[[k]]$selected)]
d[, attr_participants := as.character(s$Participants)][, attr_grievance := as.character(s$Grievance)]
d[, attr_blame := as.character(s$Blame)][, attr_tactics := as.character(s$Tactics)]
d[, attr_duration := as.character(s$Duration)][, attr_police := as.character(s$Police)]
d[, cov_vignette_arm := as.character(g$Vignette)]
d[, cov_q3_1_code := as.integer(as.character(s$Q3.1))][, cov_race_code := as.integer(as.character(s$Q3.2))]
stopifnot(uniqueN(d$id) == 1591, d[, .N, id][, all(N == 6)], !anyDuplicated(d[, .(id, task, profile)]),
          !anyNA(d[, .SD, .SDcols = patterns("^attr_|^choice_")]), d[, uniqueN(cov_vignette_arm), id][, all(V1 == 1)])
for (k in names(o)) stopifnot(d[, sum(get(paste0("choice_", k))), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "koob_2026_protest_dimensions.csv"))
