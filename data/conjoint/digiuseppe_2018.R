##Trade-agreement conjoint (US, MTurk) from
##DiGiuseppe, M., & Kleinberg, K. B. (2018). Economics, security, and individual-level
##preferences for trade agreements. International Interactions, 45(2), 289-315.
##https://doi.org/10.1080/03050629.2019.1551007
##Replication data: Harvard Dataverse doi:10.7910/DVN/0HST44, CC0 1.0, no restricted files.
##File read: DK18_rep.dta (Dataverse "original format" download of DK18_rep.tab; Stata value
##labels used). DK18_repcode.do read as text. Level text and design facts are from the
##article's Table 1 and design section (author accepted manuscript, Leiden University open
##access repository, hdl 1887/72366); the instrument appendix (Supplemental Appendix A) was not
##available.
##Usage: Rscript digiuseppe_2018.R <dir holding DK18_rep.dta> <output dir>
##
##US MTurk workers, July 15-19, 2016. Each saw 5 pairs of hypothetical trade agreements
##(task, profile recorded in the file) and indicated which agreement they preferred.
##  choice: binary, forced choice, no opt-out (exactly one profile chosen in every task).
##    Wording: the article says only that respondents were asked "to indicate which trade
##    agreement they preferred" (paraphrase; full instructions in the unavailable appendix).
##Three randomly assigned arms, ONE TABLE (one fielding, same economic attributes; the authors
##compare arms): trial_arm = control (Group 1: economic attributes only), global_influence
##(Group 2: adds "Global influence effect"), political_relations (Group 3: adds "Other
##country's relationship to the United States"). attr_global_influence / attr_relationship
##are blank where that attribute was not shown.
##Attributes (Stata value labels; text as in article Table 1): jobs ("Effect on US jobs"),
##us_growth, partner_growth, regime_economy ("Other country's political system and economy",
##one attribute with 6 combined levels), global_influence (geopolB labels Increases /
##Diminishes / Maintains -> "Increases US global political influence" etc., Table 1 text),
##relationship (partner codes -> Table 1 text: "US military ally", "US military rival",
##"Neither a US military ally or rival", "Not a US military ally but has hostile relations with
##our adversaries", "Not a US military rival but has cooperative relations with our
##adversaries"; the authors' dummies agree 1:1). Attribute order was randomized across
##respondents (article) but is not recorded. No restrictions are documented; levels look
##uniform.
##Respondent 580 (anonymous id) has no regime value on any of his 10 profiles (its regime
##dummies are all 0, which would mean "Wealthy and undemocratic" ten times): dropped. One
##empty row dropped. 2,513 respondents in the file -> 2,512 here, matching the article's 2,512.
##Covariates: cov_age (years), cov_race (value-label text), cov_male, cov_attention_check1/2
##(1 = pass). Dropped: Qualtrics responseid (re-keyed: id = the deposit's anonymous id
##anymid), task timings, the authors' derived dummies and composites (pdem.., ally.., geopolC,
##partnerB, liberal, democrat, protrade, Hawk, LowIncome, PassCheck, ...). No survey weight.
##Spot check: in the control arm, OLS of choice on the four economic attributes (baseline "No
##impact on jobs" / "No effect on the US economy") gives Creates many jobs 0.19, Creates some
##jobs 0.11, Costs some jobs -0.17, Costs many jobs -0.31, Significantly grows 0.26, Somewhat
##grows 0.17 = article Table 2 "Control group AMCE".
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "DK18_rep.dta"))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
s <- data.table(id = as.integer(k$anymid), task = as.integer(k$task), profile = as.integer(k$profile), choice = as.integer(k$binary),
                group = as.integer(k$Group), jobs = lab(k$jobs), us = lab(k$USgrowth), tp = lab(k$TPgrowth), regime = lab(k$regime),
                geo = lab(k$geopolB), partner = as.integer(zap_labels(k$partner)),
                ally = k$ally, rival = k$rival, neither = k$noallyrival, ourside = k$ourside, rivalside = k$rivalside,
                age = as.integer(k$age), race = lab(k$race), male = as.integer(k$male), at1 = as.integer(k$attck1), at2 = as.integer(k$attck2))
s <- s[!is.na(task)]
stopifnot(s[is.na(regime), all(id == 580)], s[id == 580, all(is.na(regime))])
s <- s[id != 580]
stopifnot(s[, .N, id][, all(N == 10)], uniqueN(s$id) == 2512, !anyNA(s[, .(jobs, us, tp, regime)]))
rel <- c("US military ally", "US military rival", "Neither a US military ally or rival",
         "Not a US military ally but has hostile relations with our adversaries",
         "Not a US military rival but has cooperative relations with our adversaries")
stopifnot(s[group == 3, all((partner == 0) == (ally == 1) & (partner == 1) == (rival == 1) & (partner == 2) == (neither == 1) &
                            (partner == 3) == (ourside == 1) & (partner == 4) == (rivalside == 1))],
          s[group != 3, all(is.na(partner))], s[group == 2, all(geo %in% c("Increases", "Diminishes", "Maintains"))], s[group != 2, all(geo == "Not asked")])
d <- s[, .(id, task, profile, choice, attr_jobs = jobs, attr_us_growth = us, attr_partner_growth = tp, attr_regime_economy = regime,
           attr_global_influence = fifelse(group == 2, paste(geo, "US global political influence"), NA_character_),
           attr_relationship = fifelse(group == 3, rel[partner + 1L], NA_character_),
           trial_arm = c("control", "global_influence", "political_relations")[group],
           cov_age = age, cov_race = race, cov_male = male, cov_attention_check1 = at1, cov_attention_check2 = at2)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(trial_arm), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "digiuseppe_2018_trade_agreements.csv"))
