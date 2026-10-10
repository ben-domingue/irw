##Credit-claiming factorial vignette experiment (US, MTurk 2013) from
##Grimmer, J., Messing, S., & Westwood, S. J. (2017). Estimating heterogeneous treatment effects and
##the effects of heterogeneous treatments with ensemble methods. Political Analysis, 25(4), 413-434.
##https://doi.org/10.1017/pan.2017.15
##Replication data: Harvard Dataverse doi:10.7910/DVN/BQMLQW, CC0 1.0. Files read: Het_Experiment.RData
##(Dataverse original; data.frame `svdat`, loaded into its own environment); RepCode-1.R and ReadMe.docx
##read as text (not run) for the variable names, sample filter and level handling.
##Usage: Rscript grimmer_2017.R <dir holding Het_Experiment.RData> <output dir>
##
##1,074 respondents (online, 5 June 2013 onward per StartDate; the file has MTurk worker ids), each read ONE
##press release in which a legislator claims credit for spending (task = profile = 1). Five factors
##were randomized (the paper's "heterogeneous treatments", RepCode-1.R main-effects section):
##  attr_party       (cond.party):  "a Democrat" / "a Republican"
##  attr_along_with  (cond.alongWith): "alone" / "w/ Dem" / "w/ Rep" (the authors' labels for claiming
##                    credit alone or together with a Democrat / Republican; the displayed wording is not
##                    deposited)
##  attr_stage       (cond.stage): "requested" / "secured" / "will request"; the headline verb shown with
##                    it is cond.stageTitle (requests / secures / will request), one-to-one with the level
##  attr_money       (cond.money): "$20 million" / "$50 thousand"
##  attr_type        (cond.type): "for medical equipment at the local planned parenthood", "to beautify
##                    local parks", "to help build a state of the art gun range", "to purchase safety
##                    equipment for local firefighters", "to purchase safety equipment for local police",
##                    "to repave local roads" (each with a fixed quotation, cond.typeQuote)
##The party, money and type levels are the text inserted into the press release; the full vignette text
##is not deposited. 122 respondents were assigned to the control condition (contr == 1, no press release;
##the authors recode all five factors to "control") and are DROPPED: no profile was shown. 952 remain.
##All 1,074 passed the authors' attention filter (comments field matches "I pay attention",
##RepCode-1.R), so no one else is dropped; the free-text comments field itself is dropped.
##Outcomes (question wording and anchors not deposited):
##  rating         = approval, 1-5. The authors code approval < 3 as approving (approve_bi, RepCode-1.R),
##                   so LOWER = MORE APPROVAL; stored raw, not reversed.
##  rating_therm   = therm, 0-100 feeling thermometer toward the legislator (by its name; direction not
##                   documented).
##Other post-treatment items (fiscRespbl, bringMoneyEff, passLegEff, secReqMC manipulation check, likGetM,
##daysGetM) have no wording or anchors in the deposit and are dropped.
##Covariates kept as source codes, no codebook in the deposit (hence _code): cov_gender_code (gender 1/2),
##cov_race_code, cov_byear_code (byear: small integers 5-?, not calendar years), cov_ideo3_code (1-5),
##cov_voted_code, cov_pid3_code (1-4; the authors map 1 Dem, 2 Rep, 3/4 Ind/Other), cov_pidcloser_code,
##cov_educ_code, cov_inc_code. cov_duration_sec = EndDate - StartDate.
##PII in the source: IPAddress (all rows) and wid (MTurk worker id, 815 rows) are dropped, as are
##ResponseID, GUID and the Qualtrics bookkeeping columns; respondents re-keyed 1..1074 in file order
##(ids of dropped control respondents are skipped).
##Level weights: party, money near 50/50; along-with, stage near 1/3; type near 1/6 (observed).
##Spot check: an LPM of approving (rating < 3) on the five factors gives the gun range -0.54 against
##planned-parenthood equipment and "secured" +0.10 against "requested", the paper's two largest
##treatment contrasts in direction; the article's figure values were not compared.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "Het_Experiment.RData"), envir = e)
s <- as.data.table(e$svdat)
stopifnot(nrow(s) == 1074)
ok <- unique(c(agrep("I pay attention", s$comments, max.distance = .3), agrep("I PAY ATTENTION", s$comments, max.distance = .3)))
s[, rid := .I][, cov_attn := as.integer(rid %in% ok)]
stopifnot(all(s$cov_attn == 1))
s <- s[is.na(contr)]
stopifnot(nrow(s) == 952, all(s$treat == 1))
ch <- function(x) as.character(x)
d <- s[, .(id = rid, task = 1L, profile = 1L, rating = as.integer(approval), rating_therm = as.integer(therm),
           attr_party = ch(cond.party), attr_along_with = ch(cond.alongWith), attr_stage = ch(cond.stage),
           attr_money = ch(cond.money), attr_type = ch(cond.type),
           cov_gender_code = gender, cov_race_code = race, cov_byear_code = byear, cov_ideo3_code = ideo3,
           cov_voted_code = voted, cov_pid3_code = pid3, cov_pidcloser_code = pidCloser, cov_educ_code = educ,
           cov_inc_code = inc,
           cov_duration_sec = as.integer(difftime(as.POSIXct(EndDate, tz = "UTC"), as.POSIXct(StartDate, tz = "UTC"), units = "secs")))]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), !any(d[[v]] == "control"))
stopifnot(all(d$rating %in% 1:5), all(d$rating_therm >= 0 & d$rating_therm <= 100))
stopifnot(all(s[, ch(cond.stage)] == c(requests = "requested", secures = "secured", "will request" = "will request")[s$cond.stageTitle]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "grimmer_2017_credit_claiming.csv"))
