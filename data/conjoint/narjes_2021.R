##Native bee conservation policy choice experiments in Thailand, from
##Narjes, M. E., & Lippert, C. (2021). Regional differences in farmers' preferences for a native bee
##conservation policy: The case of farming communities in Northern and Eastern Thailand. PLOS ONE, 16(5),
##e0251206. https://doi.org/10.1371/journal.pone.0251206
##Deposit: Mendeley Data doi:10.17632/tyjry2n2hb (version 1, "DCE dataset_PONE-D-20-27763"), CC BY 4.0. File
##read: DCE dataset_PONE-D-20-27763.csv (the deposit has no codebook; variable meanings and level wording are
##from the article's Table 1 and Sections 2.2-2.3, read as text).
##Usage: Rscript narjes_2021.R <dir holding the csv> <output dir>
##
##Sample: 325 farmers in 2013: 198 longan farmers in Chiang Mai province (Northern Thailand) and 127 rambutan
##farmers in Chanthaburi province (Eastern Thailand). The paper reports two discrete choice experiments with
##the same attributes and design and analyses them together and side by side with a region contrast (variable
##CHB "Farmer in Chanthaburi" in its Table 1); the deposit pools them with a Chiang Mai indicator, so one table
##with cov_region (the attribute text is shared).
##12 choice sets x 3 alternatives ("Policy A", "Policy B" and a fixed status quo "no conservation strategy").
##Outcome: choice = the preferred alternative of the three; no opt-out in the sense of the standard: the status quo
##is displayed with its own levels (no pest-control, no habitat improvement, no husbandry, native bees -50%,
##cost 0 THB; article Table 1 note a), so it is a profile (profile 3, attr_alternative = Status quo).
##Exactly one alternative chosen per set (checked).
##Attributes (Table 1): bee-friendly pest control (no/yes), improving native bee habitat (no/yes), native bee
##husbandry (no/yes), change in the native bee population (-50%, 0%, +50%), policy implementation cost, a
##one-time fee paid to local authorities (THB 0, 250, 500, 750). The article gives the attributes, not the exact
##on-screen wording of each level, so the level text is a paraphrase of Table 1 ("No"/"Yes", "-50%", "THB 250").
##Language of the survey (Thai presumably) is not stated in the deposit or article.
##Profile order Policy A = 1, Policy B = 2, status quo = 3 follows the data's Alt labels (screen position not
##documented: profile_source inferred). Task = the deposit's `set` (1-12; whether it is display order is not
##documented).
##Covariates (variable names from Table 1): MALE (gender), age, number of children, education, occupation and
##ethnic group (codes without labels: kept as _code), BEEKEEPER (beekp), BEE_FARM (keeps bees on farm), ECON_BEE
##(engages in beekeeping, honey hunting or bee-rental), POS_BEE (rated native bees' effect on yields good or
##excellent), POLL_DEC (believes to have experienced a native-bee pollination shortage), region. Dropped: the
##many income and farm-economics columns (units and periods undocumented), the authors' dummies wb_dec/wb_inc
##(derived from the population change), Q-ID survey codes. No survey weight. ID is a plain survey number,
##re-keyed to 1..325.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "csv$", full.names = TRUE); stopifnot(length(f) == 1)
d <- fread(f); setnames(d, make.names(trimws(names(d))))
stopifnot(nrow(d) == 325 * 12 * 3, d[, uniqueN(ID)] == 325, d[, .N, .(ID, set)][, all(N == 3)],
          d[, sum(Choice), .(ID, set)][, all(V1 == 1)], all(d$Alt %in% c("PA", "PB", "NP")))
d[, id := as.integer(factor(ID, levels = sort(unique(ID))))]
yn <- function(x) ifelse(x == 1, "Yes", "No")
o <- d[, .(id, task = as.integer(set), profile = c(PA = 1L, PB = 2L, NP = 3L)[Alt], choice = as.integer(Choice),
           attr_alternative = c(PA = "Policy A", PB = "Policy B", NP = "Status quo")[Alt],
           attr_bee_friendly_pest_control = yn(pest), attr_native_bee_habitat_improvement = yn(hab),
           attr_native_bee_husbandry = yn(bkeep),
           attr_native_bee_population_change = ifelse(wbee > 0, sprintf("+%d%%", wbee), sprintf("%d%%", wbee)),
           attr_implementation_cost = sprintf("THB %d", costs),
           cov_region = ifelse(Chiang.Mai..yes.1. == 1, "Chiang Mai (longan)", "Chanthaburi (rambutan)"),
           cov_gender = ifelse(male == 1, "male", "female"), cov_age = as.integer(age), cov_children = as.integer(children),
           cov_education_code = as.integer(edu), cov_occupation_code = as.integer(occup), cov_ethnic_group_code = as.integer(ethnic),
           cov_beekeeper = as.integer(beekp), cov_keeps_bees_on_farm = as.integer(bee_farm), cov_econ_bee_activity = as.integer(econ_bee),
           cov_rates_native_bees_good = as.integer(pos_nativebee), cov_pollination_shortage_experienced = as.integer(X26.dec_bee))]
stopifnot(!anyNA(o$attr_implementation_cost), o[profile == 3, uniqueN(paste(attr_bee_friendly_pest_control, attr_native_bee_population_change, attr_implementation_cost))] == 1)
setorder(o, id, task, profile)
fwrite(o, file.path(out, "narjes_2021_native_bee_policy.csv"))
