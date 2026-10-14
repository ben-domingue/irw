##US-China air-incident crisis vignettes from
##Dafoe, A., Hatz, S., & Zhang, B. (2021). Coercion and provocation. Journal of Conflict Resolution, 65(2-3), 372-402.
##https://doi.org/10.1177/0022002720957078
##Replication data: Harvard Dataverse doi:10.7910/DVN/0BFI9L, CC0 1.0. Files read: CP_data.RData (object CP),
##dafoe_hatz_zhang_2020_CP.pdf (manuscript; Appendix B is the survey text), replication_code_dataverse.R (text).
##Usage: Rscript dafoe_2021.R <dir holding CP_data.RData> <output dir>
##
##1,761 US MTurk respondents (Feb 2016; the authors' N for all analyses). Each read one crisis scenario about the
##US-China dispute over military operations in the East China Sea, a 2 x 5 between-subject factorial (paper Table 1):
##  military_capability (MilCapT): 1 "Experts agree that the US's military capability is inferior to China's for a
##    conflict in the East China Sea." / 2 "... superior to China's ..." (Appendix B.1.1; 50% each)
##  incident (Incident; 20% each): Attack / Collision / Non-Collision / Accident texts verbatim from Appendix B.1.2;
##    Control = "[No text]", coded "(not shown)" since the design left the incident off the vignette.
##Four respondents (Incident = 1, 2, 4) lack the authors' dummy columns (Attack, Collision, Accident); the
##coded Incident variable, which the authors' code uses (Incident.f), is used here.
##One task of one profile per respondent (id = row order; the Qualtrics ResponseId is dropped). Outcomes (Table 2,
##Appendix B.2), all "how far should the US go to assert its claims in this dispute", higher = more resolve:
##  rating                 LevelEsc, military force, 0-3 (0 "The US should not assert its claims" ... 3 "... using
##                         military force if necessary, even if this risks war")
##  rating_economic_cost   EcCosts, future economic costs, 0-9 (0 not assert ... 9 "no matter the economic cost")
##  rating_military_deaths MilDeaths, future US military fatalities, 0-7 (0 ... 7 "no matter the number")
##  rating_risk_of_war     RiskWar, risk of war with China, 0-6 (0 ... 6 "no matter the risk of war")
##No opt-out. Dropped: the mediator and importance batteries, manipulation/attention checks, survey metadata,
##race, income, state, open-ended text, derived dummies, and LocationLatitude/LocationLongitude (PII FOUND, dropped).
##Covariates (codes from Appendix B.2): cov_gender (1 Male, 2 Female, -98 = NA), cov_age (whole numbers 18-100,
##else NA), cov_education (answer text of codes 1-8, -98 = NA), cov_party_id (PolParty text: Democrat,
##Republican, Independent, "Haven't thought much about this", Other; -98 = NA), cov_ideology_code (Pol7scale codes,
##unlabelled in my reading of the text). No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "CP_data.RData"), envir = e); d <- as.data.table(e$CP)
stopifnot(nrow(d) == 1761)
d[, id := .I]
cap <- c("Experts agree that the US's military capability is inferior to China's for a conflict in the East China Sea.",
         "Experts agree that the US's military capability is superior to China's for a conflict in the East China Sea.")
inc <- c(Attack = "Recently a Chinese military plane shot down an American military plane over the East China Sea. China claims the American plane was trespassing in China's ADIZ. The American pilot died and the plane was destroyed in the crash.",
  Collision = "Recently there was a collision between an American and a Chinese military plane. The collision occurred because the Chinese plane was flying dangerous maneuvers around the American plane, making several close passes. On the third pass, the Chinese plane collided with the American plane. The American pilot died. The Chinese pilot just barely managed to eject and survive. Both planes were destroyed.",
  `Non-Collision` = "Recently an American military plane and a Chinese military plane almost collided with each other. They almost collided because the Chinese plane was flying dangerous maneuvers around the American plane, making several close passes. No one was hurt.",
  Accident = "Recently an American military plane that was conducting routine operations in the East China Sea crashed in a storm. The pilot died and the plane was destroyed.",
  Control = "(not shown)")
f <- as.character(d$Incident.f)
stopifnot(all(f %in% names(inc)), all(d$MilCapT %in% 1:2))
edu <- c("Less than high school", "High school or GED", "Some college", "2-year college degree", "4-year college degree",
         "Masters degree", "Doctoral degree", "Professional degree (e.g., JD or MD)")
pp <- c(`1` = "Haven't thought much about this", `2` = "Democrat", `3` = "Independent", `4` = "Republican", `-88` = "Other")
age <- ifelse(!is.na(d$Age) & d$Age >= 18 & d$Age <= 100 & d$Age == round(d$Age), d$Age, NA)
r <- d[, .(id, task = 1L, profile = 1L, rating = as.integer(LevelEsc), rating_economic_cost = as.integer(EcCosts),
  rating_military_deaths = as.integer(MilDeaths), rating_risk_of_war = as.integer(RiskWar))]
r[, `:=`(attr_military_capability = cap[d$MilCapT], attr_incident = unname(inc[f]),
  cov_gender = c("male", "female")[match(d$Gender, 1:2)], cov_age = as.integer(age),
  cov_education = edu[match(d$Education, 1:8)], cov_party_id = unname(pp[as.character(d$PolParty)]),
  cov_ideology_code = as.integer(ifelse(d$Pol7scale == -98, NA, d$Pol7scale)))]
stopifnot(!anyNA(r[, .(rating, rating_economic_cost, rating_military_deaths, rating_risk_of_war)]))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "dafoe_2021_coercion_provocation.csv"))
