##Candidate choice and attitude prediction, paired conjoints in the Norwegian Citizen Panel, from
##Arnesen, S., Duell, D., & Johannesson, M. P. (2019). Do citizens make inferences from political
##candidate characteristics when aiming for substantive representation? Electoral Studies, 57, 46-60.
##https://doi.org/10.1016/j.electstud.2018.10.005 (article CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/AESELE, CC0 1.0. Files read:
##data-experiment-one.csv (6,624 rows), data-experiment-two.csv (6,370 rows). Also read as
##documentation: README.md, raw/vars-exp-represent.xlsx, raw/vars-exp-predict.xlsx,
##raw/labels-exp-*.xlsx, raw/vars-resp.xlsx, raw/docs/"Codebook NCP w01-07 - EN.pdf".
##Usage: Rscript arnesen_2019_representation.R <raw dir> <output dir>
##  (<raw dir> holds data-experiment-one.csv and data-experiment-two.csv)
##
##NOTE on the deposit's DOI. candidates.csv recorded this deposit against doi 10.1016/j.electstud.
##2018.11.003, which is a different Electoral Studies article (Carl, Richards & Heath on Brexit
##knowledge). The DOI above is the one Crossref gives for this title and author list.
##
##LICENCE NOTE. The README states that the raw Norwegian Citizen Panel (NCP) file cannot be shared
##openly under data-protection law, so the authors deposited PREPARED analysis files instead. The
##CC0 1.0 licence and these tables cover those prepared files; the raw panel file is not in the
##deposit and is not used here. Researchers obtain the raw NCP from Sikt (formerly NSD).
##
##Two tables, one per experiment (different attribute sets, different outcomes, different waves):
##  arnesen_2019_candidate_choice      Experiment I, NCP wave 6
##  arnesen_2019_attitude_prediction   Experiment II, NCP wave 7
##
##EXPERIMENT I - arnesen_2019_candidate_choice (1,139 respondents, 6,624 rows)
##Design: three paired candidate-choice tasks per respondent, two hypothetical members of parliament
##per task, shown in a randomised order. Ten attributes: seven social characteristics (age, gender,
##region, relationship, education, religion, work) and three issue positions, each on the same 7-point
##agree/disagree scale. The issue statements, from raw/vars-exp-represent.xlsx:
##  attr_opinion_inequality = "State should reduce income inequality"
##  attr_opinion_refugees   = "Refugees should have the same right to social assistance"
##  attr_opinion_emissions  = "Most of the emission reductions should be done abroad"
##The information condition is WITHIN respondent, not between: every respondent did all three tasks,
##one per condition (codebook variables r6pad8a/b/c, "the order of which R6PAD8A-C is asked is
##randomized"). So trial_information carries the condition and `task` carries the display order:
##  descriptive only  (r6pad8a) - the three issue positions are not shown
##  substantive only  (r6pad8b) - the seven social characteristics are not shown
##  both              (r6pad8c) - everything shown
##The deposit's own label for the first condition reads "Only descriptic information" (sic); the values
##written here are normalised to "descriptive only" / "substantive only" / "both", which is a trial_
##column of IRW's own making rather than displayed level text.
##Hidden attributes are the reserved `(not shown)`. This is exactly structural: every one of the 2,204
##NA social-characteristic cells falls in the substantive-only condition and every one of the 2,212 NA
##issue-position cells falls in the descriptive-only condition, with no residual missingness in any
##attribute column (checked).
##Outcome: choice = post. Codebook r6pad8a, literal question: "Below we are presenting you with two
##hypothetical members of parliament with differing characteristics. Let us say that you have to choose
##one of these to represent you in parliament. Please read the description of each representative
##carefully. Then, please indicate which representative you would prefer to represent you."
##Forced choice, no opt-out; exactly one of the two profiles chosen in all 3,312 tasks (checked).
##task = exp_order (1-3, "When the decision where asked" per raw/labels-vars.xlsx), recorded.
##profile = cand_candidate (1/2), recorded.
##Dropped as derived: exp_decision (the chosen candidate's number; post is 1 exactly when
##cand_candidate == exp_decision, 0 mismatches in 6,624 rows), exp_version and exp_version_2 (the
##condition, kept as trial_information), and the nine cand_matched_* columns (same/different relative
##to the respondent, built from respondent attributes).
##Respondents with fewer than three tasks are kept as they are: 1,059 did all three, 55 did two and 25
##did one (codebook value 97 = "No answer"), and each surviving task still has exactly one chosen
##profile. Respondent N is not stated in the paper's main text.
##
##EXPERIMENT II - arnesen_2019_attitude_prediction (1,077 respondents, 6,370 rows)
##Design: three paired tasks per respondent, two hypothetical people per task, seven social
##characteristics (no issue positions, nothing hidden: zero NA attribute cells). Respondents predict
##which of the two would agree with a stated attitude, so the attitude is a task-level detail rather
##than a profile attribute. trial_attitude carries the statement; trial_profile_kind carries whether
##the pair was described as ordinary persons or as politicians (codebook r7pad6a vs r7pad6b), which is
##BETWEEN respondents (constant within all 1,077: checked).
##Outcome: choice = post. Codebook r7pad6a, pre-question: "People have differing political opinions,
##and sometimes these opinions are related to their background. Below we have made up two imagined
##persons of different background. We wish to know which of these you think will be mostly in agreement
##with the statement below." Literal question: "Please choose the person you believe would be most in
##agreement with the following statement: <statement>". This is a pick AMONG the two profiles, so it is
##a `choice` and not a `rating`; exactly one chosen in all 3,185 tasks (checked). No opt-out.
##task = exp_attitude (1-3). The display order is NOT recorded in this experiment (unlike Experiment I,
##which has exp_order), so task_source is inferred and task indexes the attitude, not the order shown.
##Dropped as derived: exp_decision, exp_attitude (kept as trial_attitude's text),
##exp_attitude_label_2 (the same statements with line breaks for plotting), exp_type (kept as
##trial_profile_kind).
##
##COVARIATES (both tables). The prepared files ship respondent variables as NCP numeric codes; the
##mappings below are read from the deposit's own "Codebook NCP w01-07 - EN.pdf" and the raw variable
##names in raw/vars-resp.xlsx, so no reserved cov_ name holds a code.
##  cov_age_group  <- resp_age (r6P5_1/r7P5_1, "Age (7 categories)"): 18-25, 26-35, 36-45, 46-55,
##                    56-65, 66-75, "75 and above"
##  cov_gender     <- resp_gender (r6P1/r7P1): 1 = male, 2 = female, mapped to IRW's female/male
##  cov_education  <- resp_education (r6P4_1/r7P4_1), the codebook's three categories VERBATIM,
##                    including its own typo: "No education/elementary school",
##                    "Upper secondary eduction" (sic), "University/university college"
##  cov_region     <- resp_region (r6P2/r7P2): Oslo/Akershus, Ostlandet, Sorlandet, Vestlandet,
##                    Trondelag, Nord-Norge (codebook spellings, with Norwegian letters as deposited)
##  cov_religion   <- resp_religion, already text in the deposit ("Christianity", "None", "Other")
##  cov_vote_intent<- resp_would_vote_party (r6k204/r7k204), codebook labels. This is VOTE CHOICE
##                    ("Which party would you vote for if there were a parliamentary election
##                    tomorrow?"), so it is deliberately NOT cov_party_id, which the standard reserves
##                    for party identification. Levels include "Would not vote", "Not entitled to
##                    vote" and "Other:" as the codebook writes them.
##resp_county (19 codes) and resp_city (area-type size, 5 codes) are NOT carried: county or
##area type alongside age band, religion and gender is a re-identification surface these tables have no
##use for, and region is the geography the paper analyses. The remaining resp_* columns are the panel's
##other attitude batteries, dropped as not covariates of these experiments.
##Respondent id: responseid is the real NCP respondent id and is kept, so it links the same people
##across these two tables and to arnesen_2019_referendum_mandate (864 respondents in common with that
##table). resp_wave is constant per table (6 for Experiment I, 7 for Experiment II) and is recorded
##here rather than as a column.
##Note on the two region vocabularies: the CANDIDATE's region is the English set the authors wrote for
##the profiles (Oslo, Eastern/Southern/Western/Central/Northern Norway), while the RESPONDENT's region
##is the panel's own six regions under the codebook's Norwegian names (Oslo/Akershus, Ostlandet,
##Sorlandet, Vestlandet, Trondelag, Nord-Norge). They describe the same geography in two vocabularies
##and are not joinable as strings; both are kept as their source gives them.
##Language: the NCP is fielded in Norwegian; the deposit's prepared files carry the authors' ENGLISH
##level labels, translated from the Norwegian via raw/labels-exp-*.xlsx (e.g. "22 ar" -> "22 years").
##So display_language = no, label_language = en.
##Restrictions: the codebook says the profile contents are "randomly determined"; no restriction on
##level combinations is documented. Attribute display order within a profile is not recorded.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]

