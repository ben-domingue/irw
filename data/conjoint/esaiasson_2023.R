##Good-loser decision vignette (Norway, Study 3): issue x outcome x winning margin x winner's gloating x loser's
##message, from
##Esaiasson, P., Arnesen, S., & Werner, H. (2023). How to be gracious about political loss: The importance of good loser
##messages in policy controversies. Comparative Political Studies, 56(5), 599-624. https://doi.org/10.1177/00104140221109433
##Replication data: Harvard Dataverse doi:10.7910/DVN/AZGPQO, CC0 1.0 (no terms, no restricted files; the Norwegian
##Citizen Panel extract question was ruled open by Ben 2026-10-21). Files read: Goodloser-exp3.rds (datafile 6276064,
##2,819 rows, SPSS value labels kept by haven), Rmarkdown-article-and-appendix.Rmd (6360608, read as text: Study III
##section, "Vignette treatment dimensions and values" table and recodes). Studies 1 and 2 (one randomized factor each,
##favourability derived from the respondent's own opinion) are not conjoints and are not built.
##Usage: Rscript esaiasson_2023.R <dir holding Goodloser-exp3.rds> <output dir>
##
##Design: Norwegian Citizen Panel wave 13 (fall 2018), one text vignette per respondent (task = profile = 1, id = row
##order; the panel responseid is dropped). Vignette (Rmd table footnote, English rendering of the Norwegian text):
##"Imagine that your municipality must decide on {Issue} The decision will be taken by the municipal council ... In the
##end, the politicians will vote on the issue. {Outcome} {Winning margin} {Winner gloating} {Messenger and message}".
##Attribute TEXT (not coded): from the deposit's value labels (truncated at 120 characters) completed with the authors'
##table in the Rmd, which gives the full English wording; code-to-text mapping from the value labels and the Rmd recodes
##(treat_issue, treat_outcome, treat_winningmargin, treat_winnergloat, treat_message/treat_messenger):
## attr_issue 1 begging ban / 2 diesel-car toll (full sentence as in the Rmd table); attr_outcome 1 "The Yes side won
## the vote" / 2 "The No side won the vote"; attr_margin 1 = "." in the labels and "Not shown" in the Rmd ->
## "(not shown)", 2 "with a slight majority.", 3 "with a large majority."; attr_winner_gloating 1 [BLANK] ->
## "(not shown)", 2 the gloating sentence; attr_loser_message 1 [BLANK] -> "(not shown)", 2-4 party leader (labels
## begin "The leader of one of the parties..."; Rmd treat_messenger 3:4 = "Political leader"), 5-7 local newspaper
## (labels begin "The local newspaper..."; Rmd 6:7 = "Local newspaper"); 2/5 = no good-loser message, 3/6 = specific
## ("fair fight") message, 4/7 = generic ("living in a democracy") message (Rmd treat_message).
##Outcomes (three questions, each on one of two randomized answer formats, r13pad6_ran: 1 = worded options
##(r13pad6a/7a/8a), 2 = numbered 1-5 scale with end labels (6b/7b/8b); trial_scale_format records it; stored raw,
##NOT reversed, 1 = most positive): rating_fairness "How fair was the way the decision was made" (1 Very fair /
##1 Most fair .. 5 Not at all fair / 5 Not fair); rating_reasonable "How reasonable was the decision" (1 Very / Most
##reasonable .. 5 Not reasonable at all / Not reasonable); rating_accept "How willing to accept the decision" (1 Very /
##Most willing .. 5 Not at all willing / Not willing). Wording from the deposit's variable labels (English rendering;
##the Rmd tables give "What do you think about the way the decision was made?" and "When you think about the actual
##outcome of the decision, how willing are you to accept the decision?"). The authors reverse all three (5 = most).
##97/98 (not answered / not asked) -> NA. 26 respondents answered none of the three: omitted (2,793 kept).
##No exclusions: the preregistered speeding rule (time on the outcome page < 0.25 x median) was not applied by the
##authors either (Rmd 3010); reproduce it with cov_outcome_page_sec.
##Covariates: cov_gender (1 Male, 2 Female per value labels), cov_age_group (year-of-birth band text: "1959 or
##earlier", "1960-1989", "1990 or later"; the panel stores birth year only in bands), cov_polint (1 Very interested ..
##5 Not interested at all, as stored; 97 -> NA), cov_opinion_begging / cov_opinion_toll (answer text, pre-treatment),
##cov_importance_begging / cov_importance_toll (1 Very important .. 5, as stored), cov_outcome_page_sec (seconds on the
##outcome page, NCP time tracker). The authors' "outcome favourable to the respondent" is derived (issue x outcome x
##own opinion) and not stored. No survey weight in the extract.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(readRDS(file.path(raw, "Goodloser-exp3.rds")))
stopifnot(nrow(k) == 2819L, !anyDuplicated(k$responseid))
lab <- function(v) attr(k[[v]], "labels")
stopifnot(startsWith(names(lab("issue"))[1], "in the future, begging"), startsWith(names(lab("issue"))[2], "in the future, diesel"),
          names(lab("outcome")) == c("The Yes side won the vote", "The No side won the vote"),
          names(lab("margin"))[1] == ".", names(lab("winner"))[1] == "[BLANK]", names(lab("messenger"))[1] == "[BLANK]",
          all(startsWith(names(lab("messenger"))[2:4], "The leader of one of the parties")),
          all(startsWith(names(lab("messenger"))[5:7], "The local newspaper")))
