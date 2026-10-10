##Medicare-for-all program conjoint (US) from
##Qi, H. (2025). Understanding public attitudes toward redistribution: Analysis by ideological
##subgroups. Public Opinion Quarterly. https://doi.org/10.1093/poq/nfaf046
##Replication data: Harvard Dataverse doi:10.7910/DVN/ABP4XA, CC0 1.0. File read:
##conjoint_data.dta (Dataverse "original format" download; value and variable labels).
##conjoint_analysis.do and conjoint_analysis.log were read as text. The article and its
##supplement are paywalled and were not read.
##Usage: Rscript qi_2025.R <dir holding conjoint_data.dta> <output dir>
##
##1,638 US online respondents (Qualtrics export, all finished, fielded 11 Aug 2023; the panel
##is not named in the deposit), 9 pairs of hypothetical government health-insurance programs,
##4 attributes. The file has one row per respondent x profile with `expand` (1-18, "Profile
##identifier") and no task column. Rows with expand 2k-1 and 2k form a pair: in every such pair
##exactly one program is chosen (program_choice), so task = ceiling(expand/2) and profile =
##2 - expand mod 2 are INFERRED; whether expand follows the display order is not documented.
##Attribute text. The level text is the .dta VALUE label of each cat_a_* variable (the author's
##short labels): transition (Immediately replaced / Phased out over five years / Competed with
##each other), distributive result ("Lower income benefit" ... "Higher income benefit"), tax
##burden ("Higher inc pay more" ... "Lower inc pay more"), cost ("$2 trillion" ... "$6
##trillion"). The author's dummy variables carry longer sentences as variable labels, probably
##closer to the screen text ("All private health insurance immediately replaced by Medicare",
##"Lower-income citizens benefit most from this program", "The government collects a higher
##percentage of total earnings from higher-income ..." truncated at 80 characters by Stata).
##CAUTION, cost: the do-file's figure labels give "$2.4/$3.2/$4.3/$6.2 trillion" (total cost
##per year) for codes 1-4 while the value labels say $2/$3/$4/$6 trillion; which amounts were
##displayed cannot be settled from the deposit. The value labels are stored.
##Outcome: choice = program_choice (forced choice between the two programs; "Chose this
##program" = 1; the do-file calls it "forced choice"). Question wording not deposited. No
##opt-out. Randomization restrictions, level weights and attribute order are not documented.
##The author's main analyses keep respondents passing 2-4 of 4 screeners (screener_2plus).
##Covariates: cov_gender (gender Female/Male), cov_age (years; 8 implausible free-typed values
##(10, 11, 16, 1987, 1999, 2004, 30701, 98073) -> NA), cov_age_group (age_ordinal value label), cov_education (educ answer text), cov_race, cov_income (faminc answer text),
##cov_employment, cov_ideology (ideo text), cov_party_id (party: Democrat/Republican/
##Independent/Other/No preference, answer text), cov_party_id7 (pid_7 value label, "Strong
##Democrat" .. "Strong Republican"), cov_political_attention (attention, answer text),
##cov_attention_pass_1..4 (author's pass flags: 1 most-important-problem screener,
##2 newspaper screener, 3 WWI/WWII screener, 4 'neither' screener), cov_screener_count (0-4),
##cov_duration_sec (whole survey). Blank answers -> NA.
##Dropped: ipaddress (PII), responseid and the id value labels (Qualtrics ids; id is the
##author's integer key, kept), dates, raw screener items, the author's dummies and derived
##groupings (ideo3, libcon, pid_3, demrep, income3, white, female, pro_/reg_ flags).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_dta(file.path(raw, "conjoint_data.dta"))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
bl <- function(v) { v <- trimws(as.character(v)); v[v == ""] <- NA; v }
d <- data.table(id = as.integer(zap_labels(x$id)), expand = as.integer(x$expand), choice = as.integer(zap_labels(x$program_choice)),
                attr_transition = lab(x$cat_a_trans), attr_distribution = lab(x$cat_a_distri),
                attr_tax_burden = lab(x$cat_a_tax), attr_cost = lab(x$cat_a_cost),
                cov_gender = c(Female = "female", Male = "male")[bl(x$gender)], cov_age = fifelse(x$age >= 18 & x$age <= 99, as.integer(x$age), NA_integer_),
                cov_age_group = lab(x$age_ordinal), cov_education = bl(x$educ), cov_race = bl(x$race),
                cov_income = bl(x$faminc), cov_employment = bl(x$employ), cov_ideology = bl(x$ideo),
                cov_party_id = bl(x$party), cov_party_id7 = lab(x$pid_7), cov_political_attention = bl(x$attention),
                cov_attention_pass_1 = as.integer(x$mipscreener_pass), cov_attention_pass_2 = as.integer(x$newspaperscreener_pass),
                cov_attention_pass_3 = as.integer(x$wwiscreener_pass), cov_attention_pass_4 = as.integer(x$neitherscreener_pass),
                cov_screener_count = as.integer(x$screener_count), cov_duration_sec = as.integer(x$durationinseconds))
stopifnot(uniqueN(d$id) == 1638, d[, .N, id][, all(N == 18)], d[, uniqueN(expand), id][, all(V1 == 18)],
          !anyNA(d[, .(choice, attr_transition, attr_distribution, attr_tax_burden, attr_cost)]))
d[, task := (expand + 1L) %/% 2L][, profile := 2L - expand %% 2L][, expand := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "qi_2025_health_redistribution.csv"))
