##European Parliament candidate conjoint (Finland, May 2019) from
##Christensen, H. S., La Rosa, M. S., & Gronlund, K. (2020). How candidate characteristics
##affect favorability in European Parliament elections: Evidence from a conjoint experiment in
##Finland. European Union Politics, 21(4), 563-583. https://doi.org/10.1177/1465116520929765
##Replication data: OSF node w6jkq ("Conjoint of candidates in 2019 EP elections"),
##doi:10.17605/OSF.IO/W6JKQ, node licence CC BY 4.0, no other terms in the files.
##Files read: "EUP replication data.dta" (OSF j7uy5, saved as data.dta). Level text from the
##article's Table 1 (the article PDF is in the node, OSF rfct8); the .dta value labels give the
##same levels in the same order (abbreviated). "EUP replication Do file.do" (vqcph) read as text.
##Usage: Rscript christensen_2020.R <dir holding data.dta> <output dir>
##
##829 respondents (Qualtrics online panel, quotas on age, gender and region of the Finnish
##electorate; 13-20 May 2019), 7 comparisons (comp = task, recorded) of two hypothetical EP
##candidates (profile 1/2, recorded; left/right position not documented). Question (article):
##pick the candidate "they would be most likely to vote for in the elections" (paraphrase; the
##Finnish wording and the Qualtrics screenshot in the online appendix are not in the deposit).
##choice = `choice`; forced choice, no opt-out (article note 4); exactly one per task (checked).
##Attributes (article Table 1 text; the stem shown with each attribute in the table):
##attr_gender ("The gender of the candidate is...") Male / Female; attr_ideology
##("Ideologically, the candidate is...") Leftist / Center-Leftist / Centrist / Center-Rightist /
##Rightist; attr_issue ("The candidate will mainly work on the following issue...");
##attr_experience ("The previous political experience of the candidate comes from...");
##attr_representation ("The candidate will work to represent the interests of...");
##attr_citizenship ("The citizenship of the candidate is..."); attr_eu_integration ("The
##candidate has the following position on EU integration...").
##Every attribute has a "NOT SHOWN" level (code 1), which respondents "were instructed to
##interpret ... as no information being available"; stored as "(not shown)". Whether the
##attribute row was left off or displayed with a placeholder is not documented (the
##screenshot is in the online appendix only).
##Restrictions: none (article note 5: no combinations excluded). Level weights not documented.
##Respondents saw the survey in Finnish presumably (not stated; display_language unknown);
##labels are the article's English.
##Covariates: cov_eu_interest (eupolint, "Interest in EU": Not at all / Not very / Somewhat /
##Very, .dta labels); cov_ideology_3cat (the authors' collapse of the 0-10 left-right
##self-placement: Left 0-3 / Intermediate / Right; the 0-10 item is not deposited).
##Dropped: the row id, conjointchoice (= the chosen profile number; agrees with choice),
##eupolintdiko (a dichotomy of eupolint), 48 Stata e(sample) markers (_est_*).
##N = 829 matches the article. No weight in the deposit; no repeated task.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "data.dta"))))
stopifnot(nrow(s) == 11606L, uniqueN(s$respid) == 829L, s[, .N, .(respid, comp)][, all(N == 2)],
          s[, .N, respid][, all(N == 14)], all(s$profile %in% 1:2))
ns <- "(not shown)"
lab <- list(att_gender = c(ns, "Male", "Female"),
            att_ideol = c(ns, "Leftist", "Center-Leftist", "Centrist", "Center-Rightist", "Rightist"),
            att_issue = c(ns, "Human rights and democracy", "Climate change and environment", "Immigration",
                          "Security and defense"),
            att_exper = c(ns, "No political experience", "Local politics", "National level politics", "European politics"),
            att_repr = c(ns, "All the people who voted for the candidate", "The candidate's national party",
                         "All people in Finland", "All people in Europe"),
            att_ctznshp = c(ns, "Greek", "Romanian", "German", "Danish", "Finnish"),
            att_integr = c(ns, "Less EU integration", "About the same level of integration", "More EU integration"))
nm <- c(att_gender = "gender", att_ideol = "ideology", att_issue = "issue", att_exper = "experience",
        att_repr = "representation", att_ctznshp = "citizenship", att_integr = "eu_integration")
d <- s[, .(id = as.integer(respid), task = as.integer(comp), profile = as.integer(profile), choice = as.integer(choice))]
stopifnot(all(d$choice == as.integer(s$conjointchoice == s$profile)), d[, sum(choice), .(id, task)][, all(V1 == 1)])
for (v in names(lab)) {
  stopifnot(all(s[[v]] %in% seq_along(lab[[v]])))
  d[, paste0("attr_", nm[[v]]) := lab[[v]][s[[v]]]]
}
stopifnot(all(s$eupolint %in% c(1:4, NA)), all(s$ideology %in% c(0:2, NA)))
d[, cov_eu_interest := c("Not at all", "Not very", "Somewhat", "Very")[s$eupolint]]
d[, cov_ideology_3cat := c("Left", "Intermediate", "Right")[s$ideology + 1L]]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "christensen_2020_ep_candidates.csv"))
