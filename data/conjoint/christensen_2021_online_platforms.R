##Online participatory platform conjoint (Finland) from
##Christensen, H. S. (2021). A conjoint experiment of how design features affect evaluations
##of participatory platforms. Government Information Quarterly, 38(1), 101538.
##https://doi.org/10.1016/j.giq.2020.101538 (open preprint: SocArXiv 10.31219/osf.io/4ubwh).
##Replication data: OSF project fm9xp ("Conjoint participatory platforms", H. S. Christensen),
##CC BY 4.0 (node licence). File read: "Participatory platforms Replication file.dta"
##(renamed pp.dta on download). No codebook ships; wording from the preprint.
##Usage: Rscript christensen_2021_online_platforms.R <dir holding pp.dta> <output dir>
##
##1,048 Finnish adults (Qualtrics online panel representative on age, gender and region,
##13 Nov - 11 Dec 2019), six comparisons of two hypothetical participatory platforms, seven
##attributes. 12,576 rows = 1,048 x 6 x 2, as in the preprint (p. 6). task = `comp` (1-6,
##recorded), profile = `profile` (1/2, recorded; the Qualtrics screenshot, preprint Fig. 1,
##shows "Verkkoalusta 1" left and "Verkkoalusta 2" right). Exactly one chosen per task.
##Outcomes (one table, same tasks):
##  choice: "(1/6) Valitse alla olevista vaihtoehdoista alusta, jonka haluaisit
##    toteutettavan:" (screenshot) = choose the platform you would like to see introduced.
##    Forced choice, no opt-out.
##  rating_participate: follow-up asked after each choice, only about the SELECTED platform,
##    whether the respondent would also participate on it (preprint p. 12, paraphrase;
##    exact wording not deposited). 1 = yes, 0 = no, as stored. The source codes the
##    unchosen profile 0; here it is NA on the unchosen profile (never asked), so a
##    0 means "would not participate" only.
##Attribute text. Respondents saw Finnish (screenshot). The .dta value labels are the
##author's short English labels; their code order matches the preprint's Table 1, whose
##fuller English wording is stored here (label_language en). Screenshot order of rows:
##verification, anonymity, discussions, interaction, information, role, accessibility;
##whether this order was fixed is not stated. Randomization restrictions not documented;
##level shares are near-equal and every level combination occurs.
##Covariates: cov_internet_time (intnettime, value-label text: "On an average day, how
##much time do you spend using the Internet?"), cov_age_group (agegen; value labels give
##generation names, the bands are the preprint's p. 7: Generation Z 18-24, Millennials
##25-39, Generation X 40-54, Boomers 55-75). Dropped: the author's website-use index
##(websiteuse, derived from 6 items) and the 3-category recodes; source pair id `id`.
##No survey weight in the deposit. No PII.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "pp.dta")))
lab <- function(v, txt) { x <- as.integer(zap_labels(s[[v]])); stopifnot(all(x %in% seq_along(txt))); txt[x] }
stopifnot(nrow(s) == 12576, uniqueN(s$respid) == 1048)
d <- s[, .(id = as.integer(respid), task = as.integer(comp), profile = as.integer(profile),
           choice = as.integer(choice), part = as.integer(participate))]
d[, attr_discussions := lab("att_discus", c("No discussions", "Unmoderated discussions between participants",
                                             "Discussions between participants supervised by a neutral moderator"))]
d[, attr_interaction := lab("att_interac", c("No interaction",
    "Submit questions to experts and politicians that are answered after a few days",
    "Chat questions to experts and politicians that are answered immediately",
    "Ask questions to experts and politicians in occasional live meetings with webcams"))]
d[, attr_information := lab("att_info", c("No information is available",
    "Access to all official documents in connection to decisions",
    "Short overview of important issues in connection to decisions"))]
d[, attr_role := lab("att_aim", c("Undefined", "Come up with new suggestions and ideas",
                                   "Discuss existing suggestions and ideas", "Decide on final policies"))]
d[, attr_verification := lab("att_veri", c("No verification", "Weak verification by sending email link",
                                            "Strong verification with bank codes or personal id"))]
d[, attr_anonymity := lab("att_anon", c("Not possible", "Possible"))]
d[, attr_accessibility := lab("att_access", c("Via Internet browser on computer",
                                               "In an application for phones and tablets"))]
d[, cov_internet_time := lab("intnettime", c("Less than 30m", "30-60m", "1-2 hours", "2-3 hours", "More than 3 hours"))]
d[, cov_age_group := lab("agegen", c("18-24", "25-39", "40-54", "55-75"))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)],
          d[choice == 0, all(part == 0)], d[, uniqueN(cov_age_group), id][, all(V1 == 1)])
d[, rating_participate := fifelse(choice == 1L, part, NA_integer_)][, part := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating_participate"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "christensen_2021_online_platforms.csv"))
