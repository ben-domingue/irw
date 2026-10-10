##Democratic-innovations conjoint (Ghana) from
##Kramon, E. (2025). Are democratic innovations legitimate to the broader public? Evidence from
##survey experiments in Ghana. British Journal of Political Science.
##https://doi.org/10.1017/S000712342510094X
##Replication data: Harvard Dataverse doi:10.7910/DVN/JDUUGI, CC0 1.0, no restricted files.
##Files read: conjoint1_rep.rds (one row per respondent x round x profile) and dat_rep.rds
##(respondent file, for the age band). Codes are labelled from Kramon-BJPS-replication.R (read as
##text, not run): plot labels and reference levels. Design and wording from the article (web text).
##Usage: Rscript kramon_2025.R <raw dir> <output dir>
##
##Ipsos-Ghana face-to-face, nationally representative, July-September 2023, 1,043 adults; the
##questionnaire was translated into Dagbani, Ewe, Ga and Twi. Scenario: "The district government
##has received funding for a project to build and improve public goods in the district ... will
##not have enough money to provide the project to every community". 2 tasks (task = source
##`round`) of two processes (profile = source `order`, 1 = process A, 2 = process B), 3 attributes
##in fixed order. Levels are the AUTHORS' SHORT LABELS (the displayed wording is in the article's
##Table 2, an image not read, and was shown in translation):
##  attr_process: 1 Status quo, 2 Citizen-elite deliberation, 3 Participatory, 4 Deliberative
##    mini-public (replication code labs and terms pr22-pr24 vs reference "Status Quo");
##  attr_endorsement: 1 No endorsement, 2 NPP endorsement, 3 NDC endorsement (explicit
##    case_match in the balance-test code: 1 ~ "No Endorsement", 2 ~ "NPP Endorsement", 3 ~ "NDC
##    Endorsement"; same order in the regression table's custom.coef.names);
##  attr_project: 1 Community receives the project, 2 Community does not receive the project
##    (out2 relevelled to "2" = "No Project"; term out21 = "Project").
##Outcomes (article wording):
##  choice: "Which of these processes would you prefer?" forced choice, one per task.
##  rating_fair: "Thinking of process A [B], how fair would you say it is?" 1-7, stored as the
##    code of the deposit's ordered factor: Extremly unfair (sic), Not at all fair, Neutral,
##    Somewhat fair, Fair, Very fair, Extremly fair (7 = most fair).
##  rating_democratic: "Thinking of process A [B], how democratic would you say it is?" 1-7:
##    Extremly not democratic, Not at all democratic, Neutral, Somewhat democratic, Democratic,
##    Very democratic, Extremly democratic.
##Randomization: the article says levels were randomized independently for each profile; the
##  level shares are clearly unequal (status quo 35%, citizen-elite 18%, participatory 19%,
##  mini-public 28%; no endorsement 43%, NPP 24%, NDC 33%), undocumented.
##Not built: conjoint2_rep.rds (Experiment 2) varies one attribute only (reform type, 4 levels):
##  a single-factor comparison, not a conjoint.
##Covariates: cov_gender from `female` (authors' 0/1: 1 = female, 0 = male); cov_age_group from
##  dat_rep age1 band text ("Refuse" -> NA); cov_rural (authors' 0/1); cov_npp_partisan,
##  cov_ndc_partisan (authors' 0/1, NA for non-partisans as deposited). The authors' rescaled 0-1
##  age and education scores are dropped (derived; raw codes not deposited). No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "conjoint1_rep.rds")))
r <- as.data.table(readRDS(file.path(raw, "dat_rep.rds")))
stopifnot(nrow(x) == 4172, all(levels(x$fair) == c("Extremly unfair", "Not at all fair", "Neutral", "Somewhat fair", "Fair", "Very fair", "Extremly fair")),
          all(levels(x$democratic) == c("Extremly not democratic", "Not at all democratic", "Neutral", "Somewhat democratic", "Democratic", "Very democratic", "Extremly democratic")))
d <- x[, .(id = ID, task = as.integer(round), profile = as.integer(order), choice = as.integer(choice),
           rating_fair = as.integer(fair), rating_democratic = as.integer(democratic),
           attr_process = c("Status quo", "Citizen-elite deliberation", "Participatory", "Deliberative mini-public")[as.integer(as.character(process))],
           attr_endorsement = c("No endorsement", "NPP endorsement", "NDC endorsement")[as.integer(as.character(endorse))],
           attr_project = c("Community receives the project", "Community does not receive the project")[as.integer(as.character(outcome))],
           cov_gender = c("male", "female")[female + 1], cov_rural = as.integer(rural),
           cov_npp_partisan = as.integer(npp_partisan), cov_ndc_partisan = as.integer(ndc_partisan))]
ag <- r[, .(id = ID, cov_age_group = fifelse(as.character(age1) == "Refuse", NA_character_, as.character(age1)))]
d <- merge(d, ag, by = "id")
stopifnot(!anyNA(d[, .(attr_process, attr_endorsement, attr_project, choice, cov_gender)]),
          d[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)], uniqueN(d$id) == 1043)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kramon_2025_democratic_innovations.csv"))
