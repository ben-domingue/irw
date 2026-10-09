##Accountability-forum prioritization conjoint (UK and Dutch civil servants) from
##Aleksovska, M., Schillemans, T., & Grimmelikhuijsen, S. (2022). Management of multiple
##accountabilities through setting priorities: Evidence from a cross-national conjoint experiment.
##Public Administration Review, 82(1), 132-146 (online 2021). https://doi.org/10.1111/puar.13357
##Replication data: DANS SSH Data Station doi:10.17026/dans-xt3-k5qc, CC BY-NC 4.0, no restricted
##files. Files read: conjointcomplete.tab, Codebook.pdf; "replication code conjoint.R" read as text.
##Level display text, scenario and question wording from the article (open access, Utrecht
##repository copy): Table 1 "Operationalization" column and Appendix A.
##Usage: Rscript aleksovska_2021.R <raw dir> <output dir>
##
##Samples: 600 UK civil servants (Prolific, July 2019) and 603 Dutch civil servants of four executive
##agencies (BD-TL, CAK, DUO, UWV; October 2019). ONE TABLE with cov_country: the authors pool the two
##samples for their main analysis (Figure 1, N = 4,637) and compare them by country.
##Scenario (Appendix A): "Two stakeholders have communicated demands to your organization. You have
##been asked to perform tasks to respond to both demands, however, you can only do one at a time, so
##you must decide which one to perform first. Which stakeholder's demand would you prioritize?"
##Up to 4 tasks (Competition) x 2 stakeholder profiles (Option = Stakeholder 1/2, recorded).
##choice = Chosen; forced choice, no opt-out.
##Attributes: the data hold the authors' short labels; stored is the text shown (article Table 1):
##  attr_expertise (Stakeholder expertise): High expertise = "Fully understands the type of work your
##    organization performs"; Low expertise = "Has very little knowledge about the type of work your
##    organization performs"
##  attr_consequence (Possible consequence for non-compliance with demand): Financial = "Financial
##    damage to your organization (fine or budget reduction)"; Reputational = "Bad press, damage to
##    your organization's reputation"; Relational = "Worsened relationship of your organization with
##    the stakeholder"
##  attr_consequence_likelihood (Likelihood of imposing consequence for non-compliance with demand):
##    High = "Almost certainly"; Equal = "50-50 chance"; Low = "Very unlikely"
##  attr_previous_experience (Previous experience with stakeholder): Positive = "No struggles at all
##    with this stakeholder in the past, good collaboration"; Negative = "Many struggles with this
##    stakeholder in the past"
##This is the English instrument. The Dutch sample answered a Dutch questionnaire (the article's
##appendix reports their education answers in Dutch categories); its Dutch level text is not deposited.
##Restrictions: "randomly generated from the list of available levels"; tasks in which the two
##profiles were identical were removed by the authors before deposit (article note 2), so task
##numbers have gaps for some respondents. 58 tasks with no recorded choice (116 rows) are dropped
##here; the remaining 4,637 tasks (UK 2,345, NL 2,292) match the article exactly; 1,201 respondents
##(2 Dutch respondents have no answered task).
##trial_choice_time_sec = Choice_time (seconds to make that choice). Covariates: cov_country (UK/NL),
##cov_organization (various = UK sample; BD-TL, CAK, DUO, UWV), cov_recognize ("Do you recognize the
##situation provided in this study in your work?", codebook text; NA = no answer). The deposit has
##no other personal characteristics (removed by the authors). ResponseId (Qualtrics) re-keyed to
##integers. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjointcomplete.tab"))
s <- s[!is.na(Chosen)]
s[, id := match(ResponseId, sort(unique(ResponseId)))]
mp <- function(x, from, to) { stopifnot(all(x %in% from)); to[match(x, from)] }
d <- s[, .(id, task = as.integer(Competition), profile = as.integer(Option), choice = as.integer(Chosen))]
d[, attr_expertise := mp(s$Expertise, c("High expertise", "Low expertise"),
   c("Fully understands the type of work your organization performs",
     "Has very little knowledge about the type of work your organization performs"))]
d[, attr_consequence := mp(s$Consequence, c("Financial", "Reputational", "Relational"),
   c("Financial damage to your organization (fine or budget reduction)",
     "Bad press, damage to your organization's reputation",
     "Worsened relationship of your organization with the stakeholder"))]
d[, attr_consequence_likelihood := mp(s$Consequence_likelihood, c("High likelihood", "Equal likelihood", "Low likelihood"),
   c("Almost certainly", "50-50 chance", "Very unlikely"))]
d[, attr_previous_experience := mp(s$Previous_experience, c("Positive experience", "Negative experience"),
   c("No struggles at all with this stakeholder in the past, good collaboration",
     "Many struggles with this stakeholder in the past"))]
d[, trial_choice_time_sec := as.numeric(s$Choice_time)]
d[, cov_country := s$Country]
d[, cov_organization := s$Organization]
d[, cov_recognize := mp(s$Recognize, c(1:5, NA), c("I deal with similar situations very often",
   "I sometimes deal with similar situations",
   "I recognize these situations in the work of my colleagues, but not in my own work",
   "Such situations are very rare in my workplace",
   "I have never heard of or encountered such a situation before", NA))]
stopifnot(d[, .(n = .N, ch = sum(choice)), by = .(id, task)][, all(n == 2 & ch == 1)],
          d[, uniqueN(task), by = id][, all(V1 <= 4)], nrow(d) == 2 * 4637)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "aleksovska_2021_accountability_priority.csv"))