AGE <- c("1" = "18-25", "2" = "26-35", "3" = "36-45", "4" = "46-55", "5" = "56-65",
         "6" = "66-75", "7" = "75 and above")
GENDER <- c("1" = "male", "2" = "female")
EDU <- c("1" = "No education/elementary school", "2" = "Upper secondary eduction",
         "3" = "University/university college")
REGION <- c("1" = "Oslo/Akershus", "2" = "Østlandet", "3" = "Sørlandet",
            "4" = "Vestlandet", "5" = "Trøndelag", "6" = "Nord-Norge")
PARTY <- c("1" = "The Christian Democrats", "2" = "The Progress party",
           "3" = "The Conservative Party of Norway", "4" = "The Liberal Party",
           "5" = "The Socialist Left Party", "6" = "The Centre Party", "7" = "The Green Party",
           "8" = "The Labour Party", "9" = "The Red Party", "10" = "Would not vote",
           "11" = "Not entitled to vote", "12" = "Other:")
map <- function(x, tab) {
  v <- unname(tab[as.character(x)])
  stopifnot(all(is.na(x) | !is.na(v)))  # every observed code is in the codebook
  v
}
covs <- function(x) list(
  cov_age_group = map(x$resp_age, AGE), cov_gender = map(x$resp_gender, GENDER),
  cov_education = map(x$resp_education, EDU), cov_region = map(x$resp_region, REGION),
  cov_religion = ifelse(x$resp_religion == "None", "None", x$resp_religion),
  cov_vote_intent = map(x$resp_would_vote_party, PARTY))
