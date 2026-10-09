##Swiss candidate-choice conjoint (Survey Experiment 2) from
##Portmann, L. (2022). What makes a successful candidate? Political experience and low-information
##cues in elections. The Journal of Politics, 84(4), 2049-2063. https://doi.org/10.1086/719638
##(closed access; not read beyond the abstract)
##Replication data: Harvard Dataverse doi:10.7910/DVN/IZA24F, CC0 1.0. Files read: d_long.RData
##(data frame d_long, 2 rows per respondent), Codebook_Portmann_LowInformationCues.docx,
##Readme_Portmann_LowInformationCues.docx, 05_AnalysisSurveyExperiment2_Cues.R and
##04_AnalysisSurveyExperiment1_Cues.R (read as text, not run).
##Usage: Rscript portmann_2022.R <dir holding d_long.RData> <output dir>
##
##1,000 Swiss respondents (German-language Qualtrics survey; respondent canton recorded), ONE task of
##2 hypothetical male candidates. profile = the Qualtrics embedded-data slot (name_order Name1 = 1,
##Name2 = 2); choice_raw records the chosen slot and agrees with dv_choice on every row (stopifnot).
##  choice = dv_choice: which candidate the respondent prefers (codebook "Dummy whether respondent
##           prefers candidate"); exactly one per respondent, no opt-out. Wording not in the deposit.
##Attributes, German as stored in the Qualtrics fields (mis-encoded UTF-8 repaired): name (Stefan Moser
##= Swiss name, Marko Kovač = non-Swiss name; the two profiles always carry different names), profession,
##age, policy focus, number of children, and competence information (PolitOffExp/PolitOffExp2: a
##sentence such as "Er ist Regierungsrat." or "Er gilt weithin als intelligent und reflektiert.";
##the "Präsident seiner Wohngemeinde" sentence pipes in the respondent's own party answer, e.g.
##"Er ist SVP Präsident seiner Wohngemeinde.", and is kept as displayed).
##Experimental arm (trial_competence_arm = exp_arm): 1 = the block "Candidateexperimentpolitical
##experience" with competence information (the authors' tables: "Competence information: provided"),
##0 = the block without it, where attr_competence is "(not shown)" although the Qualtrics fields hold
##a drawn sentence.
##Every attribute is taken from the slot-specific raw field (Profession/Profession2, Age/Age2, ...).
##NOTE: the authors' recoded policy_f copies candidate 1's policy (Policy) onto candidate 2's row
##(745 of 1,000 candidate-2 rows differ from Policy2); profession_f, age_f, children_d match the raw
##fields. This table uses Policy2 for candidate 2, so a policy AMCE from it will differ from the paper's.
##Randomization restrictions and level probabilities are not documented; observed level shares are
##close to equal. Attribute order and presentation are not documented.
##Covariates: cov_gender ("Female"/"Male" -> female/male), cov_age_group (age band text), cov_educ3
##(the authors' low/medium/high recode; the raw education question is not in d_long), cov_ideology
##(IDEOL_1, 0-10 left-right self-placement as stored), cov_canton (respondent canton), cov_finished
##(Qualtrics Finished: 1 True, 0 False; 7 respondents did not finish the survey but answered the task).
##Dropped: ResponseId (Qualtrics; respondents re-keyed 1..1000 in ResponseId order), Party (respondent's
##party, free text answers), the authors' derived factors and dummies. No survey weight.
##NOT built from this deposit: Survey Experiment 1 (d_exp1.rdata), a 2 x 2 between-subjects experiment
##on one fixed candidate pair (Huber vs Schmid) whose vignette wording is not deposited, and the
##observational quasi-experiment (d3).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); suppressWarnings(load(file.path(raw, "d_long.RData"), envir = e))
s <- as.data.table(e$d_long[, setdiff(names(e$d_long), "d_long")])
stopifnot(nrow(s) == 2000, s[, .N, ResponseId][, all(N == 2)], all(s$name_order %in% c("Name1", "Name2")),
          s[, all(sort(name_order) == c("Name1", "Name2")), ResponseId]$V1)
fix <- function(x) { y <- iconv(x, "UTF-8", "latin1"); Encoding(y) <- "UTF-8"
  ok <- !is.na(y) & validUTF8(y) & y != x; x[ok] <- y[ok]; x <- gsub("  +", " ", trimws(x)); x }
s[, profile := match(name_order, c("Name1", "Name2"))]
s[, chosen_slot := sub("^\\$\\{e://Field/(Name[12])\\}$", "\\1", choice_raw)]
stopifnot(all(s$chosen_slot %in% c("Name1", "Name2")), all(s$dv_choice == (s$chosen_slot == s$name_order)),
          s[, sum(dv_choice), ResponseId][, all(V1 == 1)], s[, uniqueN(name), ResponseId][, all(V1 == 2)])
stopifnot(all((s$exp_arm == 1) == !is.na(s$FL_241_DO_Candidateexperimentpoliticalexperience)),
          all((s$exp_arm == 0) == !is.na(s$FL_241_DO_Candidateexperiment)))
pick <- function(a1, a2) fix(ifelse(s$profile == 1L, s[[a1]], s[[a2]]))
ids <- data.table(ResponseId = sort(unique(s$ResponseId)))[, id := .I]
s <- ids[s, on = "ResponseId"]
d <- data.table(id = s$id, task = 1L, profile = s$profile, choice = as.integer(s$dv_choice),
                trial_competence_arm = as.integer(s$exp_arm),
                attr_name = fix(s$name), attr_profession = pick("Profession", "Profession2"),
                attr_age = pick("Age", "Age2"), attr_policy = pick("Policy", "Policy2"),
                attr_children = pick("Children", "Children2"),
                attr_competence = pick("PolitOffExp", "PolitOffExp2"))
d[trial_competence_arm == 0L, attr_competence := "(not shown)"]
stopifnot(!anyNA(d), !any(d[, .SD, .SDcols = patterns("^attr_")] == ""),
          all(d$attr_profession == fix(as.character(s$profession_f))), all(d$attr_age == as.character(s$age_f)))
stopifnot(all(s$gender %in% c("Female", "Male")))
d[, cov_gender := tolower(s$gender)]
d[, cov_age_group := s$age]
d[, cov_educ3 := s$educ]
d[, cov_ideology := as.integer(s$IDEOL_1)]
d[, cov_canton := fix(s$CANTON)]
d[, cov_finished := as.integer(s$Finished == "True")]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "portmann_2022_candidate_cues.csv"))