txt_issue <- c("in the future, begging on the streets will be banned or permitted in the municipality. This is a controversial decision. Some residents are strong in favour of a ban (the “Yes” side), while other residents are strongly against a ban (the “No” side). Some parties propose a ban on begging.",
               "in the future, diesel cars will pay increased tolls. This is a controversial decision. Some residents are strongly in favour of such an increase (the “Yes” side), while others are strongly against an increase (the “No” side). Some parties propose such an increase in tolls for diesel cars.")
txt_margin <- c("(not shown)", "with a slight majority.", "with a large majority.")
txt_winner <- c("(not shown)", "Following the decision, a politician on the winning side says that it was a good decision and that common sense prevailed.")
pol <- "The leader of one of the parties that was against the decision says that they are disappointed and that the decision was wrong"
np <- "The local newspaper – which was against the decision – writes in an editorial that they are disappointed and that the decision was wrong"
spec <- ", but that it was a fair fight where both sides had the opportunity to argue in favour of their views."
gen <- ", but that is what living in a democracy is all about. Sometimes you win, sometimes you lose."
txt_msg <- c("(not shown)", paste0(pol, "."), paste0(pol, spec), paste0(pol, gen), paste0(np, "."), paste0(np, spec), paste0(np, gen))
# the deposit's truncated labels must be prefixes of the full text used (whitespace-normalised)
nz <- function(x) gsub("\\s+", " ", trimws(x))
stopifnot(all(startsWith(nz(txt_msg[2:7]), nz(names(lab("messenger"))[2:7]))),
          all(startsWith(nz(txt_issue), nz(names(lab("issue"))))),
          startsWith(txt_winner[2], nz(names(lab("winner"))[2])))
num <- function(x) { x <- as.numeric(zap_labels(x)); x[x %in% c(97, 98)] <- NA; x }
fa <- num(k$fairness_a); fb <- num(k$fairness_b); ra <- num(k$reasonable_a); rb <- num(k$reasonable_b)
aa <- num(k$accept_a); ab <- num(k$accept_b); fmt <- as.integer(k$r13pad6_ran)
stopifnot(all(is.na(fa[fmt == 2]) & is.na(ra[fmt == 2]) & is.na(aa[fmt == 2])), all(is.na(fb[fmt == 1]) & is.na(rb[fmt == 1]) & is.na(ab[fmt == 1])))
lbl <- function(v) { x <- as.numeric(zap_labels(k[[v]])); l <- lab(v); out <- names(l)[match(x, l)]; out[x %in% c(97, 98)] <- NA; out }
d <- data.table(task = 1L, profile = 1L,
  rating_fairness = as.integer(fcoalesce(fa, fb)), rating_reasonable = as.integer(fcoalesce(ra, rb)), rating_accept = as.integer(fcoalesce(aa, ab)),
  attr_issue = txt_issue[as.integer(k$issue)], attr_outcome = names(lab("outcome"))[as.integer(k$outcome)],
  attr_margin = txt_margin[as.integer(k$margin)], attr_winner_gloating = txt_winner[as.integer(k$winner)],
  attr_loser_message = txt_msg[as.integer(k$messenger)],
  trial_scale_format = c("worded", "numbered")[fmt],
  cov_gender = c("male", "female")[as.integer(k$gender)], cov_age_group = lbl("age"),
  cov_polint = num(k$polint), cov_opinion_begging = lbl("opinion_begging"), cov_opinion_toll = lbl("opinion_toll"),
  cov_importance_begging = num(k$importance_begging), cov_importance_toll = num(k$importance_toll),
  cov_outcome_page_sec = as.numeric(k$time))
stopifnot(!anyNA(d[, .(attr_issue, attr_outcome, attr_margin, attr_winner_gloating, attr_loser_message, trial_scale_format, cov_gender)]),
          all(d$cov_age_group %in% c("1959 or earlier", "1960-1989", "1990 or later")))
d <- d[!(is.na(rating_fairness) & is.na(rating_reasonable) & is.na(rating_accept))]
d[, id := seq_len(.N)]; setcolorder(d, "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "esaiasson_2023_good_loser_no.csv"))
cat(nrow(d), "\n"); print(d[, .N, attr_loser_message][order(attr_loser_message), .(substr(attr_loser_message, 1, 50), N)])