ns <- function(x) ifelse(is.na(x), "(not shown)", as.character(x))

## Experiment I -------------------------------------------------------------
d1 <- fread(file.path(raw, "data-experiment-one.csv"), encoding = "UTF-8", na.strings = c("NA", ""))
stopifnot(nrow(d1) == 6624, uniqueN(d1$responseid) == 1139, uniqueN(d1$resp_wave) == 1)
stopifnot(all((d1$cand_candidate == d1$exp_decision) == (d1$post == 1)))
##Every hidden cell is the condition's own block, and nothing else is missing.
soc <- c("cand_age", "cand_gender", "cand_region", "cand_relationship", "cand_education",
         "cand_religion", "cand_work")
opi <- c("cand_opinion_1", "cand_opinion_2", "cand_opinion_3")
stopifnot(all(d1[, lapply(.SD, function(z) all(is.na(z) == (exp_version == 2))), .SDcols = soc]),
          all(d1[, lapply(.SD, function(z) all(is.na(z) == (exp_version == 1))), .SDcols = opi]))
t1 <- d1[, c(list(
  id = as.integer(responseid), task = as.integer(exp_order), profile = as.integer(cand_candidate),
  choice = as.integer(post),
  attr_age = ns(cand_age), attr_gender = ns(cand_gender), attr_region = ns(cand_region),
  attr_relationship = ns(cand_relationship), attr_education = ns(cand_education),
  attr_religion = ns(cand_religion), attr_work = ns(cand_work),
  attr_opinion_inequality = ns(cand_opinion_1), attr_opinion_refugees = ns(cand_opinion_2),
  attr_opinion_emissions = ns(cand_opinion_3),
  trial_information = c("1" = "descriptive only", "2" = "substantive only",
                        "3" = "both")[as.character(exp_version)]), covs(.SD))]

## Experiment II ------------------------------------------------------------
d2 <- fread(file.path(raw, "data-experiment-two.csv"), encoding = "UTF-8", na.strings = c("NA", ""))
stopifnot(nrow(d2) == 6370, uniqueN(d2$responseid) == 1077, uniqueN(d2$resp_wave) == 1)
stopifnot(all((d2$cand_candidate == d2$exp_decision) == (d2$post == 1)),
          all(d2[, uniqueN(exp_type), responseid]$V1 == 1))
t2 <- d2[, c(list(
  id = as.integer(responseid), task = as.integer(exp_attitude),
  profile = as.integer(cand_candidate), choice = as.integer(post),
  attr_age = cand_age, attr_gender = cand_gender, attr_region = cand_region,
  attr_relationship = cand_relationship, attr_education = cand_education,
  attr_religion = cand_religion, attr_work = cand_work,
  trial_attitude = exp_attitude_label, trial_profile_kind = tolower(exp_type)), covs(.SD))]

for (p in list(list(t1, "arnesen_2019_candidate_choice"), list(t2, "arnesen_2019_attitude_prediction"))) {
  t <- as.data.table(p[[1]])
  ac <- grep("^attr_", names(t), value = TRUE)
  stopifnot(!anyNA(t[, ..ac]), !any(t[, ..ac] == ""), !anyNA(t$choice),
            all(t[, .(s = sum(choice), n = .N), .(id, task)][, s == 1 & n == 2]))
  setorder(t, id, task, profile)
  fwrite(t, file.path(out, paste0(p[[2]], ".csv")))
}
