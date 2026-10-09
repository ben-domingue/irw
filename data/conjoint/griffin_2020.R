##Candidate-income factorial vignette (CCES 2014 module, the paper's Experiment 1) from
##Griffin, J. D., Newman, B., & Buhr, P. (2020). Class war in the voting booth: Bias against
##high-income congressional candidates. Legislative Studies Quarterly, 45(1), 131-145.
##https://doi.org/10.1111/lsq.12253
##Replication data: Harvard Dataverse doi:10.7910/DVN/U5B81D, CC0 1.0, no restricted files.
##File read: "experiment 1 CCES for replication.dta" (original format; Stata value labels give
##all level and answer text). Read as text only: "Replication archive readme.pdf",
##"Replication code experiment 1 CCES.do".
##Usage: Rscript griffin_2020.R <raw dir> <output dir>
##
##1,500 respondents to the authors' team module of the 2014 Cooperative Congressional Election
##Study (readme). Each read ONE description of a hypothetical congressional candidate (task 1,
##profile 1), presented as text. Two randomized factors, from the value labels of
##CUB3JG1_treat ("Vignette 1 - David Jones, $3 million" ... "Vignette 6 - Denise Jones"):
##  attr_name    David Jones / Denise Jones
##  attr_income  $3 million / $75,000 / (not shown)   (vignettes 5-6 state no income; the do-file
##               calls them "No income stated")
##The full vignette prose is not in the deposit (the article was not reachable), so the
##remaining text and the order of the parts are unknown. The other two experiments in the
##deposit are not built: Experiment 2 (MTurk) randomizes only income (one factor, not a
##conjoint); Experiment 3 (MTurk, income x party) is held because its displayed income amounts
##are unresolved (do-file and abstract: $75,000 / $3 million; its manipulation-check options,
##answered correctly by ~95%, are $73,000 / $3.2 million).
##Outcomes, all ratings of the one candidate, stored as coded in the .dta (value labels), NOT
##reversed (the authors' do-file reverses all but vote so that higher = more positive):
##  rating            CUB3JG1 "JG Vote for candidate": 1 I would definitely not vote for this
##                    candidate .. 4 I would definitely vote for this candidate (higher = more
##                    favourable)
##  rating_represent  CUB3JG2 "JG represent in office": 1 Very well .. 4 Very poorly (LOWER =
##                    more favourable)
##  rating_leadership CUB3JG3 "JG provide strong leadership", rating_cares CUB3JG4 "JG cares
##                    about people like you", rating_honest CUB3JG5 "JG honest",
##                    rating_intelligent CUB3JG6 "JG intelligent": 1 Extremely well .. 5 Not well
##                    at all (LOWER = more favourable)
##Question wording beyond these variable labels is not in the deposit (paraphrase).
##Skipped / not asked (value labels 8, 9; NA in the .dta) stay NA; respondents with no outcome
##at all are omitted.
##Covariates: cov_survey_weight = weight ("Team weights"; the do-file's svyset pweight);
##cov_perceived_party = CUB3JG7 "JG political party of the candidate" (Democrat / Republican,
##value-label text; the candidate's party is not among the randomized factors, so this is the
##respondent's inference/recall); cov_millionaires = CUB3JG8 "JG millionaires in Congress",
##value-label codes 1 It is a very significant problem, 2 somewhat significant problem, 3 small
##problem, 4 not a problem at all, but it is not a good thing either, 5 slightly good thing,
##6 somewhat good thing, 7 very good thing. The deposit has no respondent ID: id = row order.
##No other CCES variables are in the deposit (readme: purged of identifying information).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "experiment 1 CCES for replication.dta"))
tr <- as.integer(zap_labels(k$CUB3JG1_treat))
stopifnot(all(tr %in% 1:6))
lab <- names(attr(k$CUB3JG1_treat, "labels"))[match(1:6, attr(k$CUB3JG1_treat, "labels"))]
stopifnot(identical(lab, c("Vignette 1 - David Jones, $3 million", "Vignette 2 - Denise Jones, $3 million",
  "Vignette 3 - David Jones, $75,000", "Vignette 4 - Denise Jones, $75,000",
  "Vignette 5 - David Jones", "Vignette 6 - Denise Jones")))
num <- function(v) as.integer(zap_labels(k[[v]]))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
  rating = num("CUB3JG1"), rating_represent = num("CUB3JG2"), rating_leadership = num("CUB3JG3"),
  rating_cares = num("CUB3JG4"), rating_honest = num("CUB3JG5"), rating_intelligent = num("CUB3JG6"),
  attr_name = c("David Jones", "Denise Jones")[2L - tr %% 2L],
  attr_income = c("$3 million", "$75,000", "(not shown)")[(tr + 1L) %/% 2L],
  cov_survey_weight = as.numeric(k$weight),
  cov_perceived_party = c("Democrat", "Republican")[num("CUB3JG7")],
  cov_millionaires = num("CUB3JG8"))
stopifnot(all(d$rating %in% c(1:4, NA)), all(d$rating_represent %in% c(1:4, NA)),
          all(unlist(d[, .(rating_leadership, rating_cares, rating_honest, rating_intelligent)]) %in% c(1:5, NA)),
          all(d$cov_millionaires %in% c(1:7, NA)))
oc <- grep("^rating", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..oc])) > 0]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "griffin_2020_candidate_income.csv"))
