##Disabled-candidate conjoint (US and UK) from
##Reher, S. (2025). Voting for disabled candidates. The Journal of Politics, 87(2), 790-794.
##https://doi.org/10.1086/732994
##Replication data: Harvard Dataverse doi:10.7910/DVN/8TEZ2R, CC0 1.0, no restricted files.
##File read: data.csv. Codebook.pdf (deposit) gives the variable coding; the displayed text
##(vignette template, Figure S1, and level wording, Table S1) is from the article's SI in the
##accepted manuscript (strathprints.strath.ac.uk/90150).
##Usage: Rscript reher_2025.R <dir holding data.csv> <output dir>
##
##Online quota samples, US (3,013 ids in the deposit) and UK (2,998), May-June 2020 / Jan 2021.
##Each respondent saw two pairs of fictional House/Commons candidates as short vignettes
##("<NAME> is <AGE> years old and has <CHILDREN>. <PRONOUN> <JOB>. <PRONOUN><DISABILITY>. ...").
##One pair carried no party, the other gave each candidate a party (always one left, one right
##party); which came first was randomized. Source `candidate` 1-2 = first comparison (A, B),
##3-4 = second, so task = display order (recorded) and profile = A/B (recorded);
##trial_party_shown says which experiment the task was. The author pooled the two countries
##(country fixed effect), so ONE table with cov_country; level wording differs by country
##where the instrument did (teacher, disability, office, party).
##Outcomes (same pairs):
##  choice = vote.n, "Which candidate would you be more likely to vote for?" (A or B), forced,
##     no opt-out. 2,632 tasks have no vote answer (missing; left blank).
##  rating_ideology = lr.s x 10: "Where would you place the candidates on the following scale
##     from left to right?" 0 = Left .. 10 = Right (direction is not favourability).
##  rating_represent = represent.n, "Candidate A/B represents people who are under-represented in
##     politics." 0 = strongly disagree .. 4 = strongly agree.
##Rows whose three outcomes are all missing are omitted (42 respondents have none at all; 62
##tasks keep one profile only). 5,969 respondents remain, 5,275 of them with a vote answer.
##Attributes (text from SI Table S1): attr_disability ("(no disability sentence)" when no
##disability was mentioned, p = 0.4), attr_age (35-65), attr_children, attr_job, attr_experience
##(years, 4-17), attr_office, attr_party (blank in the no-party task). Gender and minority
##ethnic background were carried only by the candidate's NAME (e.g. "Paul Smith"/"Anna Smith"/
##"Sofia Garcia"); the names are NOT in the deposit, so attr_gender (Female/Male) and
##attr_name_minority ("Minority ethnic name"/"Non-minority name") are the codebook's codings of
##the name shown, not displayed text. Restrictions (SI Table S1): non-uniform weights
##(disability none 0.4 vs 0.2 each type; minority names 0.3 vs 0.7); one party per side.
##Covariates: cov_country; cov_lr_self (lrown.s x 10, 0 = Left .. 10 = Right); cov_lr_group
##(the author's left/centre/right split of it); cov_age_group 1=18-24 .. 6=65+; cov_gender
##(Male/Female/Other); cov_education age left full-time education 0=15 or under 1=16 2=17-18
##3=19 4=20+ or still in education; cov_employment (author's 4 groups); cov_disabled 0/1.
##Dropped: row index columns, Disability / c.disdummy (derived), c.party3 (derived), c.party
##(-> attr_party). No survey weight in the deposit.
##N: 6,011 ids in the deposit vs "N=3,000" per country in the article; 5,969 kept (above).
##Spot check: Table S2 model 1 (no-party tasks, both countries, linear) disabled = 0.025
##reproduces exactly from this table.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.csv"))
stopifnot(s[, .N, ID][, all(N == 4)], all(s$candidate %in% 1:4))
us <- s$country == "US"
d <- data.table(id = as.integer(s$ID), task = (s$candidate + 1L) %/% 2L, profile = 2L - s$candidate %% 2L,
                choice = as.integer(s$vote.n), rating_ideology = as.integer(round(s$lr.s * 10)),
                rating_represent = as.integer(s$represent.n))
stopifnot(all(abs(s$lr.s * 10 - round(s$lr.s * 10)) < 1e-9, na.rm = TRUE))
dis <- list(None = c("(no disability sentence)", "(no disability sentence)"),
            Paralysed = c("is paralyzed below the waist and uses a wheelchair to get around.",
                          "is paralysed below the waist and uses a wheelchair to get around."),
            Blind = rep("is blind and reads using text-to-speech software.", 2),
            Deaf = c("is deaf and communicates mostly in American Sign Language.",
                     "is deaf and communicates mostly in British Sign Language."))
stopifnot(all(s$c.dis %in% names(dis)))
k <- ifelse(us, 1L, 2L)
job <- c(Doctor = "works as a doctor in a local hospital", `Factory worker` = "works in a local factory",
         Lawyer = "works as a lawyer for a large international firm",
         `Small business owner` = "owns a small business which employs five people")
stopifnot(all(s$c.job %in% c(names(job), "Teacher")))
d[, `:=`(attr_disability = mapply(function(x, i) dis[[x]][i], s$c.dis, k, USE.NAMES = FALSE),
         attr_gender = ifelse(s$c.female == 1, "Female", "Male"),
         attr_name_minority = ifelse(s$c.minority == 1, "Minority ethnic name", "Non-minority name"),
         attr_age = as.character(s$c.age),
         attr_children = c("no children", "one child", "two children", "three children")[s$c.child.num + 1L],
         attr_job = ifelse(s$c.job == "Teacher", ifelse(us, "works as an elementary school teacher", "works as a primary school teacher"),
                           job[s$c.job]),
         attr_experience = as.character(s$c.exp),
         attr_office = ifelse(s$c.heldoffice == 1, ifelse(us, "has previously served as a state legislator",
                                                          "has previously served as a local councillor"),
                              "has not yet held elected office"),
         attr_party = s$c.party)]
stopifnot(!anyNA(d$attr_children), !anyNA(d$attr_job), s[, all(c.female %in% 0:1 & c.minority %in% 0:1 & c.heldoffice %in% 0:1)])
d[, trial_party_shown := ifelse(is.na(s$c.party), "no", "yes")]
stopifnot(d[, uniqueN(trial_party_shown), .(id, task)][, all(V1 == 1)], d[, uniqueN(trial_party_shown), id][, all(V1 == 2)])
d[, `:=`(cov_country = s$country, cov_lr_self = as.integer(round(s$lrown.s * 10)), cov_lr_group = s$lrcat,
         cov_age_group = as.integer(s$age.n), cov_gender = s$gender, cov_education = as.integer(s$edu),
         cov_employment = s$emp1, cov_disabled = as.integer(s$disown))]
stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)])
d <- d[!(is.na(choice) & is.na(rating_ideology) & is.na(rating_represent))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "reher_2025_disabled_candidates.csv"))
