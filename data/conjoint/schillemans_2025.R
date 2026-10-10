##Nonpunitive-accountability conjoint (Danish public leaders) from
##Schillemans, T., & Aleksovska, M. (2025). Making nonpunitive accountability matter: Exploring
##behavioral effects of nonpunitive accountability in a conjoint experiment. Public
##Administration. https://doi.org/10.1111/padm.13024 (article identified by web search; not read)
##Replication data: DANS Data Station SSH doi:10.17026/SS/NFEZ09 ("Steering and accountability
##agencies and educational institutions Denmark", T. Schillemans), CC BY-NC 4.0, no restricted
##files, no terms. Files read: replication_data.tab (CSV), Codebook.pdf (level text); the authors'
##replication_code_final.R read as text (not run).
##Usage: Rscript schillemans_2025.R <raw dir> <output dir>
##
##385 leaders of Danish agencies (cov_sample "agencies") and educational institutions
##("educational institutions"), fielded 2020; one table, because the authors pool the two samples
##and compare them (cj(..., by = ~ sample)) over identical attributes. Each respondent saw up to two
##pairs of demands (2 profiles each; codebook `option` 1 = first, 2 = second profile), 5 binary
##attributes. trial_forum = who issued the demands (codebook "Type of accountability forums
##issuing demands": principal / stakeholder): in 383 of 385 respondents' first pair it is
##"principal" and every second pair is "stakeholder".
##TASK IS INFERRED FROM ROW ORDER: the file has no task column; rows run per respondent with option
##1,2,1,2. Pairs are rows 1-2 and 3-4 (verified: every inferred pair has option 1 then 2 and exactly
##one chosen profile, and forum is constant within a pair). 9 respondents have one pair only (7
##principal, 2 stakeholder); theirs is numbered task 1 whichever forum it was.
##Outcome: choice = Chosen ("Selected profile", codebook); the question wording is not deposited.
##The level texts ("If you prioritize this demand ...") show the choice was which demand to
##prioritize; recorded as a paraphrase. Forced choice, no opt-out.
##Attributes: the level text is the codebook's description of each level (English; the codebook's
##short tag, e.g. "Informal demand", is in the data and mapped 1:1; the tag "Faming" is the
##codebook's). Respondents were Danish leaders; the deposit does not say in which language the survey
##was shown, so the English codebook text may be a translation. No source documents restrictions,
##level probabilities or attribute order.
##Covariates (codebook): cov_gender (gender male/female; the source's one category "other / prefer
##not to say" (10 respondents) cannot be split into other vs refusal and is NA), cov_age_group
##("prefer not to say" -> NA), cov_educational_background (field of education: law, social
##sciences / humanities, management / finance, technical / natural sciences, other),
##cov_leadership_tenure (years), cov_recognize_decision ("Can you recognize the described
##decision-making situations in your work?" 1 = I experience such situations very often, 2 = from
##time to time, 3 = I recognize these situations in the work of my colleagues, but not my own work,
##4 = Such situations occur very rarely in my workplace, 5 = I have never heard of, or experienced
##such situation before), cov_contact_ministry and cov_contact_stakeholders (1 = Yes, often ..
##4 = never in contact), cov_sample. No survey weight. Qualtrics ResponseId re-keyed.
##N: the article reports 761 decisions, which equals the 761 tasks here.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.tab"), na.strings = c("NA", ""))
for (v in c("gender", "age_group", "educational_background")) set(s, which(s[[v]] == "NA"), v, NA_character_)  # quoted "NA" strings in the export
s[, r := seq_len(.N), ResponseId]
s[, task := (r + 1L) %/% 2L]
stopifnot(all(s$option == 2L - s$r %% 2L), s[, .(sum(Chosen), .N, uniqueN(forum)), .(ResponseId, task)][, all(V1 == 1 & N == 2 & V3 == 1)])
d <- data.table(id = as.integer(factor(s$ResponseId, levels = unique(s$ResponseId))), task = s$task,
                profile = s$option, choice = as.integer(s$Chosen))
lv <- function(x, map) { stopifnot(all(x %in% names(map))); unname(map[x]) }
d[, `:=`(
  attr_setting = lv(s$Setting_of_demand, c("Informal demand" = "The demand is voiced in some informal setting",
                                           "Formal demand" = "The demand is voiced during a formal meeting")),
  attr_past_experience = lv(s$Past_experience, c(
    Positive = "There have been no struggles at all with this stakeholder in the past, a good collaboration",
    Negative = "There have been many struggles with this stakeholder in the past; a problematic collaboration")),
  attr_wording = lv(s$Wording_of_demand, c(
    Collaborative = "It is kindly asked to help find a good solution in this important matter",
    Confrontational = "It is forcefully stressed that it is absolutely necessary to give priority to this demand")),
  attr_consequences = lv(s$Potential_consequences, c(
    Faming = "If you prioritize this demand, you will be praised in your professional network",
    Shaming = "If you do not prioritize this demand, you will be blamed by your professional network or stakeholders")),
  attr_timing = lv(s$Timing_of_demand, c(
    Expected = "The demand was expected; you knew all along this was going to happen at some point",
    Unexpected = "The demand comes as a big surprise; you did not expect this at all")))]
d[, trial_forum := s$forum]
stopifnot(all(s$gender %in% c("male", "female", "other / prefer not to say", NA)))
d[, cov_gender := fifelse(s$gender %in% c("male", "female"), s$gender, NA_character_)]
d[, cov_age_group := fifelse(s$age_group == "prefer not to say", NA_character_, s$age_group)]
d[, `:=`(cov_educational_background = s$educational_background, cov_leadership_tenure = s$leadership_tenure,
         cov_recognize_decision = s$recognize_decision, cov_contact_ministry = s$contact_ministry,
         cov_contact_stakeholders = s$contact_stakeholders, cov_sample = s$sample)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "schillemans_2025_accountability.csv"))
