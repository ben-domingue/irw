##Speech-style vignette experiment (gender bias in perceptions of political arguments, UK, September 2021) from
##Hargrave, L. (2023). A double standard? Gender bias in voters' perceptions of political arguments.
##British Journal of Political Science. https://doi.org/10.1017/S0007123422000515
##Replication data: Harvard Dataverse doi:10.7910/DVN/LZ4NKW, CC0 1.0. File read: data/yougov_raw_results (the .tab export,
##saved as yougov_raw.tab). Documentation read as text: README.txt, manuscript.Rmd (Research Design, outcome wording), 02_data_prep.R
##(the authors' recodes) and figure_1_example_prompt.jpg (screenshot of one prompt). The Prolific pre-test (pretesting_raw) is a
##different survey and is not used.
##Usage: Rscript hargrave_2023.R <dir holding yougov_raw.tab> <output dir>
##
##1,676 YouGov UK online-panel respondents (the paper's N = 5,028 observations); each read three short speech excerpts by a fictional
##MP (task = 1..3 in order shown, one profile per task). The manuscript says four attributes were randomized per task:
##style (emotion / aggression / evidence), treatment status of the style, policy area (transport / housing / health) and MP gender
##(by name; surnames Craddock / Jones / Richards rotate too). Stored as:
##  attr_style            Emotion / Aggression / Evidence (qstyle 1/2/3)
##  attr_style_version    the style's treatment status, with the authors' labels from 02_data_prep.R: Emotion: Non-emotional
##                        (control) / Emotional (treatment); Aggression: Non-aggressive / Aggressive; Evidence: Statistics
##                        (control) / Anecdote (treatment). qstyle_prevalence 2 = control, 4 = treatment for emotion and
##                        aggression; 3 = statistics, 1 = anecdote for evidence.
##  attr_policy_area      Transport / Housing / Health (qpolicy 1/2/3)
##  attr_mp_first_name    name1..3 (Adam, Jack, Peter; Beth, Charlotte, Lucy)
##  attr_mp_surname       surname1..3 (Craddock, Jones, Richards)
##The speech texts themselves are in the paper's appendix (not in the deposit); the stored levels are the design factors, and
##trial_speech_number (qspeech) identifies which of the written speeches was shown.
##Restrictions (manuscript): styles and policies were drawn without replacement across a respondent's three tasks (no style or policy
##twice); status and name with replacement.
##Outcomes (rating, 1 strongly disagree .. 5 strongly agree, 6 'Don't know' set to NA as the authors do; each asked 15 s after the
##speech): rating_likeable ('agree or disagree that the MP seems likeable', Q3), rating_competent ('...seems competent', Q2),
##and one style perception asked only for the style shown: rating_perceived_emotional (Q1a), rating_perceived_aggressive (Q1b),
##rating_perceived_evidence (Q1c) ('agree or disagree that the argument made by the MP is emotional / aggressive / evidence-based').
##Direction: higher = more agreement. Likert endpoints follow the manuscript and the prompt screenshot; the question-number to outcome
##mapping is the authors' own (02_data_prep.R). No choice or opt-out.
##Covariates: cov_gender (profile_gender: 1 = Man = male, 2 = Woman = female, per 02_data_prep.R), cov_age (years, as recorded),
##cov_survey_weight (Weight). Dropped: start/end times, the survey platform's counter and eligibility columns, region, social grade,
##2019 and EU-referendum vote, political attention, education, left-right placement. Respondent ID is the platform's case number (re-keyed).
##Count check: 1,676 respondents x 3 = 5,028 observations, as in the manuscript (nrow(style_data) / 3). Tasks where all five answers are missing
##(don't know or not asked) are omitted: 4,808 rows, 1,628 respondents.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "yougov_raw.tab"), encoding = "UTF-8", showProgress = FALSE)
nz <- function(x) { x <- suppressWarnings(as.integer(trimws(as.character(x)))); x }
dk <- function(x) { x <- nz(x); x[x == 6L] <- NA; x }
rows <- lapply(1:3, function(t) {
  g <- function(v) k[[paste0(v, t)]]
  q <- function(v) dk(k[[paste0("task", t, "_", v)]])
  style <- nz(g("qstyle")); prev <- nz(g("qstyle_prevalence"))
  ver <- ifelse(style == 1 & prev == 2, "Non-emotional", ifelse(style == 1 & prev == 4, "Emotional",
         ifelse(style == 2 & prev == 2, "Non-aggressive", ifelse(style == 2 & prev == 4, "Aggressive",
         ifelse(style == 3 & prev == 3, "Statistics", ifelse(style == 3 & prev == 1, "Anecdote", NA))))))
  data.table(id = seq_len(nrow(k)), task = t, profile = 1L,
    rating_likeable = q("Q3"), rating_competent = q("Q2"), rating_perceived_emotional = q("Q1a"),
    rating_perceived_aggressive = q("Q1b"), rating_perceived_evidence = q("Q1c"),
    attr_style = c("Emotion", "Aggression", "Evidence")[style], attr_style_version = ver,
    attr_policy_area = c("Transport", "Housing", "Health")[nz(g("qpolicy"))],
    attr_mp_first_name = g("name"), attr_mp_surname = g("surname"),
    trial_speech_number = nz(g("qspeech")), cov_gender = c("male", "female")[nz(k$profile_gender)],
    cov_age = as.integer(k$age), cov_survey_weight = k$Weight)
})
d <- rbindlist(rows)
stopifnot(!anyNA(d[, .(attr_style, attr_style_version, attr_policy_area, attr_mp_first_name, attr_mp_surname)]))
d <- d[!(is.na(rating_likeable) & is.na(rating_competent) & is.na(rating_perceived_emotional) &
         is.na(rating_perceived_aggressive) & is.na(rating_perceived_evidence))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hargrave_2023_speech_style.csv"))
