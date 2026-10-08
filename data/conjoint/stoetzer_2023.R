##COVID-19 intensive-care triage conjoint (patient pairs) from
##Stoetzer, L. F., Munzert, S., Lowe, W., Cali, B., Gohdes, A. R., Helbling, M., Maxwell, R., &
##Traunmueller, R. (2023). Affective partisan polarization and moral dilemmas during the COVID-19
##pandemic. Political Science Research and Methods, 11(2), 429-436.
##https://doi.org/10.1017/psrm.2022.13
##Replication data: Harvard Dataverse doi:10.7910/DVN/SURAOE, CC0 1.0. File read: dat_cnj.RDS
##(long conjoint file). Read as text: README.text, 03_analyse-cnj.R, 02_descriptives.R; dat_wide.RDS
##inspected only for the interview language per country (Q_Language; it has no key to dat_cnj).
##Design facts from the OSF preprint (doi:10.31219/osf.io/r32fa), pp. 4-6.
##Usage: Rscript stoetzer_2023.R <raw dir> <output dir>
##
##6,415 respondents from a commercial access panel (Respondi) with age/gender/education quotas,
##August 2020: USA 1,078, Germany 2,044, Italy 1,103, Poland 1,097, Brazil 1,093. One table with
##cov_country: the authors pool the five countries ("Countries combined") and the attribute set is
##shared; only the party named in the partisanship attribute differs by country (US Republican/
##Democrat, Germany AfD/Greens, Italy Lega/Italia Viva, Poland PiS/PO, Brazil PSL/PT). dat_cnj.RDS
##stacks every row twice (once under its country, once under "Countries combined"); only the
##country rows are kept. Interview language (dat_wide Q_Language): EN, DE, IT, PL, PT-BR.
##Task: respondents imagine COVID-19 overwhelms intensive care and choose which of two patients to
##prioritize (choice = y; preprint p.5: "asks them which of the two they would prioritize"; exact
##wording not deposited), 4 pairs (task = time, profile = cand a/b, both recorded). Forced choice:
##2,053 of 25,660 pairs have no answer (y NA on both) and are omitted.
##Attributes (level text = the deposit's English labels, not the translated screen text): age
##(27/42/61/76; the preprint says 21, the data say 27), gender, children, job, arrival at the
##hospital, survival chance, partisanship (authors' labels "Left PID (Democrat)", "Right PID
##(AfD)", "No PID"). Restriction: arrival is randomized for patient A only and patient B's level
##follows (First <-> Second, Same time <-> Same time; preprint fn 5, verified in the data).
##Attribute order randomized per respondent, constant across tasks, not recorded.
##Covariates: cov_resp_pid (respondent's party ID, authors' coding), cov_age_resp, cov_male,
##cov_children_household, cov_cjattcheck (passed the survival-rate manipulation check; NA for 289
##respondents). Dropped: `weight` (constant within country: a country-size weight for the pooled
##estimate, not a survey weight), partisanship1/2 and resp_pid1/2 (dummies), affective_pol and
##resp_pview1/2 (derived/ambiguous: their variable labels name the German CDU/CSU for every
##country), and ResponseId (re-keyed; it was already a country_n index).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "dat_cnj.RDS")))
x <- x[Cntry != "Countries combined" & !is.na(y)]
d <- data.table(rid = x$ResponseId, task = as.integer(x$time), profile = match(x$cand, c("a", "b")),
                choice = as.integer(x$y), attr_age = x$age, attr_gender = x$gender, attr_children = x$child,
                attr_job = x$job, attr_arrival = x$arrival, attr_survival_chance = x$chance,
                attr_partisanship = as.character(x$partisanship),
                cov_country = x$Cntry, cov_resp_pid = x$resp_pid, cov_age_resp = as.integer(x$age_resp),
                cov_male = as.integer(x$male), cov_children_household = as.integer(x$children_household),
                cov_cjattcheck = as.integer(x$cjattcheck))
stopifnot(d[, .(s = sum(choice), n = .N), .(rid, task)][, all(s == 1 & n == 2)])
ctry <- c(USA = 1, Germany = 2, Italy = 3, Poland = 4, Brazil = 5)
d[, k1 := ctry[cov_country]][, k2 := as.integer(sub(".*_", "", rid))]
setorder(d, k1, k2, task, profile)
d[, id := rleid(rid)][, c("rid", "k1", "k2") := NULL]
setcolorder(d, c("id", "task", "profile"))
fwrite(d, file.path(out, "stoetzer_2023_covid_triage.csv"))
