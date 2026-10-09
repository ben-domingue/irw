##Candidate-endorsement conjoint (Finland) from
##Christensen, H. S., Järvi, T., Mattila, M., & von Schoultz, Å. (2021). How voters choose one
##out of many: A conjoint analysis of the effects of endorsements on candidate choice. Political
##Research Exchange, 3(1). https://doi.org/10.1080/2474736X.2021.1892456
##Replication data: OSF node rdxct ("Conjoint candidate choice"), doi:10.17605/OSF.IO/RDXCT,
##node licence CC BY 4.0, no other terms. File read: "Candidate endorsement.dta" (OSF gkde9,
##saved as endorsement.dta). The article could not be retrieved (publisher 403, repository
##behind a bot check): design facts are from its abstract (choice-based conjoint, Finnish survey,
##n = 1021) and the .dta value labels; the same team's EP conjoint (christensen_2020.R, OSF
##w6jkq) uses the same NO INFO / NOT SHOWN layout.
##Usage: Rscript christensen_2021.R <dir holding endorsement.dta> <output dir>
##
##1,021 Finnish respondents, 7 comparisons (comp = task, recorded) of two hypothetical candidates
##(profile 1/2, recorded); choice = the source's `choice` (agrees with conjointchoice, the chosen
##profile number); exactly one chosen per task (checked), so forced choice, no opt-out.
##Question wording not available: paraphrased as a choice between the two candidates.
##Seven attributes, level text = the .dta value labels (English; respondents presumably saw
##Finnish, not documented): gender Male/Female; age 27/44/61; education Basic/Intermediate/
##University education; ideology "Close to own political views"/"Far from own political views";
##experience "No previous political experience"/"Experience as local councilor"/"Experience as
##MP"; recommendation (endorsement source) Nobody / "Voting Advice Application" / "Social media
##networks" / "Family or close friend"; likelihood of election ("atrisk") "Very unlikely"/
##Intermediate/"Very likely". Every attribute has a "NO INFO" level (code 1); as in the sibling
##deposit it is stored as "(not shown)". Whether the row was left off or showed a placeholder
##text is NOT documented: if respondents saw a "no information" text, these cells should hold
##that text instead.
##Randomization restrictions, level weights and attribute order: not documented.
##Covariates (.dta labels): cov_political_interest (None at all/A little/Somewhat/Very),
##cov_voted_2019 (Did not vote/Voted), cov_has_party_id (No/Yes: "Party identification"; not
##the party), cov_lr (ideology 0-10 as stored; direction undocumented), cov_education (labels;
##"Don't want to say" -> NA). Dropped: the authors' dichotomies and indices (polint_diko,
##poldisc_diko, inteff3, educ3), the row id.
##N = 1,021 respondents, as in the abstract. No weight in the deposit; no repeated task.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- read_dta(file.path(raw, "endorsement.dta"))
lab <- function(x) { l <- attr(x, "labels"); y <- trimws(names(l)[match(as.numeric(x), l)]); stopifnot(!anyNA(y[!is.na(x)])); y }
s <- as.data.table(zap_labels(r))
stopifnot(nrow(s) == 14294L, uniqueN(s$respid) == 1021L, s[, .N, .(respid, comp)][, all(N == 2)], all(s$profile %in% 1:2),
          all(s$choice == as.integer(s$conjointchoice == s$profile)), s[, sum(choice), .(respid, comp)][, all(V1 == 1)])
d <- s[, .(id = as.integer(respid), task = as.integer(comp), profile = as.integer(profile), choice = as.integer(choice))]
nm <- c(atgender = "gender", atage = "age", ateduc = "education", atideolo = "ideology", atexp = "experience",
        atreco = "recommendation", atrisk = "election_likelihood")
for (v in names(nm)) {
  stopifnot(names(attr(r[[v]], "labels"))[1] == "NO INFO", all(s[[v]] %in% seq_along(attr(r[[v]], "labels"))))
  x <- lab(r[[v]]); x[x == "NO INFO"] <- "(not shown)"
  d[, paste0("attr_", nm[[v]]) := x]
}
ed <- lab(r$education); ed[ed == "Don't want to say"] <- NA
d[, `:=`(cov_political_interest = lab(r$polint), cov_voted_2019 = lab(r$voted), cov_has_party_id = lab(r$partyid),
         cov_lr = as.integer(s$ideology), cov_education = ed)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "christensen_2021_endorsements.csv"))
message("VAA vs Nobody (MM difference): ", round(d[attr_recommendation == "Voting Advice Application", mean(choice)] -
                                                 d[attr_recommendation == "Nobody", mean(choice)], 3))
